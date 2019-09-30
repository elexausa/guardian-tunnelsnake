import socket, threading, time, json
from pprint import pprint
from enum import IntEnum
import os

# Todo items, placed at top for visibility
todos = ("Add serial support", 
    "Add bluetooth support", 
    "Display available devices", 
    "Implement master command processor (MCP)", 
    "Parse packet response (also MCP?)", 
    "Add logging")

# General program information
name = "Guardian Tunnelsnake"
description = "Provides easy access to networked Guardian devices via UDP, TCP, Serial,\nand Bluetooth connections."
created = "10-8-2018"
__author__ = "Alex Bennett"
__email__ = "abennett@elexausa.com"
__copyright__ = "(c) Copyright 2018, Elexa Consumer Products, Inc."
__version__ = "0.0.1"
__status__ = "Development"

class Utilities(object):
    @staticmethod
    def log_info(msg):
        """Log message with INFO tag."""
        print "[INFO]", msg

    @staticmethod
    def log_warn(msg):
        """Log message with WARN tag."""
        print "[WARN]", msg

    @staticmethod
    def log_err(msg):
        """Log message with ERROR tag."""
        print "[ERROR]", msg

    @staticmethod
    def separator():
        """Prints a long separator."""
        _, cols = os.popen('stty size', 'r').read().split()

        separator = ""

        for x in xrange(int(cols)):
            separator += "="

        print " "
        print separator
        print " "

    @staticmethod
    def header(header):
        """Prints a long separator."""
        _, cols = os.popen('stty size', 'r').read().split()

        separator = ""

        for x in xrange(int(cols)):
            separator += "="

        print " "
        print separator
        print " " + str(header)
        print separator
        print " "

class Guardian_Tunnel(object):
    class Status(IntEnum):
        OK = 0
        UDP_CONFIG_ERROR = 1 
        INCORRECT_MODE = 2 
        PACKET_ERROR = 3
        SOCKET_ERROR = 4

    class Mode(IntEnum):
        UDP = 0
        TCP = 1
        Serial = 2

    def __init__(self, mode=Mode.UDP, udp_ip=None, udp_port=None):
        # Initial declarations
        self.mode = mode
        self.sock = None

        # Check mode and setup accordingly
        if self.mode == self.Mode.UDP:
            # Check that ip and port have been provided
            if udp_ip == None or udp_port == None:
                Utilities.log_err("UDP configuration error")

                while True:
                    pass

            # Store IP and port
            self.udp_ip = udp_ip
            self.udp_port = int(udp_port)
        elif self.mode == self.Mode.TCP:
            self.chatserver_ip = "channel01.guardiancloud.services" 
            self.chatserver_port = "8888" 
        
    def open(self):
        """Opens tunnel to device with provided information."""

        # Proceed for UDP
        if self.mode == self.Mode.UDP:
            # Confiugure socket for UDP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Bind
            self.sock.bind(("", self.udp_port))

            # Setup listener thread
            self.listener = threading.Thread(target=self.listen_udp)
            self.listener.daemon = True
            self.listener.start()

            # Wait for thread to start
            time.sleep(2)

            # Return status
            return self.Status.OK
        else:
            Utilities.log_err("Incorrect mode selected")
            return self.Status.INCORRECT_MODE

    def listen_udp(self):
        """Listens to configured UDP socket and prints received packets."""

        # Exit if incorrect mode
        if self.mode != self.Mode.UDP:
            Utilities.log_err("Incorrect mode selected")
            return self.Status.INCORRECT_MODE

        # Listener started
        Utilities.log_info("UDP listener started for " + str(self.udp_ip) + ":" + str(self.udp_port))            

        while True:
            # Receive data
            data, addr = self.sock.recvfrom(1024)
        
            # Parse resulting JSON
            parsed_json = json.loads(data)

            # Display
            print " "
            print "Received packet (from " + addr[0] + "): "
            print " "
            pprint(parsed_json)
            print " "

    def close_udp(self):
        """Close UDP socket."""

        # Exit if incorrect mode
        if self.mode != self.Mode.UDP:
            Utilities.log_err("Incorrect mode selected")
            return self.Status.INCORRECT_MODE

        # Close socket
        self.sock.close()

        # Remove socket object
        self.sock = None

        # Return status
        return self.Status.OK

    def send_packet(self, packet=None):
        """Sends packet to connected device."""

        # Exit if incorrect mode
        if self.mode != self.Mode.UDP:
            Utilities.log_err("Incorrect mode selected")
            return self.Status.INCORRECT_MODE

        # Socket open?
        if self.sock == None:
            Utilities.log_err("Please open the UDP socket")
            return self.Status.SOCKET_ERROR

        # Valid packet provided?
        if packet == None:
            Utilities.log_err("Invalid packet provided")
            return self.Status.PACKET_ERROR

        # All good, send packet
        self.sock.sendto(packet, (self.udp_ip, self.udp_port))

        # Return status
        return self.Status.OK

