import logging
from time import sleep
import yaml
from bluetooth import sha256, crc32
from bluetooth.serial import Serial


class Buletooth():
    def __init__(self, path="../../config.yaml"):
        self.path = path
        self._serial = Serial(path=path)
        self.random = ""


    def sendAT(self, at_cmd: str, times=5, endTag="OK"):
        for i in range(times):
            self._serial.send_at(at_cmd)
            s = True
            while s:
                line = self._serial.read_line()
                s = str(line, 'utf-8')
                logging.info(s)
                if endTag in s:
                    return True
                sleep(0.1)
        raise Exception("send at command failed: %s" % at_cmd)
        return False


    def sendHexData(self, data: str):
        self._serial.send_hex_data(data)
        line = "111"
        res = b''
        while line:
            if "NOTIFY" in str(line):
                res = line

            line = self._serial.read_line()
            logging.info(line)
            sleep(0.1)
        return res


    def connect(self):
        with open(self.path, 'r') as f:
            cfg = yaml.safe_load(f)
            mac = cfg['bluetooth']['bleMAC']
        self.sendAT("AT\r\n")
        self.sendAT("AT+BLEINIT=0\r\n")
        self.sendAT("AT+BLEINIT=1\r\n")
        self.sendAT("AT+BLECONN=0,\"%s\"\r\n" % mac)
        self.sendAT("AT+BLEENCRSP=0,1\r\n")
        self.sendAT("AT+BLEGATTCPRIMSRV=0\r\n")
        self.sendAT("AT+BLEGATTCCHAR=0,3\r\n")

        self.sendAT("AT+BLEGATTCWR=0,3,6,1,2\r\n", endTag=">")
        self.sendHexData("0100")
        self.sendAT("AT+BLEGATTCWR=0,3,7,1,2\r\n", endTag=">")
        self.sendHexData("0200")

        # 与充电桩交换随机数
        self.sendAT("AT+BLEGATTCWR=0,3,5,,20\r\n", endTag=">")
        response = self.sendHexData("55aa140001000000000000001122334429480c3a")
        cp_random = self.get_random(response)
        logging.info("cp_random = %s" % cp_random)

        auth_key = sha256.get_authkey(cp_random)
        logging.info("sha256加密结果:%s", auth_key)

        # new_auth_key = ""
        # while auth_key is not "":
        #     new_auth_key += auth_key[-2] + auth_key[-1]
        #     auth_key = auth_key[:-2]
        # auth_data = "55aa30000100000000000100"+new_auth_key
        auth_data = "55aa30000100000000000100" + auth_key
        crc_data = crc32.crc32c_hex(auth_data)
        auth_data += crc_data
        logging.info(auth_data)

        self.sendAT("AT+BLEGATTCWR=0,3,5,,48\r\n", endTag=">")
        response = self.sendHexData(auth_data)
        logging.info(response)


    def get_random(self, b: bytes) ->str:
        l = [(hex(i)[2:]).zfill(2) for i in list(b)]
        l = l[-10: -6]
        cp_random = "".join(l)
        return cp_random


def test_1():
    Buletooth("../config.yaml").connect()

