import bluetooth
from threading import Thread
import netifaces as ni
import socket
import cv2
import struct
import pickle
import numpy as np
import time
from PIL import Image

from utils_folder import hash_pass
from utils_folder import neural_network

image = []
new_face_img = []
new_face_flag = 0

faces_dict = {1: ['Przemek', 'Kanach']}
ids = 2

person = 0
good_rfid = 0
good_pin = 0

choose_machine = '0'
m1_rfid = 1
m1_pin = 0
m2_rfid = 0
m2_pin = 1
m3_rfid = 1
m3_pin = 1
flag_unlocked = 0

# 123A
m1_pass = '85ea5d05ec1ea1a344bc3ee43dedc31ab3dba23d782c4e93e0e21d083ca66a15ae95a47aa7a30cb34a31c73844ce6c2d6cfed3313b7b89870b671893b9007bc61ff6cb13fbebbd2f80f9b8969df59898b2743b940de15e44ad0a77a31687259d'
# 456B
m2_pass = '7dc2587ffb22b598fbe49b9d068ae01634a43003dbe3fb48917c332b8b1458b438da4eafcb10f5903ff41601b10fa69dfe4635086842b271c0ec146e51250a7e0dbb07d8b219ead3b9e847a7dc5c58101abf10f55748eb80adcbb7544aa0458b'
# 789C
m3_pass = '0ae1b9ff1a889701290c7c01da4b2a7d48c97b7a039d39f86ba217f6c1c43f78fa105c3f9491e0b2f108929d2e67c4c4558b859d8ed6f60aaa604358e344939a5116c70018d29bd412d2c1c8d987cfa237fd0846c764c06242db90299c02e2f3'


def network():
    global person
    global new_face_flag

    while True:
        time.sleep(0.5)
        if type(image) == np.ndarray:
            try:
                if new_face_flag == 1:
                    neural_network.original_images(new_face_img)
                    new_face_flag = 0
                neural_network.face_reg(image)
                person = neural_network.person
            except:
                pass


def get_rfid():
    global good_rfid

    bd_addr = "98:D3:32:10:BD:7F"

    port = 1
    s_blu = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s_blu.connect((bd_addr, port))
    print('Connected')

    try:
        while True:
            data = []
            data_all = []
            while True:
                data = s_blu.recv(50)
                data = data.decode('utf-8')
                if data:
                    data_all.append(data)
                    if data[-1] == ';':
                        data_all = ''.join(data_all)
                        data_all = data_all[:-1]
                        if data_all == 'Access':
                            good_rfid = 1
                        elif data_all == 'Other':
                            good_rfid = 2
                        break
    except KeyboardInterrupt:
        s_blu.close()


