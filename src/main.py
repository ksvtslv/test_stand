import time
import datetime
import threading
import argparse
import numpy as np

from serial.serialutil import SerialException

from USB_8SMC5 import USB_8SMC5

def main():
    parser = argparse.ArgumentParser(
            prog='main.py',
            description='Program provides cli ineterface to run some commands...',
            epilog='This is epilog!')
    
    parser.add_argument('--list', help="enumerate all connected drives", action='store_true')
    parser.add_argument('--motor', help="use this motor to run command")
    parser.add_argument('--move', help="move to postition")
    parser.add_argument('--movr', help='shift by a set offset')
    parser.add_argument('--left', help='start moving left', action='store_true')
    parser.add_argument('--rigt', help='start moving right', action='store_true')
    parser.add_argument('--speed', help="set speed")
    parser.add_argument('--accel', help="set acceleration")
    parser.add_argument('--decel', help="set deceleration")
    parser.add_argument('--gmov', help='return movement settings (speed, acceleration, threshold, etc.)', action='store_true')
    parser.add_argument('--gser', help='return device serial number', action='store_true')
    parser.add_argument('--gets', help='return device state', action='store_true')
    parser.add_argument('--geds', help='return border and limit switches settings', action='store_true')
    parser.add_argument('--geng', help='return engine settings', action='store_true')
    parser.add_argument('--zero', help='sets the current position to 0', action='store_true')
    parser.add_argument('--stop', help='immediately stops the engine, moves it to the STOP state', action='store_true')
    parser.add_argument('--plot', help='plot speeds', action='store_true')
    parser.add_argument('--demo', help = 'move from 0 to 4500 with several speeds: 100, 500, 1000', action='store_true')
    parser.add_argument('--demo1', help = 'move from 0 to 4500 with several speeds: 100, 500, 1000', action='store_true')
    parser.add_argument('--demo2', help = 'move from 0 to 4500 with several speeds: 100, 1000', action='store_true')
    parser.add_argument('--demo3', help = 'sin speed form demo', action='store_true')
    parser.add_argument('--demo4', help = 'two-axis movement demo', action='store_true')
    parser.add_argument('--demo5', help = 'two-axis sin speed form demo', action='store_true')
        
    args = parser.parse_args()

    
    motor_list = None
    try:
        motor_list = get_motor_list()
    except SerialException as e:
        print(e)
        exit(1)
    
    motor_drive = None
    if args.motor is not None:
        motor_drive = motor_list[args.motor]
    else:
        motor_drive = motor_list[next(iter(motor_list))]

    if args.list:
        for k in list(motor_list.keys()):
            print(k)
    elif args.move is not None:
        motor_drive.move(int(args.move))
        if args.plot:
            import matplotlib.pyplot as plt
            speed = motor_drive.wait_for_stop_log()
            t = np.linspace(0, np.pi/2, len(speed), endpoint=True)
            plt.plot(t, speed)
            plt.show()
    elif args.movr is not None:
        motor_drive.movr(int(args.movr))
    elif args.left:
        motor_drive.left()
    elif args.rigt:
        motor_drive.rigt()
    elif args.speed is not None:
        motor_drive.set_speed(args.speed)
    elif args.accel is not None:
        motor_drive.set_accel(args.accel)
    elif args.decel is not None:
        motor_drive.set_decel(args.decel)
    elif args.gmov:
        st = motor_drive.gmov()
        print(f"speed: {int.from_bytes(st[4:7], byteorder='little')}")
        print(f"uSpeed: {st[8]}")
        print(f"accel: {int.from_bytes(st[9:11], byteorder='little', signed=False)}")
        print(f"decel: {int.from_bytes(st[11:13], byteorder='little', signed=False)}")
        print(f"antiplaySpeed: {int.from_bytes(st[13:16], byteorder='little')}")
        print(f"uAntiplaySpeed: {st[17]}")
        print(f"moveFlags: {st[18]}")
    elif args.gser:
        print(motor_drive.gser())
    elif args.gets:
        st = motor_drive.gets()
        print(f"movement status: {st[5]}")
        #print(f"powerfull status: {st[6]}")
        #print(f"encoder status: {st[7]}")
        #print(f"wind status: {st[8]}")
        print(f"curr.position: {int.from_bytes(st[9:13], byteorder='little')}")
        print(f"{chr(956)}_curr.position: {int.from_bytes(st[13:15], byteorder='little')}")
        #print(f"enc.position: {int.from_bytes(st[15:22], byteorder='little')}")
        print(f"curr.speed: {int.from_bytes(st[23:26], byteorder='little', signed=True)}")
    elif args.geds:
        data = motor_drive.geds()
        print(f"BORDER_IS_ENCODER             = {data[4] & 0x1}")
        print(f"BORDER_STOP_LEFT              = {data[4] & 0x2}")
        print(f"BORDER_STOP_RIGHT             = {data[4] & 0x4}")
        print(f"BORDERS_SWAP_MISSET_DETECTION = {data[4] & 0x8}")
        print(f"ENDER_SWAP                    = {data[5] & 0x1}")
        print(f"ENDER_SW1_ACTIVE_LOW          = {data[5] & 0x2}")
        print(f"ENDER_SW2_ACTIVE_LOW          = {data[5] & 0x4}")
        print(f"LeftBorder                    = {int.from_bytes(data[6:10], byteorder='little', signed=True)}")
        print(f"uLeftBorder                   = {int.from_bytes(data[10:12], byteorder='little', signed=True)}")
        print(f"RightBorder                   = {int.from_bytes(data[12:16], byteorder='little', signed=True)}")
        print(f"uRitghBorder                  = {int.from_bytes(data[16:18], byteorder='little', signed=True)}")
    elif args.geng:
        data = motor_drive.geng()
        print(f"NomVoltage: {int.from_bytes(data[4:6], byteorder='little', signed=False)} mV")
        print(f"NomCurrent: {int.from_bytes(data[6:8], byteorder='little', signed=False)} mA")
        print(f"NomSpeed: {int.from_bytes(data[8:12], byteorder='little', signed=False)}")
        print(f"uNomSpeed: {data[12]}")
        engine_flags = int.from_bytes(data[13:15], byteorder='little', signed=False)
        print(f"ENGINE_REVERSE:        {'no' if engine_flags & 0x1 == 0 else 'yes'}")
        print(f"ENGINE_CURRENT_AS_RMS: {'no' if engine_flags & 0x2 == 0 else 'yes'}")
        print(f"ENGINE_MAX_SPEED:      {'no' if engine_flags & 0x4 == 0 else 'yes'}")
        print(f"ENGINE_ANTIPLAY:       {'no' if engine_flags & 0x8 == 0 else 'yes'}")
        print(f"ENGINE_ACCEL_ON:       {'no' if engine_flags & 0x10 == 0 else 'yes'}")
        print(f"ENGINE_LIMIT_VOLT:     {'no' if engine_flags & 0x20 == 0 else 'yes'}")
        print(f"ENGINE_LIMIT_CURR:     {'no' if engine_flags & 0x40 == 0 else 'yes'}")
        print(f"ENGINE_LIMIT_RPM:      {'no' if engine_flags & 0x80 == 0 else 'yes'}")
        print(f"Antiplay: {int.from_bytes(data[15:17], byteorder='little', signed=True)}")
        microstep_mode = data[17]
        print(f"microstep_mode: {microstep_mode}")
        print(f"MICROSTEP_MODE_FULL:     {'no' if microstep_mode & 0x1 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_2:   {'no' if microstep_mode & 0x2 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_4:   {'no' if microstep_mode & 0x4 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_8:   {'no' if microstep_mode & 0x8 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_16:  {'no' if microstep_mode & 0x10 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_32:  {'no' if microstep_mode & 0x20 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_64:  {'no' if microstep_mode & 0x40 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_128: {'no' if microstep_mode & 0x80 == 0 else 'yes'}")
        print(f"MICROSTEP_MODE_FRAC_256: {'no' if microstep_mode & 0x0 == 0 else 'yes'}")
        print(f"StepsPerRev: {int.from_bytes(data[18:20], byteorder='little', signed=False)}")
    elif args.zero:
        motor_drive.zero()
    elif args.stop:
        motor_drive.stop()
    elif args.demo:
        run_demo(motor_drive)
    elif args.demo1:
        run_demo1(motor_drive)
    elif args.demo2:
        run_demo2(motor_drive)
    elif args.demo3:
        run_demo3(motor_drive)
    elif args.demo4:
        run_demo4(motor_list)
    elif args.demo5:
        run_demo5(motor_list)
    else:
        parser.print_help()

