#!/usr/bin/env python 

import paho.mqtt.client as mqtt
import getopt
import time
import threading
import re
import pickle

from device_class import *
from namespace import *
from minimalmodbus import *

TEMP_PERCENTAGE = 0.4
HUM_PERCENTAGE = 1
VOLT_PERCENTAGE = 1

'''
    DEVICES
'''

def getBuilder(deviceType):
    return  {   "Plug": lambda inter, addr: Plug(inter, addr),
                "Therm": lambda inter, addr: Therm(inter, addr),
                "Sonda": lambda inter, addr: Sonda(inter, addr),
                "Instrument": lambda inter, addr: Instrument(inter, addr)
            }[deviceType]

def getDevicesFromFile():
    try:
        with open('devices.dsla','rb') as binary:
            new_devs = {}
            devs = pickle.load(binary)
            for k, v in devs.items():
                new_devs[k] = getBuilder(v.__class__.__name__)(INTERFACE, v.address)
                if not v.__class__.__name__ is "Instrument":
                    alarms = devs[k].alarms
                    new_devs[k].alarms = alarms
        return new_devs

    except IOError, err:
        return {1: Instrument(INTERFACE, 1)}

def storeDevices():
    with open('devices.dsla', 'wb') as binary:
            pickle.dump(devices, binary, pickle.HIGHEST_PROTOCOL)
'''
    CLIENT MQTT
'''
def initialize_client(argv):
    try:
        opts, args = getopt.getopt(argv, "a:p:i:h", ["address=", "port=", "interface=", "help"])

    except getopt.GetoptError:
        usage()

    invalid_arg = re.compile("^.+=.*$")

    for opt, arg in opts:
        if invalid_arg.match(arg):
            raise Exception, "Invalid argument " + arg
        if opt in ("-i", "--interface"):
            global INTERFACE
            INTERFACE = arg
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-a", "--address"):
            global BHOST
            BHOST = arg
        if opt in ("-p", "--port"):
            global BPORT
            BPORT = arg

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print "connect to " + BHOST + " @ " + str(BPORT)
    client.connect(BHOST, BPORT, 60)

    return client

def usage():
    print "\nUsage: \n\tdatachange.py [-a, --address host] [-p, --port port]"
    print "\tDefault address is localhost, default port is 1883\n"
    os._exit(1)

'''
    COMANDI
'''
def pubTempMoreThan(newValue, therm):
    if therm.upperTempThresholdCount <= 3:
        publish("La temperatura di [" + str(therm.address) +"] ha superato la soglia massima impostata di "+ therm.alarms["Temp"]["+"] + " raggiungendo il valore di " + str(newValue))
        publish(therm.readDevice(channel='alarm'))

def pubTempLessThan(newValue, therm):
    if therm.lowerTempThresholdCount <= 3:
        publish("La temperatura di [" + str(therm.address) +"] ha superato la soglia minima impostata di " + therm.alarms["Temp"]["-"]  + " raggiungendo il valore di " + str(newValue))
        publish(therm.readDevice(channel='alarm'))

def pubTempPercentage(newValue, therm):
        publish("La temperatura di [" + str(therm.address) +"] e' variata del "+ therm.alarms["Temp"]["%"]  + "% raggiungendo il valore di " + str(newValue))
        publish(therm.readDevice())
    

def pubHumMoreThan(newValue, therm):
    if therm.upperHumThresholdCount <= 3:
        publish("L'umidita' di [" + str(therm.address) +"] ha superato la soglia massima impostata di " + therm.alarms["Hum"]["+"]  + " raggiungendo il valore di " + str(newValue))
        publish(therm.readDevice(channel='alarm'))

def pubHumLessThan(newValue, therm):
    if therm.lowerHumThresholdCount <= 3:
        publish("L'umidita' di [" + str(therm.address) +"] ha superato la soglia minima impostata di " + therm.alarms["Hum"]["-"] + " raggiungendo il valore di " + str(newValue))
        publish(therm.readDevice(channel='alarm'))

def pubHumPercentage(newValue, therm): 
    publish("L'umidita' di [" + str(therm.address) +"] e' variata del "+ therm.alarms["Hum"]["%"] + "% raggiungendo il valore di " + str(newValue))
    publish(therm.readDevice())

