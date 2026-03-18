from serial import Serial
import serial
from serial.tools import list_ports

class USB_8SMC5:
    def __init__(self):
        self.conn = None
        for prt, _, _ in sorted(list_ports.comports()):
            self.conn = Serial(port = prt,
                     baudrate      = 115200,
                     bytesize      = serial.EIGHTBITS,
                     parity        = serial.PARITY_NONE,
                     stopbits      = serial.STOPBITS_TWO,
                     timeout       = 0.3,
                     write_timeout = 0.3,)
            if self.gser() is not None:
                break
        if self.conn is None:
            raise StandaMotorsNotFound()
    
    def modbus_crc(self, msg:str) -> int:
        '''
        TODO use crcmod insetad!
        '''
        crc = 0xFFFF
        for n in range(len(msg)):
            crc ^= msg[n]
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    
    def gets(self):
        self.conn.write(str.encode('gets'))
        st = self.conn.read(54)

        crc = self.modbus_crc(st[4:52])
        ba = crc.to_bytes(2, byteorder='little')

        crc_matches = ba[0] == st[52] and ba[1] == st[53]

        if not crc_matches:
            raise CrcNotMatches()
        
        print(f"movement status: {st[5]}")
        #print(f"powerfull status: {st[6]}")
        #print(f"encoder status: {st[7]}")
        #print(f"wind status: {st[8]}")
        print(f"curr.position: {int.from_bytes(st[9:12], byteorder='little')}")
        print(f"{chr(956)}_curr.position: {int.from_bytes(st[13:15], byteorder='little')}")
        #print(f"enc.position: {int.from_bytes(st[15:22], byteorder='little')}")
        print(f"curr.speed: {int.from_bytes(st[23:26], byteorder='little', signed=True)}")
        print("===========================")

        return st



    def gser(self):
        self.conn.write(str.encode('gser'))
        serial_num_raw = self.conn.read(10)

        crc = self.modbus_crc(serial_num_raw[4:8])
        ba = crc.to_bytes(2, byteorder='little')

        crc_matches = ba[0] == serial_num_raw[8] and ba[1] == serial_num_raw[9]

        return int.from_bytes(serial_num_raw[4:8][::-1]) if crc_matches else None

        # TODO compare calculated crc with received crc from data frame!
        #print("CRC16/MODBUS: %02X %02X"%(ba[0], ba[1]))
        #print(f"original crc = {hex(serial_num_raw[8]), hex(serial_num_raw[9])}")
    
    def move(self, pos):
        # Fill data of frame
        data = bytearray(pos.to_bytes(4, "little", signed=True))
        data += int(0).to_bytes(2, "little")
        data += int(0).to_bytes(6, "little")

        # Calculate crc
        crc = self.modbus_crc(data).to_bytes(4, "little")[0:2]

        # Create packet
        cmd = bytearray(str.encode("move"))
        cmd += data
        cmd += crc

        # Send packet and get answer
        self.conn.write(cmd)
        ret = self.conn.read(4)

        # TODO Check answer for error!

        return ret

    def movr(self, pos):    
        # Fill data of frame
        data = bytearray(pos.to_bytes(4, "little", signed=True))
        data += int(0).to_bytes(2, "little")
        data += int(0).to_bytes(6, "little")

        # Calculate crc
        crc = self.modbus_crc(data).to_bytes(4, "little")[0:2]

        # Create packet
        cmd = bytearray(str.encode("movr"))
        cmd += data
        cmd += crc

        # Send packet and get answer
        self.conn.write(cmd)
        ret = self.conn.read(4)

        # TODO Check answer for error!

        return ret
    
    def zero(self):
        self.conn.write(str.encode('zero'))
        ret = self.conn.read(4)
        print(ret)

class StandaMotorsNotFound(Exception):
    """Raised when no one standa motors found."""
    pass

class CrcNotMatches(Exception):
    """Raised when calculated crc doesn't not match with crc from packet."""
    pass

def get_raw_str(raw_bytes):
    '''
    Helper function for debugging only
    '''
    raw_str = ""
    for i in range(len(raw_bytes)):
        raw_str += hex(raw_bytes[i])
        raw_str += " "
    return raw_str