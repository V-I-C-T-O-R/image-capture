# client端
import os
import socket
import threading
import struct
import time
import cv2
import numpy


class Client:
    def __init__(self, S_addr_port=("", 8880)):
        self.resolution = (640, 480)  # 分辨率
        self.img_fps = 30  # 每秒传输多少帧数
        self.addr_port = S_addr_port
        self.Set_Socket(self.addr_port)

    # 设置套接字
    def Set_Socket(self, S_addr_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口可复用
        self.server.bind(S_addr_port)
        self.server.listen(5)

def check_option(object, client):
    # 按格式解码，确定帧数和分辨率
    info = struct.unpack('lhh', client.recv(12))
    if info[0] > 888:
        object.img_fps = int(info[0]) - 888  # 获取帧数
        object.resolution = list(object.resolution)
        # 获取分辨率
        object.resolution[0] = info[1]
        object.resolution[1] = info[2]
        object.resolution = tuple(object.resolution)
        return 1
    else:
        return 0


def RT_Image(object, client, D_addr):
    if (check_option(object, client) == 0):
        return
    camera = cv2.VideoCapture(0)
    img_param = [int(cv2.IMWRITE_PNG_COMPRESSION), object.img_fps]
    while (1):
        time.sleep(0.02)
        _, object.img = camera.read()
        object.img = cv2.resize(object.img, object.resolution)
        _, img_encode = cv2.imencode('.jpg', object.img, img_param)
        img_code = numpy.array(img_encode)
        object.img_data = img_code.tostring()
        try:
            # 按照相应的格式进行打包发送图片
            client.send(
                struct.pack("lhh", len(object.img_data), object.resolution[0], object.resolution[1]) + object.img_data)
        except:
            camera.release()
            return


if __name__ == '__main__':
    camera = Client()
    while (1):
        client, D_addr = camera.server.accept()
        print('客户端:', D_addr, '接入')
        clientThread = threading.Thread(None, target=RT_Image, args=(camera, client, D_addr))
        clientThread.start()
