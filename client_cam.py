import socket
import cv2
import pickle
import struct

global_host = '192.168.1.102'

s_img = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = global_host
port = 1313

adress = ((host, port))
s_img.connect(adress)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(frame, 0)
        len_str = struct.pack('!i', len(data))
        s_img.send(len_str)
        s_img.send(data)
        cv2.waitKey(30)
except KeyboardInterrupt:
    cv2.destroyAllWindows()
