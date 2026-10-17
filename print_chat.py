#!/usr/bin/env python3
import sys
import time
import serial
from PIL import Image, ImageOps

PORT = "/dev/rfcomm0"
WIDTH = 384

def make_job(path):
    img = Image.open(path).convert("L")
    height = max(8, round(img.height * WIDTH / img.width))
    img = img.resize((WIDTH, height), Image.Resampling.LANCZOS)
    img = img.convert("1", dither=Image.Dither.FLOYDSTEINBERG)

    # Pad to a multiple of 8 rows.
    padded_height = ((height + 7) // 8) * 8
    if padded_height != height:
        canvas = Image.new("1", (WIDTH, padded_height), 255)
        canvas.paste(img, (0, 0))
        img = canvas
        height = padded_height

    # PM290 bitmap polarity: 0 = print black, 1 = skip white.
    raster = bytearray()
    for y in range(height):
        for xb in range(WIDTH // 8):
            b = 0xFF
            for bit in range(8):
                if img.getpixel((xb * 8 + bit, y)) == 0:
                    b &= ~(1 << (7 - bit))
            raster.append(b)

    header = (
        f"SIZE 54.0 mm,{height / 8:.1f} mm\r\n"
        "DIRECTION 0,0\r\n"
        "DENSITY 10\r\n"
        "CLS\r\n"
        "PRINT 1\r\n"
        f"BITMAP 0,0,48,{height},1,"
    ).encode("ascii")

    return header + raster + b"ALLEND\r\n"

def main():
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} image.png")

    job = make_job(sys.argv[1])
    print(f"Prepared {len(job)} bytes of print data.")

    with serial.Serial(
        PORT, baudrate=115200, timeout=1, write_timeout=10,
        xonxoff=False, rtscts=False, dsrdtr=False
    ) as ser:
        ser.write(b"\x11")
        ser.write(b"\x1b!o\r\n")
        ser.flush()
        time.sleep(0.2)
        ser.reset_input_buffer()

        ser.write(b"CONFIG?\r\n")
        ser.flush()
        time.sleep(0.6)
        reply = ser.read(512)
        print("Printer response:", repr(reply))

        if b"CONFIG" not in reply:
            sys.exit("No CONFIG response; image was NOT sent.")

        ser.write(job)
        ser.flush()
        print("Print data sent.")
        time.sleep(100)

if __name__ == "__main__":
    main()
