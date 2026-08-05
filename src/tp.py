import time
import os
import sys
import libximc.highlevel as ximc




def test_status(axis: ximc.Axis) -> None:
    print("\nGet status")
    status = axis.get_status()
    print("Status.Ipwr: {}".format(status.Ipwr))
    print("Status.Upwr: {}".format(status.Upwr))
    print("Status.Iusb: {}".format(status.Iusb))
    print("Status.Flags: {}".format(status.Flags))


def test_get_position(axis: ximc.Axis) -> 'tuple':
    print("\nRead position")
    pos = axis.get_position()
    print("Position: {0} steps, {1} microsteps".format(pos.Position, pos.uPosition))
    return pos.Position, pos.uPosition


def test_left(axis: ximc.Axis) -> None:
    print("\nMoving left")
    axis.command_left()


def test_move(axis: ximc.Axis, distance: int, udistance: int) -> None:
    print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
    axis.command_move(distance, udistance)


def test_wait_for_stop(axis: ximc.Axis, interval: int) -> None:
    print("\nWaiting for stop...")
    axis.command_wait_for_stop(interval)


def test_get_speed(axis: ximc.Axis) -> int:
    print("\nGet speed")
    move_settings = axis.get_move_settings()
    return move_settings.Speed


def test_set_speed(axis: ximc.Axis, speed: int) -> None:
    print("\nSet speed")
    move_settings = axis.get_move_settings()
    print("The speed was equal to {0}. We will change it to {1}".format(move_settings.Speed, speed))
    move_settings.Speed = speed
    axis.set_move_settings(move_settings)


def test_set_microstep_mode_256(axis: ximc.Axis) -> None:
    print("\nSet microstep mode to 256")
    engine_settings = axis.get_engine_settings()

    # Change MicrostepMode parameter to MICROSTEP_MODE_FRAC_256
    # (use MICROSTEP_MODE_FRAC_128, MICROSTEP_MODE_FRAC_64 ... for other microstep modes)
    engine_settings.MicrostepMode = ximc.MicrostepMode.MICROSTEP_MODE_FRAC_256

    axis.set_engine_settings(engine_settings)

def cycling_motion(axis: ximc.Axis) -> None:
    borders = axis.get_edges_settings()
    try:
        while True:
            axis.command_move(borders.RightBorder, 0)
            axis.command_wait_for_stop(10)
            axis.command_move(borders.LeftBorder, 0)
            axis.command_wait_for_stop(10)
    except KeyboardInterrupt:
        print("\nStop cycling motion...")
        axis.command_stop()
    except Exception as e:
        print(f"\nStop cycling motion becasue of: {e}")
        axis.command_stop()


if __name__ == "__main__":
    try:
        print(f"Library version: {ximc.ximc_version()}")

        #enum_flags = ximc.EnumerateFlags.ENUMERATE_PROBE | ximc.EnumerateFlags.ENUMERATE_NETWORK
        flags = ximc.EnumerateFlags.ENUMERATE_NETWORK

        dptr_ip="192.168.1.10"
        ctrl_ip="192.168.1.2"
        hints = (f"addr=xi-net://{ctrl_ip}\n"f"adapter_addr={dptr_ip}")

        devices = ximc.enumerate_devices(flags, hints)
        print("Device count: {}".format(len(devices)))
        print("Found devices:\n", devices)

        open_name = None
        if len(sys.argv) > 1:
            open_name = sys.argv[1]
        elif len(devices) > 0:
            open_name = devices[0]["uri"]
        else:
            print("There no device to connect. Exit...")
            exit(0)

        axis = ximc.Axis(open_name)
        print("\nOpen device " + axis.uri)
        axis.open_device()

        test_status(axis)

        borders = axis.get_edges_settings()
        borders.LeftBorder = -2000
        borders.RightBorder = 67000
        axis.set_edges_settings(borders)
        borders = axis.get_edges_settings()
        print("\nBorder settings:")
        print(borders)

        movevement_settings = axis.get_move_settings()
        print("\nMovement settings:")
        print(movevement_settings)

        pos = axis.get_position()
        print("\nPoisition settings:")
        print(pos)

        print("\nCycling motion...")
        cycling_motion(axis)

    except Exception as e:
        print(f"Fatal error: {e}")
    
    print("\nClosing...")
    axis.close_device()