def get_motor_list():
    device_list = {}
    exclude_list = []
    try:
        while True:
            d = USB_8SMC5(exclude_list)
            if d.port_name is None:
                break
            exclude_list.append(d.port_name)
            device_list[str(d.gser())] = d
    except Exception as e:
        print(f"Listing COM ports failed with error: {e}")
        pass
    return device_list

def get_first_two_motors(): 
    device_list = []
    exclude_list = []
    try:
        while True:
            d = USB_8SMC5(exclude_list)
            if d.port_name is None:
                break
            exclude_list.append(d.port_name)
            device_list.append(d)
    except Exception as e:
        print(f"Listing COM ports failed with error: {e}")
        pass
    return device_list[0], device_list[1]

class DummyStopEvent:
    def is_set(self):
        return False

def run_demo(motor : USB_8SMC5) -> None:
    '''
    Demo contains next steps:
        1. Moving to 0
        2. Setting speed to 100
        3. Moving from 0 to 281
        4. Setting speed to 500
        5. Moving from 281 to 1405+281=1686
        6. Settings speed to 1000
        7. Moving from 1686 to 1686+2814=4500
        8. Stop
        9. Moving back with reverse repeat steps from 7 to 1
        10. Stop (if need)
    '''
    motor.move(0)
    motor.wait_for_stop()
    motor.set_speed(100)
    motor.movr(281)
    motor.wait_for_dest(281, t = 0.01)
    motor.set_speed(500)
    motor.movr(1405)
    motor.wait_for_dest(281+1405, t = 0.01)
    motor.set_speed(1000)
    motor.movr(2814)
    motor.wait_for_dest(281+1405+2814, t = 0.01)
    # TODO go back with different speeds!
    motor.move(0)