class Guardian_Valve_Controller_V1_Commands(object):
    GET_VALVE = '{"command":"get_valve","type":0,"silent":0}'
    MOTOR_ACTION_OPEN = '{"command":"motor_action","action":"open","type":0}'
    MOTOR_ACTION_CLOSE = '{"command":"motor_action","action":"close","type":0}'
    GET_SENSOR_LIST = '{"command":"get_sensor_list","type":0,"silent":0}'
    UPDATE_ESP32 = '{{"command":"update_esp32","address":"{ip}","port":"{port}","filename":"{path}","type":0}}'
    UPDATE_LORA = '{{"command":"update_lora","address":"{ip}","port":"{port}","filename":"{path}","type":0}}'
    CANCEL_LEAK = '{"command":"leak_ignore", "type":0}'
    ENABLE_LEAK_CANCEL = '{"command":"leak_ignore_config","option":1,"type":0}'
    DISABLE_LEAK_CANCEL = '{"command":"leak_ignore_config","option":0,"type":0}'
    CLEAR_CALIBRATION = '{"command":"motor_erase_calibration","type":0}'
    SET_WIFI_AP = '{{"command":"set_WIFI_ap","type":0,"option":{option}}}'
    SET_WIFI_STATION = '{{"command":"set_WIFI_station","SSID":"{ssid}","PASS":"{password}","type":0,"connect":1}}'

class Menu_Helper(object):
    @staticmethod
    def welcome():
        """Displays welcome message with program information."""
        
        print " "
        print " ######   ##     ##    ###    ########  ########  ####    ###    ##    ##"
        print "##    ##  ##     ##   ## ##   ##     ## ##     ##  ##    ## ##   ###   ##" 
        print "##        ##     ##  ##   ##  ##     ## ##     ##  ##   ##   ##  ####  ##"
        print "##   #### ##     ## ##     ## ########  ##     ##  ##  ##     ## ## ## ##"
        print "##    ##  ##     ## ######### ##   ##   ##     ##  ##  ######### ##  ####"
        print "##    ##  ##     ## ##     ## ##    ##  ##     ##  ##  ##     ## ##   ###"
        print " ######    #######  ##     ## ##     ## ########  #### ##     ## ##    ##"
        print "                                                                 by Elexa"
        print " "
        print name + " (v" + __version__ + ", " + __status__ + ")\n"
        print description
        print " "
        print __copyright__
        print " "
        print "Author: " + __author__
        print "Email: " + __email__
        print "Created: " + created
        print " "
        print "Todo:"

        for todo in todos:
            print " - " + todo

        print " "

    @staticmethod
    def choose_mode():
        # Print header
        Utilities.header("Available Modes")

        # Display modes
        for mode in iter(Guardian_Tunnel.Mode):
            print " " + str(int(mode)) + ".) " + str(mode)

        # New line
        print " "

        # Accept choice
        choice = raw_input("Please choose a mode by entering its number: ")

        # Validate choice
        if int(choice) < 0 or int(choice) > len(list(Guardian_Tunnel.Mode)):
            raise Exception("Not a valid choice")

        # Validated, return
        return int(choice)

