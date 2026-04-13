from serial import Serial
import serial
from serial.tools import list_ports
import time

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
            if self.conn is None:
                continue
            if self.gser() is not None:
                break
        if self.conn is None:
            raise StandaMotorNotFound()



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



    def gmov(self):
        '''
        Read movement settings (speed, acceleration, threshold, etc.).
        '''
        self.conn.write(str.encode('gmov'))
        st = self.conn.read(30)

        crc = self.modbus_crc(st[4:28])
        ba = crc.to_bytes(2, byteorder='little')

        crc_matches = ba[0] == st[28] and ba[1] == st[29]

        if not crc_matches:
            raise CrcNotMatches()
        
        return st
    
    

    def geds(self):
        '''
        Read border and limit switches settings.
        '''
        self.conn.write(str.encode('geds'))
        data = self.conn.read(26)

        crc = self.modbus_crc(data[4:24])
        ba = crc.to_bytes(2, byteorder='little')

        crc_matches = ba[0] == data[24] and ba[1] == data[25]

        if not crc_matches:
            raise CrcNotMatches()
        
        return data



    def gsec(self):
        '''
        Read settings of step motor power control. Used with a stepper motor only.
        '''
        pass



    def geng(self):
        '''
        Read engine settings. This function reads the structure containing a set of useful motor settings stored
        in the controller’s memory. These settings specify motor shaft movement algorithm, list of limitations
        and rated characteristics.
        '''
        self.conn.write(str.encode('geng'))
        data = self.conn.read(34)

        crc = self.modbus_crc(data[4:32])
        ba = crc.to_bytes(2, byteorder='little')

        crc_matches = ba[0] == data[32] and ba[1] == data[33]

        if not crc_matches:
            raise CrcNotMatches()
        
        return data



    def gfbs(self):
        pass
    def gpwr(self):
        pass
    def gbrk(self):
        pass
    def gctl(self):
        pass
    def gjoy(self):
        pass
    def gctp(self):
        pass
    def ghom(self):
        pass
    def gpid(self):
        pass
    def gsni(self):
        pass
    def gsno(self):
        pass
    def gurt(self):
        pass
    def geio(self):
        pass
    def gemf(self):
        pass
    def gnmf(self):
        pass
    def gfwv(self):
        pass
    def geti(self):
        pass


    def gets(self):
        self.conn.write(str.encode('gets'))
        st = self.conn.read(54)

        crc = self.modbus_crc(st[4:52])
        ba = crc.to_bytes(2, byteorder='little')

        crc_matches = ba[0] == st[52] and ba[1] == st[53]

        if not crc_matches:
            raise CrcNotMatches()
        
        return st



    def gser(self):
        self.conn.write(str.encode('gser'))
        serial_num_raw = self.conn.read(10)
        if len(serial_num_raw) != 10:
            return None

        crc = self.modbus_crc(serial_num_raw[4:8])
        ba = crc.to_bytes(2, byteorder='little')

        crc_matches = ba[0] == serial_num_raw[8] and ba[1] == serial_num_raw[9]

        return int.from_bytes(serial_num_raw[4:8][::-1]) if crc_matches else None



    def smov(self,
             speed : int = 0,
             uSpeed : int = 0,
             accel : int = 0,
             decel : int = 0,
             antiplaySpeed : int = 0,
             uAntiplaySpeed : int = 0,
             moveFlags : int = 0):
        
        '''
        uint32_t Speed          Target speed(for stepper motor: steps/s, for DC:rpm). Range:0..100000.
        uint8_t  uSpeed         Target speed in micro step fractions/s.
        uint16_t accel          Motor shaft acceleration, steps/s^2(step per motor) or RPM/s (DC). Range: 1..65535.
        uint16_t decel          Motor shaft deceleration, steps/s^2(step per motor) or RPM/s (DC). Range: 1..65535.
        uint32_t antiplaySpeed  Speed in antiplay mode, full steps/s (steppermotor) orRPM(DC). Range: 0..100000.
        uint8_t  uAntiplaySpeed 
        uint8_t  moveFlags      0x1-RPM_DIV_1000 --  Indicates that the operating speed specified in the command is set in milliRPM.
                                Applicableonly for ENCODER feedbackmode and only for BLDCmotors.
        '''

        data =  bytearray(int(speed).to_bytes(4,  "little", signed=False)) # speed
        data += bytearray(int(uSpeed).to_bytes(1, "little", signed=False)) # uSpeed
        data += bytearray(int(accel).to_bytes(2, "little", signed=False)) # accel
        data += bytearray(int(decel).to_bytes(2, "little", signed=False)) # decel
        data += bytearray(int(antiplaySpeed).to_bytes(4, "little", signed=False)) # antiplaySpeed
        data += bytearray(int(uAntiplaySpeed).to_bytes(1, "little", signed=False)) # uantiplaySpeed
        data += bytearray(int(moveFlags).to_bytes(1, "little", signed=False)) # moveFlags
        data += bytearray(int(0).to_bytes(9, "little", signed=False)) # reserved

        # Calculate crc
        crc = self.modbus_crc(data).to_bytes(4, "little")[0:2]

        cmd = bytearray(str.encode("smov"))
        cmd += data
        cmd += crc

        # Send packet and get answer
        self.conn.write(cmd)
        ret = self.conn.read(4)

        # TODO Check answer for error!

        return ret




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



    def left(self):
        self.conn.write(str.encode('left'))
        ret = self.conn.read(4)
        print(ret)

    

    def rigt(self):
        self.conn.write(str.encode('rigt'))
        ret = self.conn.read(4)
        print(ret)
    


    def stop(self):
        self.conn.write(str.encode('stop'))
        ret = self.conn.read(4)
        print(ret)



    def zero(self):
        self.conn.write(str.encode('zero'))
        ret = self.conn.read(4)
        print(ret)




    def set_speed(self, speed : int):
        st = self.gmov()
        self.smov(speed = speed,
                  uSpeed = st[8],
                  accel = int.from_bytes(st[9:11], byteorder='little'),
                  decel = int.from_bytes(st[11:13], byteorder='little'),
                  antiplaySpeed = int.from_bytes(st[13:16], byteorder='little'),
                  uAntiplaySpeed = st[17],
                  moveFlags=st[17])




    def set_accel(self, accel : int):
        st = self.gmov()
        self.smov(speed = int.from_bytes(st[4:7], byteorder='little'),
                  uSpeed = st[8],
                  accel = accel,
                  decel = int.from_bytes(st[11:13], byteorder='little'),
                  antiplaySpeed = int.from_bytes(st[13:16], byteorder='little'),
                  uAntiplaySpeed = st[17],
                  moveFlags=st[17])




    def set_decel(self, decel : int):
        st = self.gmov()
        self.smov(speed = int.from_bytes(st[4:7], byteorder='little'),
                  uSpeed = st[8],
                  accel = int.from_bytes(st[9:11], byteorder='little'),
                  decel = decel,
                  antiplaySpeed = int.from_bytes(st[13:16], byteorder='little'),
                  uAntiplaySpeed = st[17],
                  moveFlags=st[17])




    def wait_for_stop(self, t = 0.1):
        st = self.gets()
        while st[5] & 0x80:
            time.sleep(t)
            st = self.gets()
    



    def wait_for_stop_log(self, t = 0.1):
        speed = []
        st = self.gets()
        while st[5] & 0x80:
            speed.append(abs(int.from_bytes(st[23:26], byteorder='little', signed=True)))
            time.sleep(t)
            st = self.gets()
        return speed



    def wait_for_dest(self, pos : int, dt = 0.1):
        cur_pos = int.from_bytes(self.gets()[9:13], byteorder='little', signed=True)
        ds1 = abs(cur_pos - pos)
        ds0 = ds1
        while ds0 >5:
            ds0 = ds1
            time.sleep(dt)
            cur_pos = int.from_bytes(self.gets()[9:13], byteorder='little')
            ds1 = abs(cur_pos - pos)
            if ds1 > ds0:
                break




    def wait_for_dest_right(self, pos : int, dt = 0.1):
        cur_pos = int.from_bytes(self.gets()[9:13], byteorder='little')
        while cur_pos < pos:
            time.sleep(dt)
            cur_pos = int.from_bytes(self.gets()[9:13], byteorder='little')
    


    def wait_for_dest_left(self, pos : int, dt = 0.1):
        cur_pos = int.from_bytes(self.gets()[9:13], byteorder='little')
        while cur_pos > pos:
            time.sleep(dt)
            cur_pos = int.from_bytes(self.gets()[9:13], byteorder='little')
    



    def wait_for_speed(self, target_speed : int, t = 0.1):
        cur_speed = int.from_bytes(self.gets()[23:26], byteorder='little', signed=True)
        while cur_speed != target_speed:
            time.sleep(t)
            cur_speed = int.from_bytes(self.gets()[23:26], byteorder='little', signed=True)
    



    def wait_for_abs_speed(self, target_speed : int, t = 0.1):
        cur_speed = abs(int.from_bytes(self.gets()[23:27], byteorder='little', signed=True))
        while cur_speed != target_speed:
            time.sleep(t)
            cur_speed = abs(int.from_bytes(self.gets()[23:27], byteorder='little', signed=True))




class StandaMotorNotFound(Exception):
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