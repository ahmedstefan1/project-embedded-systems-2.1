import serial
import serial.tools.list_ports as com_ports
import binascii
from sched import *
from time import *


connection = serial.Serial()
s = scheduler(time, sleep)
ran_once = False


# haalt op wat voor comports zijn aangesloten op de PC
def get_com_ports():
    ports = list(com_ports.comports())
    formatted_comports = []
    for p in ports:
        formatted_comports.append(p[0])
    if len(ports) < 1:
        return "N/A"
    else:
        return formatted_comports


# maakt de seriele connectie
def serial_connection(com):
    global connection
    connection = serial.Serial(com, 19200)
    print(connection)
    add_task()


def clean_queue():
    try:
        for task in s.queue:
            s.cancel(task)
        print("queue empty?:" + s.empty())
    except:
        print(s.queue)
        print("empty")


# sluit de seriële connectie
def close_connection():
    global connection
    clean_queue()

    if connection.is_open and s.empty():
        connection.close()
    else:
        print("no connection is open")


# leest de wat de arduino verstuurt
def getpacket():
    global connection
    x = connection.readline()
    try:
        protocol_understanding(binascii.hexlify(x))
    except:
        print("guess what again")
        print(x)


# hoort characters te versturen
def sendpacket(data=None):
    global connection, ran_once
    clean_queue()
    print("came here")
    print(data)
    connection.write(data)
    ran_once = False
    add_task()


def addself():
    s.enter(0.2, 3, add_task)
    s.enter(1, 4, addself)


# adds tasks
def add_task(task=getpacket, priority=3, args=None):
    # als er geen argumenten zijn gegeven hoeven die niet erbij
    # TODO check how often reading data is in the queue and how often adding yourself is in the queue?
    # TODO make sure that adding itsself is in there max 1-2 times and reading is in there max 3-5 times?
    if not ran_once:
        addself()
    if args is None:
        s.enter(0.1, priority, task)
    else:
        s.enter(0.1, priority, task, argument=args)
    # zorgt ervoor dat deze taak zichzelf oproept zodat je niet alleen 1 keer de getpackets uitvoert
    # voert de taken uit
    s.run()


# understands the protocol and checks for mistakes
def protocol_understanding(data):
    # slices the data to what is needed
    sliced_data = data[0:4]

    # puts the data in different variables
    sensor = sliced_data[0:1]
    waarde = sliced_data[1:3]
    check = sliced_data[3:4]
    # xors the front part of the data with the back part, er is wat omrekenen nodig
    # Xor werkt alleen met Int en niet met hexadecimalen
    u1 = int(waarde[0:1], 16) ^ int(waarde[1:2], 16)
    # xors de data van de sensor met uitkomst1 (u1)
    u2 = u1 ^ int(sensor, 16)
    # kijkt of die waarden overeen komen ( als ze niet overeen komen is er waarschijnlijk ergens een fout ontstaan
    if u2 == int(check, 16):
        # welke sensor komt het uit
        if sensor == b'8':
            # print de waarde van de sensor naar de console
            print("temperatuur:" + str(int(waarde, 16)) + u'\u00B0' + "C")
        # elif sensor ==
            # print("sensor:" + str(int(waarde, 16)) + "eenheid")
        # elif sensor ==
            # print("sensor:" + str(int(waarde, 16)) + "eenheid")
        # elif sensor ==
            # print("sensor:" + str(int(waarde, 16)) + "eenheid")
        else:
            print("something went wrong")
            print(data)

    else:
        print("didnt pass check")
        print(data)