if __name__ == "__main__":
    try:
        # Create tunnel var
        tunnel = None

        # Print welcome page
        Menu_Helper.welcome()

        # Choose mode
        chosen_mode = Menu_Helper.choose_mode()

        if chosen_mode == int(Guardian_Tunnel.Mode.UDP):
            # Request device info
            device_ip = raw_input("Guardian device IP: ")
            device_port = raw_input("Guardian device port: ")
        
            # Initialize guardian tunnel in UDP mode
            tunnel = Guardian_Tunnel(Guardian_Tunnel.Mode.UDP, device_ip, device_port)
        elif chosen_mode == int(Guardian_Tunnel.Mode.TCP):
            raise Exception("Not currently supported.")
        elif chosen_mode == int(Guardian_Tunnel.Mode.Serial):
            raise Exception("Not currently supported.")

        # Open socket
        tunnel.open()

        Utilities.log_info("Waiting for packet to send...\n")

        # Enter main loop
        while True:
            # Accept packet
            packet = raw_input("PACKET> ")

            # Exit?
            if packet.lower() in ("quit", "bye", "leave"):
                Utilities.log_info("Exit requested")
                raise SystemExit

            # Parse packet
            # TODO: Move this into its own handler

            split_packet = packet.split(':')
            command = split_packet[0]
            params = []

            # Params
            if len(split_packet) > 1:
                raw_params = split_packet[1]
                # Parse params
                params = raw_params.split(',')

            if command == "gv": # Get valve
                packet = Guardian_Valve_Controller_V1_Commands.GET_VALVE
                       
            elif command == "gs": # Get sensors
                packet = Guardian_Valve_Controller_V1_Commands.GET_SENSOR_LIST
            
            elif command == "uesp": # Update EPS
                # Validate param length
                if len(params) != 3:
                    Utilities.log_err("Invalid packet. Check formatting. \n\n\tuesp:<ip>,<port>,<path>\n")
                    continue

                # FIXME: This needs to be validated more (regex)!
                ip = params[0]
                port = params[1]
                path = params[2]

                packet = Guardian_Valve_Controller_V1_Commands.UPDATE_ESP32.format(ip=ip, port=port, path=path)
            
            elif command == "ulora":
                # Validate param length
                if len(params) != 3:
                    Utilities.log_err("Invalid packet. Check formatting. \n\n\tulora:<ip>,<port>,<path>\n")
                    continue

                # FIXME: This needs to be validated more (regex)!
                ip = params[0]
                port = params[1]
                path = params[2]

                packet = Guardian_Valve_Controller_V1_Commands.UPDATE_LORA.format(ip=ip, port=port, path=path)

            elif command == "sap": # Set wifi access point on/off
                # Validate param length
                if len(params) != 1:
                    Utilities.log_err("Invalid packet. Check formatting. \n\n\tsap:<option: 1/0>\n")
                    continue

                # FIXME: This needs to be validated more (regex)!
                option = params[0]

                packet = Guardian_Valve_Controller_V1_Commands.SET_WIFI_AP.format(option=option)

            elif command == "swifi": # Set wifi station
                # Validate param length
                if len(params) != 2:
                    Utilities.log_err("Invalid packet. Check formatting. \n\n\tswifi:<ssid>,<password>\n")
                    continue

                # FIXME: This needs to be validated more (regex)!
                ssid = params[0]
                password = params[1]

                packet = Guardian_Valve_Controller_V1_Commands.SET_WIFI_STATION.format(ssid=ssid,password=password)

            elif command == "cc": # Clear calibration
                packet = Guardian_Valve_Controller_V1_Commands.CLEAR_CALIBRATION

            elif command == "open": # Open valve
                packet = Guardian_Valve_Controller_V1_Commands.MOTOR_ACTION_OPEN

            elif command == "close": # Close valve
                packet = Guardian_Valve_Controller_V1_Commands.MOTOR_ACTION_CLOSE

            else:
                Utilities.log_err("Unknown command")
                continue

            # Log packet being sent
            Utilities.log_info("Sending packet: {p}".format(p=packet))

            # Send packet
            tunnel.send_packet(packet)

            # Wait a moment to allow response
            # FIXME: This is ugly but to prevent the response from writing 
            # to the console AFTER raw_input has been sent (looks bad)
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        # Clean exit
        print ""
        Utilities.log_info(name + " (v" + __version__ + ", " + __status__ + ") session ended")
