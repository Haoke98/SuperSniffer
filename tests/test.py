# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/1/20
@Software: PyCharm
@disc:
======================================="""
from scapy.all import *
import os


def process_packet(packet):
    print("Packet received:", packet)
    if packet.haslayer('Raw'):
        print("Raw packet")
        raw_data = packet['Raw'].load
        print(raw_data)
        if b'Content-Type: image' in raw_data:
            with open(f"image{str(time.time())}.jpg", "wb") as f:
                f.write(raw_data)
                f.close()


if __name__ == '__main__':
    # os.system("sudo sysctl -w net.ipv4.ip_forward=1")
    sniff(prn=process_packet, store=0, filter="ip src 218.31.113.195 and (tcp src port 49900)")
