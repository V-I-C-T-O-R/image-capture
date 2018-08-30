# server端
import datetime
import os

import socket
import cv2
import threading
import struct
import numpy

local_dir = os.path.dirname(os.path.realpath(__file__)) + '/video/'


class Camera:
    def __init__(self, addr_port=["", 8880]):
        self.resolution = [640, 480]
        self.addr_port = addr_port
        self.src = 888 + 30  # 双方确定传输帧数，（888）为校验值
        self.interval = 0  # 图片播放时间间隔
        self.img_fps = 30  # 每秒传输多少帧数

    def Set_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def Socket_Connect(self):
        self.Set_socket()
        self.client.connect(self.addr_port)
        print("IP is %s:%d" % (self.addr_port[0], self.addr_port[1]))

    def RT_Image(self):

        self.name = self.addr_port[0] + " Camera"
        self.client.send(struct.pack("lhh", self.src, self.resolution[0], self.resolution[1]))
        file_name = local_dir + datetime.datetime.now().strftime('%Y-%m-%d') + '.avi'
        fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', '2')
        out = cv2.VideoWriter(file_name, fourcc, self.img_fps, (self.resolution[0], self.resolution[1]))
        while (1):
            info = struct.unpack("lhh", self.client.recv(12))
            buf_size = info[0]
            if buf_size:
                try:
                    self.buf = b""
                    temp_buf = self.buf
                    while (buf_size):
                        temp_buf = self.client.recv(buf_size)

                        buf_size -= len(temp_buf)
                        self.buf += temp_buf
                        data = numpy.fromstring(self.buf, dtype='uint8')
                        self.image = cv2.imdecode(data, 1)
                        out.write(self.image)
                        cv2.imshow(self.name, self.image)
                except Exception as e:
                    out.release()
                    return
                finally:
                    if (cv2.waitKey(10) == 27):  #
                        self.client.close()
                        cv2.destroyAllWindows()
                        break

    def Get_Data(self, interval):
        showThread = threading.Thread(target=self.RT_Image)
        showThread.start()


if __name__ == '__main__':
    camera = Camera()
    # camera.addr_port[0]=input("Please input IP:")
    camera.addr_port[0] = '127.0.0.1'
    camera.addr_port = tuple(camera.addr_port)
    camera.Socket_Connect()
    camera.Get_Data(camera.interval)
