import time
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
    parser.add_argument('--zero', help='sets the current position to 0', action='store_true')
    parser.add_argument('--stop', help='immediately stops the engine, moves it to the STOP state', action='store_true')
    parser.add_argument('--plot', help='plot speeds', action='store_true')
    parser.add_argument('--demo', help = 'move from 0 to 4500 with several speeds: 100, 500, 1000', action='store_true')
    parser.add_argument('--demo1', help = 'move from 0 to 4500 with several speeds: 100, 500, 1000', action='store_true')
    parser.add_argument('--demo2', help = 'move from 0 to 4500 with several speeds: 100, 1000', action='store_true')
    parser.add_argument('--demo3', help = 'move from 0 to 4500 with sin speed form', action='store_true')
        
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
        print(f"curr.position: {int.from_bytes(st[9:12], byteorder='little')}")
        print(f"{chr(956)}_curr.position: {int.from_bytes(st[13:15], byteorder='little')}")
        #print(f"enc.position: {int.from_bytes(st[15:22], byteorder='little')}")
        print(f"curr.speed: {int.from_bytes(st[23:26], byteorder='little', signed=True)}")
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



#def run_demo3(motor : USB_8SMC5) -> None:
#    '''
#    Demo contains next steps:
#        1. TODO
#    '''
#    import matplotlib.pyplot as plt
#    # ===== параметры движения =====
#    amplitude_rev = 1.0     # амплитуда в оборотах (±1 оборот)
#    period = 5.0            # секунд
#    dt = 0.01               # шаг обновления
#
#    # ===== параметры мотора =====
#    steps_per_rev = 200
#    microstep = 256
#
#    steps_per_rev_full = steps_per_rev * microstep
#
#    # амплитуда в микрошагов
#    A = amplitude_rev * steps_per_rev_full
#
#    omega = 2 * np.pi / period
#
#    # увеличить ускорение для плавности
#    motor.set_accel(65000)
#    motor.set_decel(65000)
#    motor.set_speed(50000)
#
#    t = 0.0
#    cur_pos = []
#    while t < 2:
#        # синус по позиции
#        pos = A*np.cos(omega * t)
#
#        motor.move(int(pos))
#
#        time.sleep(dt)
#        t += dt
#        cur_pos.append(int.from_bytes(motor.gets()[9:12], byteorder='little'))
#    plt.plot(np.linspace(1, len(cur_pos), len(cur_pos), endpoint=True), cur_pos)
#    motor.move(0)
#    plt.show()

    #================================
    #n = 10
    #t = np.linspace(0, 90, n, endpoint=True)
    #speeds = np.sin(np.pi*t/180.0)*1000
    ##exit(0)
    #plt_speeds = []
    #motor.set_accel(50000)
    #motor.set_decel(50000)
    #motor.set_speed(1000)
    #motor.move(0)
    #motor.wait_for_stop()
    #motor.move(-4500)
    #motor.wait_for_stop()
    #print("before start test")
    #motor.set_speed(speeds[0])
    #motor.move(4500)
    #for v in speeds:
    #    print(f"motor speed = {v}")
    #    motor.set_speed(v)
    #    time.sleep(1)
    #    plt_speeds.append(int.from_bytes(motor.gets()[23:26], byteorder='little', signed=True))
    ## TODO go back with different speeds!
    #motor.move(0)
    #plt_t = np.linspace(1, len(plt_speeds), len(plt_speeds))
    #plt.plot(plt_t, plt_speeds)
    #plt.show()


def run_demo3(motor : USB_8SMC5) -> None:
    '''
    Demo contains next steps:
        1. TODO
    '''
    import matplotlib.pyplot as plt
    Vmax = 10000
    period = 8.0
    dt = 0.1

    omega = 2 * np.pi / period

    # настройки движения
    motor.set_accel(60000)
    motor.set_decel(60000)

    t = 0

    direction = 1
    v = Vmax * np.sin(omega * t)
    print(v)
    motor.set_speed(int(abs(v)))
    motor.rigt()

    plt_speed = []
    while t < 2.0:
        v = Vmax * np.sin(omega * t)
    
        new_dir = 1 if v >= 0 else -1
    
        if new_dir != direction:
            if new_dir > 0:
                motor.rigt()
            else:
                motor.left()
    
            direction = new_dir
    
        speed = int(abs(v))
        plt_speed.append(speed)
        motor.set_speed(speed)
        t += dt
        time.sleep(dt)
    plt.plot(np.linspace(1, len(plt_speed), len(plt_speed)), plt_speed)
    plt.show()
    print(plt_speed)



if __name__ == "__main__":
    main()


    