def get_image():
    global image
    host = ni.ifaddresses('wlp3s0')[ni.AF_INET][0]['addr']
    port = 1313

    print(host)

    s_img = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_img.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_img.bind((host, port))
    s_img.listen(2)

    print('Waiting for CAMERA connection')

    conn, addr = s_img.accept()
    print('CAMERA connection from', addr)

    while True:
        len_str = conn.recv(4)
        size = struct.unpack('!i', len_str)[0]

        img_str = b''

        while size > 0:
            if size >= 4096:
                data = conn.recv(4096)
            else:
                data = conn.recv(size)

            if not data:
                break

            size -= len(data)
            img_str += data

        frame_data = img_str
        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        image = frame
        if person != 0:
            cv2.putText(frame, faces_dict[person][0], (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, 255)
        cv2.imshow('ImageWindow', frame)
        cv2.waitKey(30)


def get_pin():

    global good_pin
    global good_rfid
    global choose_machine
    global flag_unlocked

    host = ni.ifaddresses('wlp3s0')[ni.AF_INET][0]['addr']
    port = 1314

    s_pin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_pin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_pin.bind((host, port))
    s_pin.listen(2)

    print('Waiting for PIN connection')

    conn, addr = s_pin.accept()
    print('PIN connection from', addr)

    while True:
        print('MACHINE')
        choose_machine = conn.recv(4096)
        choose_machine = choose_machine.decode('utf-8')

        good_rfid = 0

        if choose_machine == '1':
            conn.send(str.encode(choose_machine + '/' +
                                 str(m1_rfid) + '/' + str(m1_pin)))
        elif choose_machine == '2':
            conn.send(str.encode(choose_machine + '/' +
                                 str(m2_rfid) + '/' + str(m2_pin)))
        elif choose_machine == '3':
            conn.send(str.encode(choose_machine + '/' +
                                 str(m3_rfid) + '/' + str(m3_pin)))
        else:
            conn.send(str.encode('WRONG_MACHINE'))
            choose_machine = '0'

        if (choose_machine == '1' and m1_pin == 1) or (choose_machine == '2' and m2_pin == 1) or (choose_machine == '3' and m3_pin == 1):
            data = conn.recv(4096)
            data = data.decode('utf-8')

            good_rfid = 0

            if data:
                if choose_machine == '1' and m1_pin == 1:
                    if hash_pass.verify_password(m1_pass, data):
                        print('GOOD M1')
                        good_pin = 1
                        conn.send(str.encode('GOOD_PIN'))
                    else:
                        print('WRONG M1')
                        good_pin = 0
                        good_rfid = 0
                        conn.send(str.encode('WRONG_PIN'))
                elif choose_machine == '2' and m2_pin == 1:
                    if hash_pass.verify_password(m2_pass, data):
                        print('GOOD M2')
                        good_pin = 1
                        conn.send(str.encode('GOOD_PIN'))
                    else:
                        print('WRONG M2')
                        good_pin = 0
                        good_rfid = 0
                        conn.send(str.encode('WRONG_PIN'))
                elif choose_machine == '3' and m3_pin == 1:
                    if hash_pass.verify_password(m3_pass, data):
                        print('GOOD M3')
                        good_pin = 1
                        conn.send(str.encode('GOOD_PIN'))
                    else:
                        print('WRONG M3')
                        good_pin = 0
                        good_rfid = 0
                        conn.send(str.encode('WRONG_PIN'))

        if (choose_machine == '1' and m1_rfid == 1) or (choose_machine == '2' and m2_rfid == 1) or (choose_machine == '3' and m3_rfid == 1):
            print('SECOND DATA')
            data = conn.recv(4096)
            data = data.decode('utf-8')

            if data == 'WRONG_RFID':
                good_rfid = 0
                good_pin = 0


def app():

    global m1_rfid
    global m1_pin
    global m2_rfid
    global m2_pin
    global m3_rfid
    global m3_pin

    global ids
    global first_names
    global last_names

    global m1_pass
    global m2_pass
    global m3_pass

    global new_face_flag
    global ids
    global new_face_img

    host = ni.ifaddresses('wlp3s0')[ni.AF_INET][0]['addr']
    port = 1315

    s_app = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_app.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_app.bind((host, port))
    s_app.listen(2)

    print('Waiting for APP connection')

    conn, addr = s_app.accept()
    print('APP connection from', addr)
    conn.send(str.encode('GC'))

    while True:

        top_data = conn.recv(3)
        top_data = top_data.decode('utf-8')

        if top_data:

            if top_data == 'new':
                len_str = conn.recv(4)
                size = struct.unpack('!i', len_str)[0]

                img_str = b''

                while size > 0:
                    if size >= 4096:
                        data = conn.recv(4096)
                    else:
                        data = conn.recv(size)

                    if not data:
                        break

                    size -= len(data)
                    img_str += data

                data = pickle.loads(img_str)

                basewidth = 700

                img = Image.open(data).convert('RGB')
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), Image.ANTIALIAS)

                img_array = np.array(img)

                new_face_img = img_array[:, :, ::-1].copy()

                # cv2.imshow('siema', new_face_img)
                # cv2.waitKey(0)

                data = conn.recv(4096)
                data = data.decode('utf-8')

                if data:

                    faces_dict[ids] = [data.split('/')[0], data.split('/')[1]]

                    ids += 1
                    new_face_flag = 1

            elif top_data[:2] == 'pa':

                data = conn.recv(4096)
                data = data.decode('utf-8')

                if data:
                    if top_data[-1] == '1':
                        m1_pass = hash_pass.hash_password(data)
                    elif top_data[-1] == '2':
                        m2_pass = hash_pass.hash_password(data)
                    elif top_data[-1] == '3':
                        m3_pass = hash_pass.hash_password(data)

            elif top_data == 'mch':

                data = conn.recv(4096)
                data = data.decode('utf-8')

                if data:
                    if data[:2] == 'm1':
                        if data[2:] == 'r1':
                            m1_rfid = 1
                        elif data[2:] == 'r0':
                            m1_rfid = 0
                        elif data[2:] == 'p1':
                            m1_pin = 1
                        elif data[2:] == 'p0':
                            m1_pin = 0
                    elif data[:2] == 'm2':
                        if data[2:] == 'r1':
                            m2_rfid = 1
                        elif data[2:] == 'r0':
                            m2_rfid = 0
                        elif data[2:] == 'p1':
                            m2_pin = 1
                        elif data[2:] == 'p0':
                            m2_pin = 0
                    elif data[:2] == 'm3':
                        if data[2:] == 'r1':
                            m3_rfid = 1
                        elif data[2:] == 'r0':
                            m3_rfid = 0
                        elif data[2:] == 'p1':
                            m3_pin = 1
                        elif data[2:] == 'p0':
                            m3_pin = 0


