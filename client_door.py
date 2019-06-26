import socket
from threading import Thread
import time
import RPi.GPIO as GPIO
from RPLCD import CharLCD

global_host = '192.168.1.102'

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

lock = 17

GPIO.setup(lock, GPIO.OUT)
GPIO.output(lock, GPIO.LOW)

show_time = '0'
work_hours = '0'
work_minutes = '0'
work_seconds = '0'

step = 0
lcd_flag = 0

lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2,
              pin_rs=21, pin_e=20, pins_data=[16, 12, 27, 22],
              compat_mode=True)

lcd.clear()
lcd.cursor_mode = 'hide'

first_name = ''
second_name = ''


def send_pin():
    global step
    global lcd_flag
    global lcd

    s_pin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = global_host
    port = 1314

    adress = ((host, port))
    s_pin.connect(adress)

    matrix = [['1', '2', '3', 'A'],
              ['4', '5', '6', 'B'],
              ['7', '8', '9', 'C'],
              ['*', '0', '#', 'D']]

    row = [14, 15, 18, 23]
    col = [24, 25, 8, 7]

    for j in range(4):
        GPIO.setup(col[j], GPIO.OUT)
        GPIO.output(col[j], 1)

    for i in range(4):
        GPIO.setup(row[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    text_pin = ''

    write_pin = 0

    m_pin = 0
    m_rfid = 0

    while True:
        for j in range(4):
            GPIO.output(col[j], 0)

            for i in range(4):
                if GPIO.input(row[i]) == 0:
                    if matrix[i][j] == 'D':
                        start = time.time()
                        while (GPIO.input(row[i]) == 0):
                            if (time.time() - start > 1.0) and (text_pin != '') and (step == 0 or step == 1):
                                s_pin.send(str.encode(text_pin))
                                data = s_pin.recv(4096)
                                data = data.decode('utf-8')
                                data_splitted = data.split('/')
                                if len(data_splitted) == 3:
                                    m_rfid = data_splitted[1]
                                    m_pin = data_splitted[2]
                                    if m_pin == '1':
                                        step = 1
                                        lcd_flag = 0
                                    elif m_rfid == '1':
                                        step = 2
                                        lcd_flag = 0
                                    elif (m_pin == '0') and (m_rfid == '0'):
                                        step = 5
                                        lcd_flag = 0
                                elif len(data_splitted) == 1:
                                    if data_splitted[0] == 'GOOD_PIN':
                                        if m_rfid == '1':
                                            step = 2
                                        else:
                                            step = 5
                                        lcd_flag = 0
                                    elif data_splitted[0] == 'WRONG_PIN':
                                        step = 3
                                        lcd_flag = 0
                                    elif data_splitted[0] == 'WRONG_MACHINE':
                                        m_pin = None
                                        m_rfid = None
                                        step = 8
                                        lcd_flag = 0
                                text_pin = ''
                                lcd.cursor_pos = (1, 0)
                                lcd.write_string(u'                ')
                                break
                        if (time.time() - start < 1.0) and (step == 0 or step == 1):
                            text_pin = text_pin[:-1]
                            lcd.cursor_pos = (1, 0)
                            if write_pin == 0:
                                lcd.write_string(text_pin+u' ')
                            if write_pin == 1:
                                lcd.write_string('*'*len(text_pin)+u' ')
                    else:
                        if (step == 0) or (step == 1):
                            text_pin += matrix[i][j]
                            lcd.cursor_pos = (1, 0)
                            if write_pin == 0:
                                lcd.write_string(text_pin)
                            if write_pin == 1:
                                lcd.write_string('*'*len(text_pin))
                        while (GPIO.input(row[i]) == 0):
                            pass

            GPIO.output(col[j], 1)

        if lcd_flag == 0:
            lcd.clear()
            if step == 0:
                lcd_flag = 1
                write_pin = 0
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'CHOOSE MACHINE')
            elif step == 1:
                lcd_flag = 1
                write_pin = 1
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'WRITE PIN')
            elif step == 2:
                lcd_flag = 1
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'PLACE RFID CARD')
                time.sleep(1)
            elif step == 3:
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'WRONG')
                lcd.cursor_pos = (1, 0)
                lcd.write_string(u'PIN')
                if m_rfid == '1':
                    s_pin.send(str.encode(' '))
                time.sleep(1)
                step = 0
            elif step == 4:
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'WRONG')
                lcd.cursor_pos = (1, 0)
                lcd.write_string(u'RFID CARD')
                s_pin.send(str.encode('WRONG_RFID'))
                time.sleep(1)
                step = 0
            elif step == 5:
                lcd_flag = 1
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'FACE')
                lcd.cursor_pos = (1, 0)
                lcd.write_string(u'RECOGNITION')
                if m_rfid == '1':
                    s_pin.send(str.encode(' '))
                time.sleep(2)
            elif step == 6:
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'WELCOME')
                lcd.cursor_pos = (1, 0)
                lcd.write_string(first_name + u' ' + second_name)
                time.sleep(3)
                lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2,
                              pin_rs=21, pin_e=20, pins_data=[16, 12, 27, 22],
                              compat_mode=True)
                lcd.clear()
                step = 0
            elif step == 7:
                lcd.cursor_pos = (0, 0)
                lcd.write_string(first_name + u' ' + second_name)
                lcd.cursor_pos = (1, 0)
                lcd.write_string(
                    u'H: ' + work_hours + u' M: ' + work_minutes + u' S: ' + work_seconds)
                time.sleep(3)
                lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2,
                              pin_rs=21, pin_e=20, pins_data=[16, 12, 27, 22],
                              compat_mode=True)
                lcd.clear()
                step = 0
            elif step == 8:
                lcd.cursor_pos = (0, 0)
                lcd.write_string(u'WRONG')
                lcd.cursor_pos = (1, 0)
                lcd.write_string(u'MACHINE')
                time.sleep(1)
                step = 0


def get_door():
    global flag_send
    global first_name
    global second_name
    global show_time

    global work_hours
    global work_minutes
    global work_seconds

    global step
    global lcd_flag

    access_or_not = 0

    s_door = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = global_host
    port = 1316

    adress = ((host, port))
    s_door.connect(adress)

    while True:
        data = s_door.recv(50)
        data = data.decode('utf-8')
        splitted_data = data.split('/')
        if len(splitted_data) == 3:
            show_time = 0
            first_name = splitted_data[0]
            second_name = splitted_data[1]
            access_or_not = splitted_data[2]
        if len(splitted_data) == 6:
            show_time = 1
            first_name = splitted_data[0]
            second_name = splitted_data[1]
            access_or_not = splitted_data[2]
            work_hours = splitted_data[3]
            work_minutes = splitted_data[4]
            work_seconds = splitted_data[5]
        if len(splitted_data) == 1:
            good_rfid = splitted_data[0]
            if (step == 2) and (good_rfid == '1'):
                step = 5
                lcd_flag = 0
            elif (step == 2) and (good_rfid == '2'):
                step = 4
                lcd_flag = 0
        if (step == 5) and (access_or_not == '1'):
            if show_time == 0:
                step = 6
                lcd_flag = 0
            elif show_time == 1:
                step = 7
                lcd_flag = 0
            s_door.send(str.encode('unlocked'))
            access_or_not = '0'
            time.sleep(0.5)
            GPIO.output(lock, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(lock, GPIO.LOW)


f1 = Thread(target=send_pin)
f1.daemon = True
f1.start()
f2 = Thread(target=get_door)
f2.daemon = True
f2.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    lcd.close(clear=True)
    GPIO.cleanup()
