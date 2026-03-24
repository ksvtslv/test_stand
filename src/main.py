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
    parser.add_argument('--gmov', help='return movement settings (speed, acceleration, threshold, etc.)', action='store_true')
    parser.add_argument('--gser', help='return device serial number', action='store_true')
    parser.add_argument('--gets', help='return device state', action='store_true')
    parser.add_argument('--zero', help='sets the current position to 0', action='store_true')
    parser.add_argument('--demo', help = 'move from 0 to 4500 with several speeds: 100, 500, 1000', action='store_true')
        
    args = parser.parse_args()

    motor_drive = None
    try:
        motor_drive = USB_8SMC5()
    except SerialException as e:
        print(e)
        exit(1)

    if args.move is not None:
        motor_drive.move(int(args.move))
        motor_drive.wait_for_stop()
    elif args.movr is not None:
        motor_drive.movr(int(args.movr))
    elif args.speed is not None:
        motor_drive.smov(speed = args.speed)
    elif args.gmov:
        motor_drive.gmov()
    elif args.gser:
        print(motor_drive.gser())
    elif args.gets:
        motor_drive.gets()
    elif args.zero:
        motor_drive.zero()
    elif args.demo:
        run_demo(motor_drive)
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
    motor.smov(speed = 100)
    motor.movr(281)
    motor.wait_for_dest(281)
    motor.smov(speed = 500)
    motor.movr(1405)
    motor.wait_for_dest(281+1405)
    motor.smov(speed = 1000)
    motor.movr(2814)
    motor.wait_for_dest(281+1405+2814)
    # TODO go back with different speeds!
    motor.smov(speed = 500)
    motor.move(0)


if __name__ == "__main__":
    main()


    
