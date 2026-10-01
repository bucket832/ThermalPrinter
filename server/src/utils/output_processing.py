import usb.core


VID = 0x28e9
PID = 0x0289

dev = usb.core.find(idVendor=VID, idProduct=PID)

if dev is None:
    raise Exception("Printer not found")

dev.set_configuration()



def printString(string):
    dev.write(0x03, bytes(string, 'utf-8'))
    dev.write(0x03, b"\n\n\n")

def printBytes(b):
    dev.write(0x03, b)
    dev.write(0x03, b"\n\n\n")


if __name__ == "__main__":
    print("Testing Only")
    dev.write(0x03, b"\x1d\x21\x00") 
    dev.write(0x03, bytes("small font ?", 'utf-8'))
    dev.write(0x03, b"\n\n\n")




