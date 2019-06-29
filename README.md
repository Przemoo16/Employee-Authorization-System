# Overview

The project presents a system of employee authorization, which can be used in a factory or any industrial plant. This solution allows access to individual machines, rooms or devices that
it can be individually tailored to each employee. The design consists of a dummy door opened with an electric lock. System has three types of security:
* PIN code
* RFID card reader
* System face recognition

A person who wants to get into a room with a specific device must be authorized by the selected security. At the moment of successful verification, the doors are opened.

The system is controlled by a mobile application. Thanks to app it is possible to change the PIN and security code of the given machine and to add a new employee.

<p align="center">
  <img src="/Images/door.JPG" width="500" height="800" />
</p>

## Application build

The easiest way is to install the file my_app.apk.

If you want to change something in the code, you have to build the application again. The buildozer tool is used for this. Instruction on how to use the buildozer tool is available at this link [Buildozer](https://github.com/kivy/buildozer).

**When building the application, replace the generated *buildozer.spec* file with the one from this repository. If you don't do this, the application will not work correctly.**

**To build the application use the Cython version == 0.25.2. It may not work with newer versions.**

## How to run

First, Download weights and face landmarks for neural network: 
* [Weights](https://drive.google.com/file/d/1CPSeum3HpopfomUEK1gybeuIVoeJT_Eo/view).
* [Face Landmarks](https://github.com/AKSHAYUBHAT/TensorFace/blob/master/openface/models/dlib/shape_predictor_68_face_landmarks.dat).

Then, turn on Arduino and upload the program to it.

Next, run server.py on PC. The console displays the address where the server listens for connections.

At the end, change IP's in client\_cam.py and client\_door.py and run it on two Raspberry Pi.

## How to use mobile app

In mobile appplication after pressing the WI-Fi logo, you connect to the server that is on the PC. After the correct connection, the tick icon will appear. In the main menu there is a possibility to choose 4 keys (3 machines and adding a new employee). After selecting a particular machine, you can change the security. It is possible to add a new employee by entering his name and taking a face photo.

### Images

<p align="center">
<img src="/Images/1.png" width="400" height="300" />
<img src="/Images/2.png" width="400" height="300" />
</p>
</center>

<p align="center">
<img src="/Images/3.JPG" width="768" height="448" />
<img src="/Images/4.JPG" width="768" height="448" />
</p>
</center>

<p align="center">
<img src="/Images/5.png" width="260" height="540" />
<img src="/Images/6.png" width="260" height="540" />
<img src="/Images/7.png" width="260" height="540" />
</p>
</center>


## Requirements

### To build app

* [Kivy](https://kivy.org/#home) - Library for development of applications
* [Kivy-Garden](http://kivy-garden.github.io) - Project to centralize addons for Kivy maintained by users
* [PyGame](https://www.pygame.org/news) - Library for making multimedia applications like games built on top of the SDL library
* [Pillow](https://pillow.readthedocs.io/en/stable/) - Imaging Library
* [Plyer](https://plyer.readthedocs.io/en/latest/#) - Library for accessing features of your hardware / platforms
* [Pyjnius](https://pyjnius.readthedocs.io/en/latest/) - Library for accessing Java classes
* [Cython](https://cython.org) - Optimising static compiler for both the Python programming language and the extended Cython programming language

### To run clients and server

* [OpenCV](https://pypi.org/project/opencv-python/) - Open source computer vision and machine learning software library
* [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) - Package provides a class to control the GPIO on a Raspberry Pi
* [RPLCD](https://pypi.org/project/RPLCD/) - Package to control LCDs
* [PyBluez](https://pypi.org/project/PyBluez/) - Bluetooth Python extension module
* [TensorFlow](https://www.tensorflow.org/) - Deep learning framework (version 1.12)
* [Pillow](https://pillow.readthedocs.io/en/stable/) - Imaging Library
* [netifaces](https://pypi.org/project/netifaces/) - Library to get the address(es) of the machine’s network interfaces from Python
* [Numpy](http://www.numpy.org) - Package for scientific computing
* [HDF5](http://docs.h5py.org/en/stable/) - Pythonic interface to the HDF5 binary data format
* [dlib](https://pypi.org/project/dlib/) - A toolkit for making real world machine learning and data analysis applications

### To run Arduino client

* [SoftwareSerial](https://www.arduino.cc/en/Reference/SoftwareSerial) - Library to allow serial communication on other digital pins of the Arduino
* [MFRC522](https://www.arduinolibraries.info/libraries/mfrc522) - Arduino library for MFRC522 and other RFID RC522 based modules

## Author

* **Przemysław Kanach** - [Przemysław Kanach](https://github.com/Przemoo16)
