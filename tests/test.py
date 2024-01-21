# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/1/20
@Software: PyCharm
@disc:
======================================="""
import binascii
from io import BytesIO

from scapy.all import sniff
from PIL import Image
from scapy.layers.http import HTTPResponse, HTTPRequest
import os

from scapy.layers.inet import TCP, IP
from scapy.plist import PacketList
from scapy.sessions import DefaultSession

tcp_streams = {}


def reassemble_tcp_stream(session):
    # 获取当前流的包列表
    stream = tcp_streams[session]
    # 对数据包按序列号排序
    stream.sort(key=lambda x: x[TCP].seq)
    print(session, len(tcp_streams), len(stream))
    # 重组成一个字节流
    byte_stream = b''
    for pkt in stream:
        payload = bytes(pkt[TCP].payload)
        seq = pkt[TCP].seq
        if not byte_stream:
            # 如果 byte_stream 为空，直接添加数据
            byte_stream += payload
        elif seq >= stream[0][TCP].seq + len(byte_stream):
            # 如果当前包的起始序列号大于等于整个 TCP 会话的起始序列号 + 当前 byte_stream 的长度
            byte_stream += payload
        else:
            # 重叠或重复包，可能需要特殊处理
            raise Exception("invalid payload")
    # 检查是否为 HTTP 响应
    if b"HTTP/" in byte_stream:
        # 简单地查找图片数据的开始和结束位置
        start = byte_stream.find(b'\r\n\r\n') + 4
        image_data = byte_stream[start:]
        # 保存图片数据到文件
        fp = f'{session}.png'
        print("抓到了一个图片", fp)
        # 检查是否为 PNG 图片
        if byte_stream.startswith(b'\x89PNG\r\n\x1a\n'):
            # 尝试解析 PNG 数据块
            print("这是一个PNG图片!!!")
            try:
                while byte_stream:
                    # 检查数据块长度
                    length = int(binascii.hexlify(byte_stream[4:8]), 16)
                    # 确保数据块完整
                    if len(byte_stream) >= 12 + length:
                        # 保存当前数据块
                        chunk = byte_stream[:12 + length]
                        # 更新字节流
                        byte_stream = byte_stream[12 + length:]
                        # 保存 PNG 图片数据到文件
                        with open(fp, 'ab') as f:
                            f.write(chunk)
                    else:
                        # 数据块不完整，等待更多数据
                        break
            except Exception as e:
                print(f"Error processing PNG: {e}")
        else:
            print("image_data:", image_data[0:20])
            with open(fp, 'wb') as f:
                f.write(image_data)


def process_packet(pkt):
    # print("Packet received:", pkt)
    if pkt.haslayer(TCP):
        session_id = f"{pkt[IP].src}:{pkt[TCP].sport} ===>>> {pkt[IP].dst}:{pkt[TCP].dport}"
        if pkt[TCP].flags & 0x02 or pkt[TCP].flags & 0x04:
            if session_id in tcp_streams:
                del tcp_streams[session_id]
            return
        if session_id not in tcp_streams:
            tcp_streams[session_id] = PacketList([pkt], name=session_id)
        else:
            tcp_streams[session_id].append(pkt)
        # 尝试重组 TCP 流
        reassemble_tcp_stream(session_id)


class PictureSniffSession(DefaultSession):
    def __init__(self):
        selfPictures = {}
        super(PictureSniffSession, self).__init__()

    def on_packet_received(self, pkt):
        if pkt.haslayer(TCP):
            stream = pkt.get_tcp_stream()
            if stream is not None:
                print("stream:", stream)
                data = b''.join(stream[1])
                print(data)


if __name__ == '__main__':
    # os.system("sudo sysctl -w net.ipv4.ip_forward=1")
    # session = PictureSniffSession()
    sniff(prn=process_packet, store=0, filter="tcp and ip src 192.168.1.57")
