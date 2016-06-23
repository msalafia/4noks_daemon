INTERFACE = "/dev/ttyUSB0"
BHOST = "192.168.1.8"
BPORT = 1883
COMMAND_TOPIC = "Lagarto-SWAP/simple/control/4noks/command"
STATUS_TOPIC = "Lagarto-SWAP/json/status"

'''
 Struttura device
'''

device_t = ["Plug", "Therm", "Sonda", "Instrument"]

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
                "Energy_consumed_high",
                "Energy_consumed_low",
                "Measurement_time_high",
                "Measurement_time_low",
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
