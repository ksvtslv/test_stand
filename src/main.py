import time
import argparse

from serial.serialutil import SerialException

from USB_8SMC5 import USB_8SMC5

def main():
    parser = argparse.ArgumentParser(
            prog='main.py',
            description='Program provides cli ineterface to run some commands...',
            epilog='This is epilog!')
    
    parser.add_argument('--move', help="move to postition")
    parser.add_argument('--movr', help='shift by a set offset')
    parser.add_argument('--speed', help="set speed")
    parser.add_argument('--accel', help="set acceleration")
    parser.add_argument('--decel', help="set deceleration")
    parser.add_argument('--gmov', help='return movement settings (speed, acceleration, threshold, etc.)', action='store_true')
    parser.add_argument('--gser', help='return device serial number', action='store_true')
    parser.add_argument('--gets', help='return device state', action='store_true')
    parser.add_argument('--zero', help='sets the current position to 0', action='store_true')
    parser.add_argument('--demo', help = 'move from 0 to 4500 with several speeds: 100, 500, 1000', action='store_true')
    parser.add_argument('--demo1', help = 'move from 0 to 4500 with several speeds: 100, 500, 1000', action='store_true')
    parser.add_argument('--demo2', help = 'move from 0 to 4500 with several speeds: 100, 1000', action='store_true')
        
    args = parser.parse_args()

    motor_drive = None
    try:
        motor_drive = USB_8SMC5()
    except SerialException as e:
        print(e)
        exit(1)

    if args.move is not None:
        motor_drive.move(int(args.move))
    elif args.movr is not None:
        motor_drive.movr(int(args.movr))
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
        print(f"accel: {int.from_bytes(st[9:10], byteorder='little')}")
        print(f"decel: {int.from_bytes(st[11:12], byteorder='little')}")
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
        print(f"curr.position: {int.from_bytes(st[9:12], byteorder='little')}")
        print(f"{chr(956)}_curr.position: {int.from_bytes(st[13:15], byteorder='little')}")
        #print(f"enc.position: {int.from_bytes(st[15:22], byteorder='little')}")
        print(f"curr.speed: {int.from_bytes(st[23:26], byteorder='little', signed=True)}")
    elif args.zero:
        motor_drive.zero()
    elif args.demo:
        run_demo(motor_drive)
    elif args.demo1:
        run_demo1(motor_drive)
    elif args.demo2:
        run_demo2(motor_drive)
    else:
        parser.print_help()

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
    motor.wait_for_dest(400)
    print("moved to 400")
    motor.set_speed(1000)
    print("speed is 1000")
    motor.wait_for_dest(4500)
    print("moved to 4500")
    motor.move(0)


if __name__ == "__main__":
    main()


    
