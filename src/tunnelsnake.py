import socket, threading, time, json
from pprint import pprint

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
    print "-----"
    print " "

def log_info(msg):
    """Log message with INFO tag."""
    print "[INFO]", msg

def log_warn(msg):
    """Log message with WARN tag."""
    print "[WARN]", msg

def log_err(msg):
    """Log message with ERROR tag."""
    print "[ERROR]", msg


class Guardian_Tunnel(object):
    class Status:
        OK, UDP_CONFIG_ERROR, INCORRECT_MODE, PACKET_ERROR, SOCKET_ERROR = range(0, 5)

    class Mode:
        UDP, TCP, Serial = range(0, 3)

    def __init__(self, mode=Mode.UDP, udp_ip=None, udp_port=None):
        # Initial declarations
        self.mode = mode
        self.sock = None

        # Check mode and setup accordingly
        if self.mode == self.Mode.UDP:
            # Check that ip and port have been provided
            if udp_ip == None or udp_port == None:
                log_err("UDP configuration error")

                while True:
                    pass

            # Store IP and port
            self.udp_ip = udp_ip
            self.udp_port = int(udp_port)
        
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
            log_err("Incorrect mode selected")
            return self.Status.INCORRECT_MODE

    def listen_udp(self):
        """Listens to configured UDP socket and prints received packets."""

        # Exit if incorrect mode
        if self.mode != self.Mode.UDP:
            log_err("Incorrect mode selected")
            return self.Status.INCORRECT_MODE

        # Listener started
        log_info("UDP listener started for " + str(self.udp_ip) + ":" + str(self.udp_port))            

        while True:
            # Receive data
            data, addr = self.sock.recvfrom(1024)
        
            # Parse resulting JSON
            parsed_json = json.loads(data)

            # Display
            print " "
            print "Received packet (from " + addr[0] + "): "
            print "---"
            pprint(parsed_json)
            print " "

    def close_udp(self):
        """Close UDP socket."""

        # Exit if incorrect mode
        if self.mode != self.Mode.UDP:
            log_err("Incorrect mode selected")
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
            log_err("Incorrect mode selected")
            return self.Status.INCORRECT_MODE

        # Socket open?
        if self.sock == None:
            log_err("Please open the UDP socket")
            return self.Status.SOCKET_ERROR

        # Valid packet provided?
        if packet == None:
            log_err("Invalid packet provided")
            return self.Status.PACKET_ERROR

        # All good, send packet
        self.sock.sendto(packet, (self.udp_ip, self.udp_port))

        # Return status
        return self.Status.OK


class Tunnel_Command_Processor(object):
    def __init__(self):
        pass
    
    @staticmethod
    def process_command(self, str):
        pass


if __name__ == "__main__":
    try:
        # Print welcome page
        welcome()

        # Request device info
        device_ip = raw_input("Guardian device IP: ")
        device_port = raw_input("Guardian device port: ")

        # Initialize guardian tunnel in UDP mode
        tunnel = Guardian_Tunnel(Guardian_Tunnel.Mode.UDP, device_ip, device_port)

        # Open socket
        tunnel.open()

        log_info("Waiting for packet to send...")

        # Enter main loop
        while True:
            # Accept packet
            packet = raw_input("")

            # Exit?
            if packet.lower() in ("quit", "bye", "leave"):
                log_info("Exit requested")
                raise SystemExit

            # Send packet
            tunnel.send_packet(packet)

    except (KeyboardInterrupt, SystemExit):
        # Clean exit
        print ""
        log_info(name + " (v" + __version__ + ", " + __status__ + ") session ended")
