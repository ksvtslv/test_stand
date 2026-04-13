import time
import datetime
import argparse
import numpy as np

from serial.serialutil import SerialException

from USB_8SMC5 import USB_8SMC5

def main():
    parser = argparse.ArgumentParser(
            prog='main.py',
            description='Program provides cli ineterface to run some commands...',
            epilog='This is epilog!')
    
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
    parser.add_argument('--demo3', help = 'move from 0 to 4500 with sin speed form', action='store_true')
    #parser.add_argument('--demo4', help = 'move from 0 to 4500 with cos speed form', action='store_true')
        
    args = parser.parse_args()

    motor_drive = None
    try:
        motor_drive = USB_8SMC5()
    except SerialException as e:
        print(e)
        exit(1)

    if args.move is not None:
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
        print(f"BORDER_IS_ENCODER             = {data[5] & 0x1}")
        print(f"BORDER_STOP_LEFT              = {data[5] & 0x2}")
        print(f"BORDER_STOP_RIGHT             = {data[5] & 0x4}")
        print(f"BORDERS_SWAP_MISSET_DETECTION = {data[5] & 0x8}")
        print(f"LeftBorder                    = {int.from_bytes(data[7:11], byteorder='little', signed=True)}")
        print(f"uLeftBorder                   = {int.from_bytes(data[11:13], byteorder='little', signed=True)}")
        print(f"RightBorder                   = {int.from_bytes(data[13:17], byteorder='little', signed=True)}")
        print(f"uRitghBorder                  = {int.from_bytes(data[17:19], byteorder='little', signed=True)}")
    elif args.geng:
        data = motor_drive.geng()
        print(data)
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
    #elif args.demo4:
    #    run_demo4(motor_drive)
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



def run_demo3(motor : USB_8SMC5) -> None:
    '''
    Demo contains next steps:
        1. TODO
    '''
    #import matplotlib.pyplot as plt
    D = 10*100
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

    #plt_speed = []
    #plt_t = []
    dist = 0.0
    print("TEST STARTED")
    #t_start = datetime.datetime.now()
    #wait_for_dest = motor.wait_for_dest_right
    try:
        while True:
            v = Vmax * np.cos(omega * t)
            new_dir = 1 if v >= 0 else -1

            if new_dir != direction:
                if new_dir > 0:
                    motor.rigt()
                    #wait_for_dest = motor.wait_for_dest_right
                else:
                    motor.left()
                    #wait_for_dest = motor.wait_for_dest_left

                direction = new_dir

            cur_pos = int.from_bytes(motor.gets()[9:13], byteorder='little', signed = True)
            #print(f"_cur_pos_ = {cur_pos}")
            speed = int(abs(v))
            #plt_speed.append(v)
            motor.set_speed(speed)
            motor.wait_for_abs_speed(speed)
            #print(f"old_dist={dist}")
            dist += int(v)*dt
            if cur_pos > dist and direction == 1:
                dist = cur_pos
            if cur_pos < dist and direction == -1:
                dist = cur_pos
            #print(f"wait for {dist} with speed {int(v)}")
            if speed != 0:
                #wait_for_dest(dist, dt = 0.01)
                motor.wait_for_dest(dist, dt = 0.1)
            #time.sleep(dt)
            #plt_t.append(int(((datetime.datetime.now()-t_start).microseconds)/1000))
            t = (t + dt) % period
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Exception {e}")
        exit(1)

    print("TEST FINISHED")
    motor.set_speed(1000)
    motor.move(0)

    #plt.figure(1)
    #plt.plot(np.linspace(1, len(plt_speed), len(plt_speed)), plt_speed)
    #plt.title("speed")

    #plt.figure(2)
    #plt.plot(np.linspace(1, len(plt_t), len(plt_t)), plt_t)
    #plt.title("time")

    #plt.show()





#def run_demo4(motor : USB_8SMC5) -> None:
#    Vmax = 2400
#    period = 10.0
#    dt = 0.1
#    AngleMax = 10 #degrees
#
#    omega = 2 * np.pi / period
#
#    # настройки движения
#    motor.set_accel(60000)
#    motor.set_decel(60000)
#    motor.zero()
#
#    dest = []
#    speed = []
#
#    t = 0
#    d0 = AngleMax * np.sin(omega * t)
#    dest = []
#    print("TEST STARTED")
#    try:
#        while True:
#            d1 = int(AngleMax * 100 * np.sin(omega * (t + dt)))
#            d2 = int(AngleMax * 100 * np.sin(omega * (t + dt + dt)))
#            d3 = int(AngleMax * 100 * np.sin(omega * (t + dt + dt + dt)))
#            dest.append(d3)
#            v = (d3-d0)/dt
#            print(f"v={v}")
#            print(f"d1={d1}, d2={d2}, d3={d3}")
#            
#            motor.set_speed(abs(int(v)))
#            print(f"cur_pos = {int.from_bytes(motor.gets()[9:13], byteorder='little')}")
#            motor.move(d3)
#            cur_speed = int.from_bytes(motor.gets()[23:27], byteorder='little', signed=True)
#            print(f"cur_speed={cur_speed}")
#            #motor.wait_for_abs_speed(abs(int(v)))
#            motor.set_speed(abs(int(v)))
#            time.sleep(0.1)
#            if cur_speed != 0:
#                motor.wait_for_dest(int((d1+d2)/2))
#            d0 = int.from_bytes(motor.gets()[9:13], byteorder='little', signed = True)
#            t = np.arcsin(d0*0.01/AngleMax)/omega % period
#            print(f"t = {t}")
#    except KeyboardInterrupt:
#        pass
#    except Exception as e:
#        print("="*10)
#        print(f"Exception {e}")
#        print("="*10)
#
#    print("TEST FINISHED")
#    motor.set_speed(1000)
#    motor.move(0)
#    import matplotlib.pyplot as plt
#    plt.figure(figsize=(8, 5))
#    plt.plot(np.linspace(1, len(dest), len(dest)), dest)
#    #plt.scatter(np.linspace(1, len(dest), len(dest)), dest, color='red', s=50, label='Dots')
#    #plt.xlabel("Destination")
#    #plt.ylabel("Point number")
#    #plt.title("Destination")
#    #plt.legend()
#    #plt.grid(True, linestyle='--', alpha=0.6)
#
#    #plt.figure(figsize=(8, 5))
#    #plt.plot(np.linspace(1, len(speed), len(speed)), speed)
#    #plt.scatter(np.linspace(1, len(speed), len(speed)), speed, color='red', s=50, label='Dots')
#    #plt.xlabel("Speed")
#    #plt.ylabel("Point number")
#    #plt.title("Speed")
#    #plt.legend()
#    #plt.grid(True, linestyle='--', alpha=0.6)
#
#    plt.show()


#def run_demo4(motor : USB_8SMC5) -> None:
#    motor.set_accel(60000)
#    motor.set_decel(60000)
#    motor.zero()
#
#    motor.set_speed(50)
#    motor.rigt()
#    time.sleep(5)
#    motor.stop()


if __name__ == "__main__":
    main()


    
