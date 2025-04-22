#from serial.tools import list_ports
from serial import Serial
import serial

#def connect_to_devce():
#    prt = None
#    for port, desc, _ in sorted(list_ports.comports()):
#        try:
#            prt = Serial(port          = port,
#                         baudrate      = 115200,
#                         bytesize      = serial.EIGHTBITS,
#                         parity        = serial.PARITY_NONE,
#                         stopbits      = serial.STOPBITS_TWO,
#                         timeout       = 0.3,
#                         write_timeout = 0.3,)
#        except Exception as e:
#            print(f"Can't connect to device {prt}, details: {e}")
#            continue
#        try:
#            test_connection(prt)
#            break
#        except Exception as e:
#            print(f"exception with testing the connection {prt}: {e}")
#    return prt

#def test_connection(prt):
#    pass

def modbus_crc(msg:str) -> int:
    '''
    TODO user crcmod insetad
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

def gser(prt):
    prt.write(str.encode('gser'))
    serial_num_raw = prt.read(10)
    
    ret = int.from_bytes(serial_num_raw[4:8][::-1])
    print(f"seial number {ret}")

    crc = modbus_crc(serial_num_raw[4:8])
    #print("0x%04X"%(crc))            

    ba = crc.to_bytes(2, byteorder='little')
    print("CRC16/MODBUS: %02X %02X"%(ba[0], ba[1]))
    print(f"original crc = {hex(serial_num_raw[8]), hex(serial_num_raw[9])}")

    return ret

def move(prt):
    pos = 500
    data = bytearray(pos.to_bytes(4, "little"))
    data += int(0).to_bytes(2, "little")
    crc = modbus_crc(data)
    le_crc = crc.to_bytes(2, byteorder='little')
    cmd = bytearray(str.encode("move"))
    cmd += data
    cmd += int(0).to_bytes(6, "little")
    cmd += le_crc
    
    print(len(cmd), cmd)
    prt.write(cmd)
    ret = prt.read(4)
    print(ret)
    
    return ret

if __name__ == "__main__":
    prt = Serial(port = "COM3",
                 baudrate      = 115200,
                 bytesize      = serial.EIGHTBITS,
                 parity        = serial.PARITY_NONE,
                 stopbits      = serial.STOPBITS_TWO,
                 timeout       = 0.3,
                 write_timeout = 0.3,)
    move(prt)
    