def run_demo1(motor : USB_8SMC5) -> None:
    '''
    Demo contains next steps:
        1. Moving to 0
        2. Setting speed to 100
        3. Moving from 0 to 281
        4. Setting speed to 500
        5. Moving from 281 to 1405+281=1686
        6. Settings speed to 1000
        7. Moving from 1686 to 1686+2814=4500
        8. Stop
        9. Moving back with reverse repeat steps from 7 to 1
        10. Stop (if need)
    '''
    motor.move(0)
    print("moved to 0")
    motor.wait_for_stop()
    motor.set_speed(100)
    print("speed is 100")
    motor.move(4500)
    motor.wait_for_dest(281)
    print("moved to 281")
    motor.set_speed(500)
    print("speed is 500")
    motor.wait_for_dest(281+1405)
    print("moved to 281+1405")
    motor.set_speed(1000)
    print("speed is 1000")
    motor.wait_for_dest(281+1405+2814)
    print("moved to 281+1405+2814")
    # TODO go back with different speeds!
    motor.move(0)

def run_demo2(motor : USB_8SMC5) -> None:
    '''
    Demo contains next steps:
        1. TODO
    '''
    motor.move(0)
    motor.wait_for_stop()
    motor.set_speed(100)
    motor.move(4500)
    motor.wait_for_dest(150)
    motor.set_speed(200)
    motor.wait_for_dest(150 + 150*2)
    motor.set_speed(400)
    motor.wait_for_dest(150*2 + 150*4)
    motor.set_speed(800)
    motor.wait_for_dest(150*4 + 150*8)
    motor.set_speed(1600)
    motor.wait_for_dest(150*8 + 150*16)
    time.sleep(1)
    # TODO go back with different speeds!
    motor.move(0)



