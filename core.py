# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/1/21
@Software: PyCharm
@disc:
======================================="""
import binascii
import gzip
import mimetypes
import os
import zlib
from io import BytesIO

from scapy.all import sniff
from scapy.layers.inet import TCP, IP
from scapy.layers.l2 import Ether
from scapy.packet import Raw, ls
import threading

_columns = {
    "tcp_ack": {"width": 80},
    "tcp_seq": {"width": 80},
    "ip_src": {"width": 100},
    "tcp_sport": {"width": 50},
    "ip_dst": {"width": 100},
    "tcp_dport": {"width": 50},
    "ip_ttl": {"width": 50},
    "Accept-Ranges": {"width": 80},
    "Content-Type": {"width": 80},
    "Content-Length": {"width": 40},
    "Content-Encoding": {"width": 40},
    "Server": {"width": 80},
    "PKT Count": {"width": 30},
    "Teacher": {"width": 100}
}
_data = {
}


def packet_callback(pkt: Ether):
    global acks
    # pkt.show()
    # pkt.psdump()
    # pkt.pdfdump()
    # pkt.show2()
    print(pkt.summary())
    print("!" * 300)
    ls(pkt)
    print("=" * 300)
    # pkt_raw = raw(pkt)
    # print(pkt_raw)
    # print("*" * 300)
    # print(ls(pkt))
    # print("Packet received:", pkt)
    # if pkt.haslayer(HTTP):
    #     http_layer = pkt.getlayer(HTTP)
    #     print(" " * 10, "http_layer", http_layer)
    #     if http_layer.haslayer(Raw):
    #         raw_layer = pkt.getlayer(Raw)
    #         print(" " * 20, "raw_layer", raw_layer)
    #         if "image" in raw_layer.load:
    #             with open('image.jpg', 'wb') as f:
    #                 f.write(raw_layer.load)

    info = {"pkt": pkt}
    if pkt.haslayer(TCP) and pkt.haslayer(Raw):
        ip_layer = pkt.getlayer(IP)
        print("IP layer", ip_layer)
        if ip_layer:
            info["ip_src"] = ip_layer.src
            info["ip_dst"] = ip_layer.dst
            info["ip_ttl"] = ip_layer.ttl
        tcp_layer = pkt[TCP]
        print("TCP layer:", tcp_layer)
        if tcp_layer:
            info["tcp_seq"] = tcp_layer.seq
            info["tcp_ack"] = tcp_layer.ack
            info["tcp_sport"] = tcp_layer.sport
            info["tcp_dport"] = tcp_layer.dport
        raw_layer = pkt[Raw]
        print("Raw layer:", raw_layer)
        raw_data = raw_layer.load
        print(" " * 10, "Raw packet", raw_data)
        info["load"] = raw_data
        blocks = raw_data.split(b'\r\n')
        for block in blocks:
            print(block)
            try:
                block_str = block.decode("utf-8")
                for k in ["Content-Type", "Content-Length", "Accept-Encoding", "Accept-Language", "Connection",
                          "Upgrade-Insecure-Requests", "Server-Side-Effects", "Server", "Accept-Ranges", "Content",
                          "Content-Encoding"]:
                    target = f"{k}: "
                    if target in block_str:
                        # 特殊情况特殊处理
                        if k == "Content-Type" and "text/plain" in block_str:
                            info["Content-Type"] = "text/plain"
                        else:
                            info[k] = block_str.replace(target, "")

            except UnicodeDecodeError:
                pass

        if _data.__contains__(tcp_layer.ack):
            pass
        # if b'Content-Type: image' in raw_data:
        #     target_ack = ack
        #     # Extract the image data from the packet
        #
        else:
            _data.setdefault(tcp_layer.ack, {"PKTs": []})
            # if ack == target_ack:
            #     with open('image.jpg', 'wb+') as f:
            #         f.write(raw_data)
        _data[tcp_layer.ack]["PKTs"].append(info)
        save_data_content()

        print("^" * 300)

    # if pkt.haslayer(HTTP):
    #     http_layer = pkt[HTTP]
    #     print("HTTP layer:", http_layer)
    #     if http_layer:
    #         stream = http_layer.stream
    #         print("HTTP stream:", stream)
    #         response = pkt[HTTPResponse]
    #         print("HTTPResponse code:", response.code, response)
    #     # Do something with the response
    #


data_content_dir = "content"
if not os.path.exists(data_content_dir):
    os.mkdir(data_content_dir)


def save_data_content():
    for ack in _data.keys():
        pkts: list = _data[ack]["PKTs"]
        pkts = sorted(pkts, key=lambda item: item["tcp_seq"])
        seqs = []
        for pkt in pkts:
            if pkt["tcp_seq"] in seqs:
                print("Dropping...")
                pkts.remove(pkt)

        # Save the data content to a file
        if pkts[0].__contains__("Content-Type"):
            ext = mimetypes.guess_extension(pkts[0]["Content-Type"])
            if ext is None:
                if pkts[0]["Content-Type"] == "text/javascript":
                    ext = ".js"
            fp = os.path.join(data_content_dir, str(ack) + ext)
            with open(fp, "wb") as f:
                byte_stream = b''
                for i, pkt in enumerate(pkts):
                    PKT = pkt["pkt"]
                    raw_layer = PKT[Raw]
                    byte_stream += raw_layer.load
                start = byte_stream.find(b'\r\n\r\n') + 4
                byte_stream_content = byte_stream[start:]
                final_binary_content = byte_stream_content
                if pkts[0].__contains__("Content-Encoding"):
                    if pkts[0]["Content-Encoding"] == "gzip":
                        gzip_start = byte_stream.find(b"\x1f\x8b\x08")
                        byte_stream_content = byte_stream[gzip_start:]
                        try:
                            #     final_binary_content = gzip.decompress(byte_stream_content)
                            # gzip_data = binascii.a2b_base64(byte_stream_content)
                            gzip_data = byte_stream_content
                            # 解压gzip数据
                            with gzip.GzipFile(fileobj=BytesIO(gzip_data), mode='rb') as gzip_f:
                                png_data = gzip_f.read()
                                f.write(png_data)
                        except EOFError:
                            pass
                else:
                    f.write(final_binary_content)


class NetSniffer(threading.Thread):
    def __init__(self, filter_value: str):
        super(NetSniffer, self).__init__()
        self._stop_event = threading.Event()
        self._filter_value = filter_value

    def run(self):
        while not self._stop_event.is_set():
            # 执行线程的工作
            print("Sniffer is started...")
            sniff(prn=packet_callback, store=0, filter=self._filter_value)
        print("Sniffer is stopped.")

    def stop(self):
        print("Sniffer is stopping...")
        self._stop_event.set()
