
import argparse

from serial.serialutil import SerialException

from USB_8SMC5 import USB_8SMC5

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='main.py',
            description='Program provides cli ineterface to run some commands...',
            epilog='This is epilog!')
    
    parser.add_argument('--move', help="move to postition")
    parser.add_argument('--movr', help='shift by a set offset')
    parser.add_argument('--gser', help='return device serial number', action='store_true')
    parser.add_argument('--gets', help='return device state', action='store_true')
        
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
    elif args.gser:
        print(motor_drive.gser())
    elif args.gets:
        motor_drive.gets()
    else:
        parser.print_help()
    
