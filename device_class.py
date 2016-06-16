from __future__ import division
import json
import namespace as util
import time
from minimalmodbus import *


"""
.. moduleauthors:: Damiano Di Stefano <damiano.di.stefano@gmail.com>, Marco Giuseppe Salafia <marco.salafia@gmail.com>
4noks_device: A simple daemon written in python for polling 4noks devices based on Modbus protocol. It's necessary
                downloading minimalmodbus.
"""

__authors__   = ['Damiano Di Stefano', 'Marco Giuseppe Salafia']
__email__    = ['damiano.di.stefano@gmail.com', 'marco.salafia@gmail.com']
__url__      = 'https://github.com/Andorath/4noks_daemon'


emptyDict = {   "+": None,
                "-": None,
                "%": None,
            }

class Plug(Instrument):

    #alarms = None
    
    def __init__(self, port, addr):
        self.alarms = {"Watt": emptyDict.copy()}
        self.relayStatus = ""
        self.upperWattThresholdCount = 0
        self.lowerWattThresholdCount = 0
        self.wattStatus = None

        Instrument.__init__(self, port, addr)

    def setRelay(self, status):
        register = 1 if int(status) == 1 else 2
        self.write_bit(register, 1)
    
    def isRelayChanged(self):
        status = "Acceso" if self.read_bit(0) else "Spento"
        if status != self.relayStatus:
            self.relayStatus = status
            return(True, status)
        return(False, None)

    def setAddress(self, interface, address):
        tmp_plug = Instrument(interface, 127)
        tmp_plug.write_register(0, 6521, functioncode=6)
        tmp_plug.write_register(2, address, functioncode=6)
        tmp_plug.write_bit(0, 1)
    

    def readDevice(self, channel='status'):
        valueList = self.read_registers(0, 15, functioncode=4)
        valueList.append(self.read_bit(0))
        valueList.append(self.read_bit(1))
        valueList.append(self.read_bit(13))
        return buildJSON(zip(util.plugKeyList, valueList), self.address, channel)

    def isWattMoreThan(self, value):
        newWatt = self.read_register(5, functioncode=4)
        isMore = newWatt > value 
        self.upperWattThresholdCount = self.upperWattThresholdCount + 1 if isMore else 0
        return (isMore, newWatt)

    def isWattLessThan(self, value):
        newWatt = self.read_register(5, functioncode=4)
        isLess = newWatt < value 
        self.lowerWattThresholdCount = self.lowerWattThresholdCount + 1 if isLess else 0
        return (isLess, newWatt)

    def isWattChanged(self, percentage):
        newWatt = self.read_register(5, functioncode=4)
        if self.wattStatus == None or abs(newWatt - self.wattStatus) > (percentage / 100) * self.wattStatus:
            self.wattStatus = newWatt
            return (True, newWatt)
        else:
            return (False, newWatt)

    callbackDict = {    
                        "Watt": {       
                                "+": isWattMoreThan,
                                "-": isWattLessThan,
                                "%": isWattChanged
                                }
                    }
    
    def checkAlarms(self):
        resultDic = {}
        for key in self.alarms.keys():
            resultDic[key] = {}
            for k,v in self.alarms[key].items():
                if v is not None:
                    resultDic[key][k] = Plug.callbackDict[key][k](self,int(v))
            resultDic[key] = dict((k,v) for k,v in resultDic[key].iteritems() if v[0] is True)
        return resultDic