def send_door():

    global good_rfid
    global good_pin
    global choose_machine
    global flag_unlocked

    entered_people = {}

    host = ni.ifaddresses('wlp3s0')[ni.AF_INET][0]['addr']
    port = 1316

    s_door = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_door.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_door.bind((host, port))
    s_door.listen(2)

    print('Waiting for DOOR connection')

    conn, addr = s_door.accept()
    print('DOOR connection from', addr)

    access_or_not = 0

    while True:
        time.sleep(1)
        if choose_machine == '1':
            if (m1_rfid == 0) and (m1_pin == 0):
                access_or_not = 1
            elif (m1_rfid == 1) and (m1_pin == 0):
                if good_rfid == 1:
                    access_or_not = 1
                else:
                    access_or_not = 0
            elif (m1_rfid == 0) and (m1_pin == 1):
                if good_pin == 1:
                    access_or_not = 1
                else:
                    access_or_not = 0
            elif (m1_rfid == 1) and (m1_pin == 1):
                if (good_rfid == 1) and (good_pin == 1):
                    access_or_not = 1
                else:
                    access_or_not = 0
        if choose_machine == '2':
            if (m2_rfid == 0) and (m2_pin == 0):
                access_or_not = 1
            elif (m2_rfid == 1) and (m2_pin == 0):
                if good_rfid == 1:
                    access_or_not = 1
                else:
                    access_or_not = 0
            elif (m2_rfid == 0) and (m2_pin == 1):
                if good_pin == 1:
                    access_or_not = 1
                else:
                    access_or_not = 0
            elif (m2_rfid == 1) and (m2_pin == 1):
                if (good_rfid == 1) and (good_pin == 1):
                    access_or_not = 1
                else:
                    access_or_not = 0
        if choose_machine == '3':
            if (m3_rfid == 0) and (m3_pin == 0):
                access_or_not = 1
            elif (m3_rfid == 1) and (m3_pin == 0):
                if good_rfid == 1:
                    access_or_not = 1
                else:
                    access_or_not = 0
            elif (m3_rfid == 0) and (m3_pin == 1):
                if good_pin == 1:
                    access_or_not = 1
                else:
                    access_or_not = 0
            elif (m3_rfid == 1) and (m3_pin == 1):
                if (good_rfid == 1) and (good_pin == 1):
                    access_or_not = 1
                else:
                    access_or_not = 0
        if (good_rfid == 1 or good_rfid == 2):
            conn.send(str.encode(str(good_rfid)))
        if person and access_or_not:
            saved_person = person
            time.sleep(0.5)
            if saved_person not in entered_people:
                conn.send(str.encode(str(faces_dict[saved_person][0]) + '/' +
                                     str(faces_dict[saved_person][1]) + '/' + str(access_or_not)))
                entered_people[saved_person] = time.time()
            else:
                elapsed = time.time() - entered_people[saved_person]
                work_hours = int(elapsed / 3600)
                work_minutes = int(elapsed / 60)
                work_seconds = int(elapsed % 60)
                conn.send(str.encode(str(faces_dict[saved_person][0]) + '/' +
                                     str(faces_dict[saved_person][1]) + '/' +
                                     str(access_or_not) + '/' +
                                     str(work_hours) + '/' +
                                     str(work_minutes) + '/' +
                                     str(work_seconds)))
                del entered_people[saved_person]
            data = conn.recv(4096)
            data = data.decode('utf-8')
            if data == 'unlocked':
                print('UNLOCKED')
                choose_machine = '0'
                good_rfid = 0
                good_pin = 0
                access_or_not = 0
            time.sleep(1)


try:
    f1 = Thread(target=network)
    f1.daemon = True
    f1.start()
    f2 = Thread(target=get_rfid)
    f2.daemon = True
    f2.start()
    f3 = Thread(target=get_image)
    f3.daemon = True
    f3.start()
    f4 = Thread(target=get_pin)
    f4.daemon = True
    f4.start()
    f5 = Thread(target=app)
    f5.daemon = True
    f5.start()
    f6 = Thread(target=send_door)
    f6.daemon = True
    f6.start()

    while True:
        pass

# Reset by pressing CTRL + C
except KeyboardInterrupt:
    cv2.destroyAllWindows()
