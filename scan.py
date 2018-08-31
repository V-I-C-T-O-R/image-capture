import _thread
import datetime
import os
import socket
import sys
import time

import threadpool

socket.setdefaulttimeout(1)
lock = _thread.allocate_lock()
local_dir = os.path.dirname(os.path.realpath(__file__)) + '/record/'
day = datetime.datetime.now().strftime('%Y-%m-%d')

def get_spec_port(func):
    def handle(file,content):
        attrs = str(content).split('-')
        ip = attrs[0].split(':')[1]
        port = int(attrs[1].split(':')[1])
        if port == 8088 and 'open' in file:
            spec_file = local_dir+day+'-spec.txt'
            func(spec_file,content)
        func(file,content)
    return handle

@get_spec_port
def write2file(file, content):
    lock.acquire()
    with open(file, 'a+') as f:
        f.write(content + '\n')
    lock.release()

def socket_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((ip, port))
        if result == 0:
            print('ip', ip, '端口', port, '开放')
            write2file(file=local_dir + ip + '-' + day + '-' + 'open.txt', content='ip:' + ip + '-端口:' + str(port))
        else:
            write2file(file=local_dir + ip + '-' + day + '-' + 'close.txt', content='ip:' + ip + '-端口:' + str(port))
    except:
        print('ip', ip, '端口', port, '扫描异常')
    finally:
        s.close()


def get_ip_port(port_list, ip):
    for i in range(22, 20000):
        port_list.append(([ip, int(i)], None))


def ip_scan(pool, port_list):
    reqs = threadpool.makeRequests(socket_port, port_list)
    [pool.putRequest(req) for req in reqs]
    pool.wait()


def num2ip(num):
    ip = ['', '', '', '']
    ip[3] = (num & 0xff)
    ip[2] = (num & 0xff00) >> 8
    ip[1] = (num & 0xff0000) >> 16
    ip[0] = (num & 0xff000000) >> 24
    return '%s.%s.%s.%s' % (ip[0], ip[1], ip[2], ip[3])


def ip2num(ip):
    lp = [int(x) for x in ip.split('.')]
    return lp[0] << 24 | lp[1] << 16 | lp[2] << 8 | lp[3]


def num2ip(num):
    ip = ['', '', '', '']
    ip[3] = (num & 0xff)
    ip[2] = (num & 0xff00) >> 8
    ip[1] = (num & 0xff0000) >> 16
    ip[0] = (num & 0xff000000) >> 24
    return '%s.%s.%s.%s' % (ip[0], ip[1], ip[2], ip[3])


def iprange(ip1, ip2):
    num1 = ip2num(ip1)
    num2 = ip2num(ip2)
    tmp = num2 - num1
    if tmp < 0:
        return None
    else:
        return num1, num2, tmp


def run(pool):
    if len(sys.argv) < 3:
        print('Usage:python3 scan.py startip endip')
        sys.exit()
    res = ()
    startip = sys.argv[1]
    endip = sys.argv[2]
    res = iprange(startip, endip)
    if not res:
        print
        'endip must be bigger than startone'
        sys.exit()
    elif res[2] == 0:
        port_list = []
        get_ip_port(port_list, startip)
        ip_scan(pool, port_list)
    else:
        port_list = []
        for x in range(int(res[2]) + 1):
            startipnum = ip2num(startip)
            startipnum = startipnum + x
            ip = num2ip(startipnum)
            get_ip_port(port_list, ip)
        ip_scan(pool, port_list)


if __name__ == '__main__':
    start_time = time.time()
    pool = threadpool.ThreadPool(50)
    run(pool)
    print('扫描端口完成，总共用时 ：%.2f' % (time.time() - start_time))
