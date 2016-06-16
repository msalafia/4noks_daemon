INTERFACE = "/dev/ttyUSB0"
BHOST = "localhost"
BPORT = 1883
COMMAND_TOPIC = "Lagarto-SWAP/simple/control/4noks/command"
STATUS_TOPIC = "Lagarto-SWAP/json/status"
ALARM_TOPIC = '/4noks/alarm'

'''
 Struttura device
'''

device_t = ["Plug", "Therm", "Sonda", "Instrument"]

wrapperJSON =   {
                    '4noks' :   { 
                                'status' : None, 
                                'timestamp' : None, 
                                'address_source' : None                                 
                                } 
                }

thermKeylist = 	["Type",
		"Firmware_version",
		"Message_sent_counter",
		"Level_radio_signal_last_message",
		"Address",
		"Power_level",
		"Temperature",
		"Humidity",
		"Seconds_from_last_message",
		"Counter_of_messages_received_from_gateway",
		"Gateway_receiving_instant_time",
		"Signal_level_of_last_gateway_message",
		"Device_network_address"]

plugKeyList = [ "Type",
                "Firmware_version",
                "Message_sent_counter",
                "Level_radio_signal_last_message",
                "Energy_meter_calibration_parameter",
                "Active_power",
                "Energy_consumed_(high)",
                "Energy_consumed_(low)",
                "Measurement_time_(hight)",
                "Measurement_time_(low)",
                "Seconds_to_last_message",
                "Counter_of_messages_received_from_gateway",
                "Gateway_receiving_instant_time",
                "Signal_level_of_last_gateway_message",
                "Device_network_address",
                "Relay_status",
                "Stand-by_killer_status",
                "Device_presence_status"]

class CommandNotFoundException(Exception):
    pass

class CommandNotSupportedException(Exception):
    pass

class DeviceAddressUnknownException(Exception):
    pass