def pubVoltMoreThan(newValue, therm):
    if therm.upperVoltThresholdCount <= 3:
        publish("Il voltaggio di [" + str(therm.address) +"] ha superato la soglia massima impostata di "+ therm.alarms["Volt"]["+"]  + " raggiungendo il valore di " + str(newValue))
        publish(therm.readDevice(channel='alarm'))

def pubVoltLessThan(newValue, therm): 
    if therm.lowerVoltThresholdCount <= 3:
        publish("Il voltggio di [" + str(therm.address) +"] ha superato la soglia minima impostata di " + therm.alarms["Volt"]["-"] + " raggiungendo il valore di " + str(newValue))
        publish(therm.readDevice(channel='alarm'))

def pubVoltPercentage(newValue, therm): 
    publish("Il voltaggio di [" + str(therm.address) +"] e' variato del " + therm.alarms["Volt"]["%"]  +  "% raggiungendo il valore di " + str(newValue))
    publish(therm.readDevice())

def pubWattMoreThan(newValue, plug): 
    if plug.upperWattThresholdCount <= 3:
        publish("Il carico [W] di [" + str(plug.address) +"] ha superato la soglia massima impostata di " + plug.alarms["Watt"]["+"] + " raggiungendo il valore di " + str(newValue))
        publish(plug.readDevice(channel='alarm'))


def pubWattLessThan(newValue, plug): 
    if plug.lowerWattThresholdCount <= 3:
        publish("Il carico [W] di [" + str(plug.address) +"] ha superato la soglia minima impostata di " + plug.alarms["Watt"]["-"] + " raggiungendo il valore di " + str(newValue))
        publish(plug.readDevice(channel='alarm'))

def pubWattPercentage(newValue, plug):
    
    publish("Il carico [W] di [" + str(plug.address) +"] e' variato del " + plug.alarms["Watt"]["%"]  +  "% raggiungendo il valore di " + str(newValue))
    publish(plug.readDevice(channel='alarm'))



publishCallbackDict =   {
                    "Watt": {
                                "+": pubWattMoreThan,
                                "-": pubWattLessThan,
                                "%": pubWattPercentage
                            },
                    "Temp": {       
                                "+": pubTempMoreThan,
                                "-": pubTempLessThan,
                                "%": pubTempPercentage,
                            },
          
                    "Hum": {        
                                "+": pubHumMoreThan,
                                "-": pubHumLessThan,
                                "%": pubHumPercentage
                            },
                    "Volt": {
                                 "+": pubVoltMoreThan,
                                 "-": pubVoltLessThan,
                                 "%": pubVoltPercentage
                            }
                    } 

def getPublishCallback(k_e, k_i):
    return publishCallbackDict[k_e][k_i]

def publish(msg):
    client.publish(STATUS_TOPIC, msg)

def publishAlarm(alarm):
    client.publish(ALARM_TOPIC, alarm)

def splitCommand(command):
    splitted = command.split("_")
    if len(splitted) > 1: splitted[1] = int(splitted[1])
    return [splitted[0], tuple(splitted[1:])]

def setAddress(address, deviceType):

    if address in devices:
        publish("Address " + str(address) + " already in use.")
        return

    if deviceType not in device_t:
        publish("Device " + deviceType + " not recognized.")
        return
    
    devices[address] = getBuilder(deviceType)(INTERFACE, address)

    devices[address].setAddress(INTERFACE, address)

    
    storeDevices()

    publish("Device " + deviceType + " @ " + str(address))

def deleteAddress(address):
    gateway = devices[1]
    gateway.write_register(1, address, functioncode=6)
    gateway.write_register(0, 12545, functioncode=6) #mettere command in un file
    gateway.write_bit(0,1)

    try:
        del devices[address]
    except KeyError:
        publish("Unknown address")
        
    storeDevices()


def setRelay(address, status):
    if address not in devices: raise DeviceAddressUnknownException("Unknown address " + str(address) + ".") 
    if isinstance(devices.get(address, None), Plug):
        devices[address].setRelay(status)
    else:
        raise CommandNotSupportedException("Command not supported. Device " + str(address) + " is not a Plug")

def readDevice(address):
    publish(devices[address].readDevice())

def validateAlarmCommand(command):
    valid_modval = re.compile("^[\+,%,-]\d{1,5}$")
    if not valid_modval.match(command):        
        raise CommandNotFoundException("Command not found.")

