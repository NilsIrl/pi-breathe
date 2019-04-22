#!/usr/bin/env python3

import serial
import struct

serial_conn = serial.Serial("/dev/serial0")


def enable_auto_send():
    serial_conn.write(b"\x68\x01\x40\x57")


def read():
    while True:
        head = serial_conn.read(2)
        if head == b"BM":
            len_all = struct.unpack("<h", serial_conn.read(2))[0]
            if len_all == 28:
                data = serial_conn.read(len_all)
                return struct.unpack("<hh", data[2:6])
            else:  # wrong length returned
                pass


if __name__ == "__main__":
    enable_auto_send()
    while True:
        print(read())