class Therm(Instrument):

    def __init__(self, port, addr):
        #self.alarms = dict.fromkeys(("Temp", "Hum", "Volt"), emptyDict.copy())
        self.alarms =   {   "Temp": emptyDict.copy(),
                            "Hum": emptyDict.copy(),
                            "Volt": emptyDict.copy()
                        }

        self.upperTempThresholdCount = 0
        self.lowerTempThresholdCount = 0
        self.upperHumThresholdCount = 0
        self.lowerHumThresholdCount = 0
        self.upperVoltThresholdCount = 0
        self.lowerVoltThresholdCount = 0

        for key in self.alarms.keys():
            self.alarms[key]["%"] = "5"

        self.tempStatus = self.humStatus = self.voltStatus = None
        Instrument.__init__(self, port, addr)

    def __str__(self):
        return "-THERM-\n\t upperTemp: %s lowerTemp: %s " % (str(self.upperTempThresholdCount), str(self.lowerTempThresholdCount))

    def setAddress(self, interface, address):
        pass
    
    def readDevice(self, channel='status'):
        valueList = self.read_registers(0, 14, functioncode=4)
        return buildJSON(zip(util.thermKeylist, valueList), self.address, channel)
    
    def isTempMoreThan(self, value):
        newTemp = self.read_register(6, functioncode=4)
        isMore = newTemp > value * 10
        if isMore : 
            self.upperTempThresholdCount += 1
        else :
            self.upperTempThresholdCount = 0
        return (isMore , newTemp)

    def isTempLessThan(self, value):
        newTemp = self.read_register(6, functioncode=4)
        isLess = newTemp < value * 10
        if isLess:
            self.lowerTempThresholdCount += 1
        else:
            self.lowerTempThresholdCount = 0
        return (isLess, newTemp)

    def isHumidityMoreThan(self, value):
        newHum = self.read_register(7, functioncode=4)
        isMore = newHum > value
        if isMore:
            self.upperHumThresholdCount += 1
        else:
            self.upperHumThresholdCount = 0
        return (isMore, newHum)

    def isHumidityLessThan(self, value):
        newHum = self.read_register(7, functioncode=4)
        isLess = newHum < value
        if isLess:
            self.lowerHumThresholdCount += 1
        else:
            self.lowerHumThresholdCount = 0
        return (isLess, newHum)

    def isVoltMoreThan(self, value):
        newVolt = self.read_register(5, functioncode=4)
        isMore = newVolt > value
        if isMore:
            self.upperVoltThresholdCount += 1
        else:
            self.upperVoltThresholdCount = 0
        return (isMore, newVolt)

    def isVoltLessThan(self, value):
        newVolt = self.read_register(5, functioncode=4)
        isLess = newVolt < value
        if isLess:
            self.lowerVoltThresholdCount += 1
        else:
            self.loweVoltThreshold = 0
        return (isLess, newVolt)
    
    def isTemperatureChanged(self, percentage):
        newTemp = self.read_register(6, functioncode=4)
        if not self.tempStatus or abs(newTemp - self.tempStatus)/self.tempStatus >= percentage / 100:
            self.tempStatus = newTemp
            return (True, newTemp)
        return (False, None)
        
    def isHumidityChanged(self, percentage):
        newHum = self.read_register(7, functioncode=4)
        if not self.humStatus or abs(newHum - self.humStatus)/self.humStatus >= percentage / 100:
            self.humStatus = newHum
            return (True, newHum)
        return (False, None)

    def isVoltageChanged(self, percentage):
        newVolt = self.read_register(5, functioncode=4)
        if not self.voltStatus or abs(newVolt - self.voltStatus)/self.voltStatus >= percentage / 100:
            self.voltStatus = newVolt
            return (True, newVolt)
        return (False, None)


    callbackDict =   {    
                        "Temp": {       
                                    "+": isTempMoreThan,
                                    "-": isTempLessThan,
                                    "%": isTemperatureChanged
                                },
              
                        "Hum": {        
                                    "+": isHumidityMoreThan,
                                    "-": isHumidityLessThan,
                                    "%": isHumidityChanged
                                },
                        "Volt": {
                                    "+": isVoltMoreThan,
                                    "-": isVoltLessThan,
                                    "%": isVoltageChanged
                                }
                    } 

    def checkAlarms(self):
        resultDic = {}
        for key in self.alarms.keys():
            resultDic[key] = {}
            for k,v in self.alarms[key].items():
                if v is not None:
                    resultDic[key][k] = Therm.callbackDict[key][k](self,int(v))

            resultDic[key] = dict((k,v) for k,v in resultDic[key].iteritems() if v[0] is True)
        return resultDic

        
class Sonda(Instrument):
	pass

def buildJSON(dict_values, addr, channel):
    util.wrapperJSON['4noks'][channel] = dict_values
    util.wrapperJSON['4noks']['timestamp'] = time.time()
    util.wrapperJSON['4noks']['address_source'] = addr
    return json.dumps(util.wrapperJSON,ensure_ascii='False')

