# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/1/21
@Software: PyCharm
@disc:
======================================="""
import mimetypes
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk

from scapy.all import sniff
from scapy.layers.inet import TCP, IP
from scapy.layers.l2 import Ether
from scapy.packet import Raw, ls

_columns = {
    "ack": {
        "width": 60
    },
    "tcp_seq": {"width": 80},
    "ip_src": {"width": 100},
    "tcp_sport": {"width": 50},
    "ip_dst": {"width": 100},
    "tcp_dport": {"width": 50},
    "ip_ttl": {"width": 50},
    "Accept-Ranges": {"width": 80},
    "Content-Type": {"width": 80},
    "Content-Length": {"width": 40},
    "Server": {"width": 80},
    "PKT Count": {"width": 30},
    "Teacher": {"width": 100}
}
_data = {
}

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
            fp = os.path.join(data_content_dir, str(ack) + ext)
            with open(fp, "wb") as f:
                for i, pkt in enumerate(pkts):
                    PKT = pkt["pkt"]
                    raw_layer = PKT[Raw]
                    raw_data = raw_layer.load
                    if i == 0:
                        blocks = raw_data.split(b'\r\n\r\n')
                        image_data = blocks[1]
                        f.write(image_data)
                    else:
                        f.write(raw_data)


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
        blocks = raw_data.split(b'\r\n')
        for block in blocks:
            print(block)
            try:
                block_str = block.decode("utf-8")
                for k in ["Content-Type", "Content-Length", "Accept-Encoding", "Accept-Language", "Connection",
                          "Upgrade-Insecure-Requests", "Server-Side-Effects", "Server", "Accept-Ranges", "Content"]:
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


class DataTable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        _column_index = list(_columns.keys())
        print(_column_index)
        self.tree = ttk.Treeview(self, columns=_column_index, show="tree")
        self.tree.heading("#0", text="HTTP请求/TCP请求包")
        for column in _columns.keys():
            self.tree.heading(column, text=column)
            columnInfo = _columns[column]
            self.tree.column(column, width=columnInfo["width"])

        # 初始数据
        self.update_data()

        self.tree.pack(expand=True, fill="both")

    def update_data(self):
        # 模拟更新数据，可以替换成你的数据更新逻辑

        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 插入新数据
        for class_name, class_info in _data.items():
            pkts = class_info["PKTs"]
            class_node = self.tree.insert("", "end", text=class_name, values=(
                pkts.__len__(),
                class_info.get("Teacher", "")
            ), open=True)

            for student in pkts:
                _values = []
                for c in _columns.keys():
                    _values.append(student.get(c, ""))
                self.tree.insert(class_node, "end", values=_values)

        # 每分钟调用一次更新数据函数
        self.after(100, self.update_data)


def my_sniff(filter: str):
    if filter:
        sniff(prn=packet_callback, store=0, filter=filter)
    else:
        sniff(prn=packet_callback, store=0)


if __name__ == "__main__":
    print(sys.argv)
    if sys.argv.__len__() > 1:
        th = threading.Thread(target=my_sniff, args=(sys.argv[1],))
    else:
        th = threading.Thread(target=my_sniff, args=(None,))
    th.start()
    # 创建主窗口
    root = tk.Tk()
    root.title("SuperSniffer")

    # 创建 DataTable 实例
    data_table = DataTable(root)
    data_table.pack(expand=True, fill="both")

    # 运行主循环
    root.mainloop()