def setWattAlarm(address,modval):
    validateAlarmCommand(modval)
    if not isinstance(devices.get(address, None), Plug):
        raise CommandNotSupportedException("Command not supported. Device " + str(address) + " is not a Plug")
    
    devices[address].alarms["Watt"][modval[0]] = modval[1:]
    storeDevices()
    
def setTempAlarm(address, modval):
    validateAlarmCommand(modval)
    if not isinstance(devices.get(address, None), Therm):
        raise CommandNotSupportedException("Command not supported. Device " + str(address) + " is not a Therm")

    devices[address].alarms["Temp"][modval[0]] = modval[1:]
    storeDevices()

def setHumAlarm(address, modval):
    validateAlarmCommand(modval)
    if not isinstance(devices.get(address, None), Therm):
        raise CommandNotSupportedException("Command not supported. Device " + str(address) + " is not a Therm")

    devices[address].alarms["Hum"] = {modval[0]: modval[1:]}
    storeDevices()

def setVoltAlarm(address, modval):
    validateAlarmCommand(modval)
    if not isinstance(devices.get(address, None), Therm):
        raise CommandNotSupportedException("Command not supported. Device " + str(address) + " is not a Therm")

    devices[address].alarms["Volt"] = {modval[0]: modval[1:]}
    storeDevices()

def openGateway():
    gateway = devices[1]
    gateway.write_register(0, 5266, functioncode=6)
    gateway.write_bit(0, 1)
    publish("Opening Network...")

def closeGateway():
    gateway = devices[1]
    gateway.write_register(0, 5267, functioncode=6)
    gateway.write_bit(0, 1)
    publish("Closing Network...")


'''
    Dizionario dei comandi disponibili
'''

commands =  {   "setAddress"    :   setAddress,
                "deleteAddress" :   deleteAddress,
                "setRelay"      :   setRelay,
                "readDevice"    :   readDevice,
                "setWattAlarm"  :   setWattAlarm,
                "setTempAlarm"  :   setTempAlarm,
                "setHumAlarm"   :   setHumAlarm,
                "setVoltAlarm"  :   setVoltAlarm,
                "openGateway"   :   openGateway,
                "closeGateway"  :   closeGateway
            }

''' POLLING '''

def scanPlugs():
    for p in filter(lambda x: isinstance(x,Plug), devices.values()):
        try:
            changed, status = p.isRelayChanged()
            resultDic = p.checkAlarms()
            for key in resultDic.keys():
                for mode, value in resultDic[key].items():
                    publishCallbackDict[key][mode](value[1], p)

        except ValueError as err:
            p.serial.close()
            p.serial.open()
            continue

        except IOError as err:
            print("IOError: {0}".format(err) + "\nRilevato al Dispositivo di indirizzo " + str(p.address) + ".")
            continue

        if changed:
                publish("Plug " + str(p.address) +": " + str(status))
                publish(p.readDevice())

         

def scanTherms():
    for t in filter(lambda x: isinstance(x,Therm), devices.values()):
        try:
            resultDic = t.checkAlarms()
            for key in resultDic.keys():
                for mode,value in resultDic[key].items():
                    publishCallbackDict[key][mode](value[1], t)
                    
        except ValueError as err:
            t.serial.close()
            t.serial.open()
            continue

        except IOError as err:
            print("IOError: {0}".format(err) + "\nRilevato al Dispositivo di indirizzo " + str(t.address) + ".")
            continue

''' MQTT CALLBACK '''


def on_connect(client, userdata, rc):
    client.subscribe(COMMAND_TOPIC)
    print "Connected with result code "+ str(rc)

def on_message(client, userdata, message):
    try:
        cmd_str, args = splitCommand(str(message.payload))
        if cmd_str in commands.keys():
            cmd = commands.get(cmd_str)
            cmd(*args)
        else:
            publish("Command not found.")
    except CommandNotSupportedException, err:
        publish(str(err))
    except DeviceAddressUnknownException, err:
        publish(str(err))
    except ValueError:
        publish("Please try again.")

   
''' 
    MAIN
'''
if __name__ == "__main__":
    devices = getDevicesFromFile()
    client = initialize_client(sys.argv[1:])
    while True:
        client.loop()
        scanPlugs()
        scanTherms()
        time.sleep(0.25)