def run_demo3(motor : USB_8SMC5, stop_event = None) -> None:
    '''
    Demo contains next steps:
        1. TODO
    '''
    D = 10 * 100
    period = 10.0
    dt = 0.1

    Vmax = D * 2 * np.pi / period

    omega = 2 * np.pi / period

    # настройки движения
    motor.set_accel(60000)
    motor.set_decel(60000)
    motor.zero()

    t = 0

    v = Vmax * np.cos(omega * t)
    motor.set_speed(int(abs(v)))
    direction = 1 if v >= 0 else -1
    if direction == 1:
        motor.rigt()
    else:motor.left()

    dist = 0.0
    print("TEST STARTED")
    t_start = datetime.datetime.now()
    time_l = []
    pos_l = []
    if stop_event is None:
        stop_event = DummyStopEvent()
    try:
        while not stop_event.is_set():
            v = Vmax * np.cos(omega * t)
            new_dir = 1 if v >= 0 else -1

            if new_dir != direction:
                if new_dir > 0:
                    motor.rigt()
                else:
                    motor.left()

                direction = new_dir

            cur_pos = int.from_bytes(motor.gets()[9:13], byteorder='little', signed = True)
            speed = int(abs(v))
            motor.set_speed(speed)
            #motor.wait_for_abs_speed(speed)
            dist += int(v)*dt
            if cur_pos > dist and direction == 1:
                dist = cur_pos
            if cur_pos < dist and direction == -1:
                dist = cur_pos
            if speed != 0:
                motor.wait_for_dest(dist, dt = 0.1)
            pos_l.append(int.from_bytes(motor.gets()[9:13], byteorder='little', signed=True))
            tnow = datetime.datetime.now()
            time_l.append((tnow-t_start).seconds*1000 + (tnow-t_start).microseconds/1000)
            t = (t + dt) % period
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Exception {e}")
        exit(1)

    print("TEST FINISHED")
    motor.set_speed(1000)
    motor.move(0)

    #import matplotlib.pyplot as plt
    #plt.figure(1)
    #plt.plot(np.linspace(1, len(pos_l), len(pos_l)), pos_l)
    #plt.scatter(np.linspace(1, len(pos_l), len(pos_l)), pos_l, color='red', s=50, label='Dots')
    #plt.title("position")
#
    #plt.figure(2)
    #plt.plot(np.linspace(1, len(time_l), len(time_l)), time_l)
    #plt.scatter(np.linspace(1, len(time_l), len(time_l)), time_l, color='red', s=50, label='Dots')
    #plt.title("time")
#
    #plt.show()

def run_demo4(motor_list) -> None:
    '''
    Demo contains next steps:
        1. TODO
    '''
    first_motor = list(motor_list.values())[0]
    second_motor = list(motor_list.values())[1]
    first_motor.set_speed(500)
    second_motor.set_speed(500)
    first_motor.move(4500)
    second_motor.move(4500)
    first_motor.wait_for_stop()
    second_motor.wait_for_stop()
    
    first_motor.move(0)
    second_motor.move(0)
    first_motor.wait_for_stop()
    second_motor.wait_for_stop()

def run_demo5(motor_list) -> None:
    '''
    Demo contains next steps:
        1. TODO
    '''
    first_motor = list(motor_list.values())[0]
    second_motor = list(motor_list.values())[1]

    stop_event = threading.Event()
    
    thread = threading.Thread(target=run_demo3, args=(first_motor,stop_event,))
    thread.start()

    run_demo3(second_motor)

    stop_event.set()

    thread.join()



if __name__ == "__main__":
    main()


    
