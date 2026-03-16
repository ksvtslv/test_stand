
import argparse

from USB_8SMC5 import USB_8SMC5

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='dummy',
            description='Program provides cli ineterface to run some commands...',
            epilog='This is epilog!')
    
    parser.add_argument('--move', help="move to postition")
    parser.add_argument('--movr', help='move to postition')
    parser.add_argument('--gser', help='get and print number of driver', action='store_true')
        
    args = parser.parse_args()

    motor_drive = USB_8SMC5()

    if args.move is not None:
        motor_drive.move(int(args.move))
    elif args.movr is not None:
        motor_drive.movr(int(args.movr))
    elif args.gser is not None:
        print(motor_drive.gser())
    
