from serial import Serial
import serial

def modbus_crc(msg:str) -> int:
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

def get_raw_str(raw_bytes):
    '''
    Helper function for debugging only
    '''
    raw_str = ""
    for i in range(len(raw_bytes)):
        raw_str += hex(raw_bytes[i])
        raw_str += " "
    return raw_str

def gser(prt):
    prt.write(str.encode('gser'))
    serial_num_raw = prt.read(10)

    ret = int.from_bytes(serial_num_raw[4:8][::-1])

    crc = modbus_crc(serial_num_raw[4:8])

    # TODO compare calculated crc with received crc from data frame!

    #ba = crc.to_bytes(2, byteorder='little')
    #print("CRC16/MODBUS: %02X %02X"%(ba[0], ba[1]))
    #print(f"original crc = {hex(serial_num_raw[8]), hex(serial_num_raw[9])}")

    return ret

def move(prt):
    
    # Fill data of frame
    pos = 0
    data = bytearray(pos.to_bytes(4, "little"))
    data += int(0).to_bytes(2, "little")
    data += int(0).to_bytes(6, "little")

    # Calculate crc
    crc = modbus_crc(data).to_bytes(4, "little")[0:2]

    # Create packet
    cmd = bytearray(str.encode("move"))
    cmd += data
    cmd += crc
    
    # Send packet and get answer
    prt.write(cmd)
    ret = prt.read(4)

    # TODO Check answer for error!
    
    return ret

def movr(prt):
    
    # Fill data of frame
    pos = 500
    data = bytearray(pos.to_bytes(4, "little"))
    data += int(0).to_bytes(2, "little")
    data += int(0).to_bytes(6, "little")

    # Calculate crc
    crc = modbus_crc(data).to_bytes(4, "little")[0:2]

    # Create packet
    cmd = bytearray(str.encode("movr"))
    cmd += data
    cmd += crc
    
    # Send packet and get answer
    prt.write(cmd)
    ret = prt.read(4)

    # TODO Check answer for error!
    
    return ret

if __name__ == "__main__":
    prt = Serial(port = "COM6",
                 baudrate      = 115200,
                 bytesize      = serial.EIGHTBITS,
                 parity        = serial.PARITY_NONE,
                 stopbits      = serial.STOPBITS_TWO,
                 timeout       = 0.3,
                 write_timeout = 0.3,)
    movr(prt)    
