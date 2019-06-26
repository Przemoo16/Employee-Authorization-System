from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.behaviors import ToggleButtonBehavior, ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

import io
import struct
import os

from plyer import camera

import socket
import pickle

Host = '192.168.100.11'
Port = '1315'
Wifi = False

try:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    android_api_version = autoclass('android.os.Build$VERSION')
    AndroidView = autoclass('android.view.View')
    AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

    Logger.debug(
        'Application runs on Android, API level {0}'.format(
            android_api_version.SDK_INT
        )
    )
except ImportError:
    def run_on_ui_thread(func):
        def wrapper(*args):
            Logger.debug('{0} called on non android platform'.format(
                func.__name__
            ))
        return wrapper

Builder.load_file('App_Kivy.kv')


class MenuImageButton(ButtonBehavior, Image):
    def on_press(self):
        self.source = 'Images/button_dn.png'

    def on_release(self):
        self.source = 'Images/button.png'


class MachineImageButton(ToggleButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(MachineImageButton, self).__init__(**kwargs)
        self.source = 'Images/button.png'

    def on_state(self, widget, value):
        if value == 'down':
            self.source = 'Images/button_dn.png'
        else:
            self.source = 'Images/button.png'


class WifiImageButton(ButtonBehavior, Image):
    def on_press(self):
        self.source = 'Images/wifi_dn.png'

    def on_release(self):
        self.source = 'Images/wifi.png'


class ArrowImageButton(ButtonBehavior, Image):
    def on_press(self):
        self.source = 'Images/back_arrow_dn.png'

    def on_release(self):
        self.source = 'Images/back_arrow.png'


class SendImageButton(ButtonBehavior, Image):
    def on_press(self):
        self.source = 'Images/send_dn.png'

    def on_release(self):
        self.source = 'Images/send.png'


class MenuScreen(Screen):
    def __init__(self, **kwargs):

        super(Screen, self).__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')

        self.host_input = TextInput(id='host', text=Host, font_size=25, multiline=False)
        self.box.add_widget(self.host_input)
        self.port_input = TextInput(id='port', text=Port, font_size=25, multiline=False)
        self.box.add_widget(self.port_input)
        self.box.add_widget(Button(text='OK', on_press=lambda a: self.try_connect()))

        self.popup = Popup(title='Set IP and HOST', auto_dismiss=False,
                           size_hint=(.5, .3), content=self.box)

        self.tick = Image(id='tick', source='Images/tick.png',
                          allow_stretch=False,
                          keep_ratio=True,
                          pos_hint={"center_x": 0.73, "center_y": 0.8},
                          size_hint=(0.08, 0.08))

        self.wrong = Image(id='wrong', source='Images/wrong.png',
                           allow_stretch=False,
                           keep_ratio=True,
                           pos_hint={"center_x": 0.73, "center_y": 0.8},
                           size_hint=(0.08, 0.08))

    @run_on_ui_thread
    def android_set_hide_menu(self):
        if android_api_version.SDK_INT >= 19:
            Logger.debug('API >= 19. Set hide menu')
            view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
            view.setSystemUiVisibility(
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )

    def open_popup(self):
        self.popup.open()

    def try_connect(self):
        self.change_host_and_ip(self.host_input.text, self.port_input.text)
        self.wifi_active()
        self.popup.dismiss()
        self.android_set_hide_menu()

    def change_host_and_ip(self, host, port):
        global Host
        global Port
        Host = host
        Port = int(port)

    def wifi_active(self):
        global Wifi
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        adress = ((Host, Port))
        try:
            s.connect(adress)
            answer = s.recv(2)
            if answer == b'GC':
                self.remove_widget(self.tick)
                self.remove_widget(self.wrong)
                self.add_widget(self.tick)
                Wifi = True

        except socket.error:
            self.remove_widget(self.wrong)
            self.remove_widget(self.tick)
            self.add_widget(self.wrong)
            Wifi = False


class Machine1(Screen):

    def m1_rfid(self, widget, value):
        if Wifi:
            if value == 'down':
                s.send(str.encode('mch'))
                s.send(str.encode('m1r1'))
            else:
                s.send(str.encode('mch'))
                s.send(str.encode('m1r0'))

    def m1_pin(self, widget, value):
        if Wifi:
            if value == 'down':
                s.send(str.encode('mch'))
                s.send(str.encode('m1p1'))
            else:
                s.send(str.encode('mch'))
                s.send(str.encode('m1p0'))


class Machine2(Screen):

    def m2_rfid(self, widget, value):
        if Wifi:
            if value == 'down':
                s.send(str.encode('mch'))
                s.send(str.encode('m2r1'))
            else:
                s.send(str.encode('mch'))
                s.send(str.encode('m2r0'))

    def m2_pin(self, widget, value):
        if Wifi:
            if value == 'down':
                s.send(str.encode('mch'))
                s.send(str.encode('m2p1'))
            else:
                s.send(str.encode('mch'))
                s.send(str.encode('m2p0'))


class Machine3(Screen):

    def m3_rfid(self, widget, value):
        if Wifi:
            if value == 'down':
                s.send(str.encode('mch'))
                s.send(str.encode('m3r1'))
            else:
                s.send(str.encode('mch'))
                s.send(str.encode('m3r0'))

    def m3_pin(self, widget, value):
        if Wifi:
            if value == 'down':
                s.send(str.encode('mch'))
                s.send(str.encode('m3p1'))
            else:
                s.send(str.encode('mch'))
                s.send(str.encode('m3p0'))


class Pin1(Screen):
    def __init__(self, **kwargs):

        super(Screen, self).__init__(**kwargs)

        self.text_pin = ''

    def on_keyboard(self, instance):
        if len(self.text_pin) < 10:
            if instance.text == 'D':
                self.text_pin = self.text_pin[:-1]
            else:
                self.text_pin += instance.text

            self.ids.label_pin.text = '*' * len(self.text_pin)
        elif instance.text == 'D':
            self.text_pin = self.text_pin[:-1]
            self.ids.label_pin.text = '*' * len(self.text_pin)

    def clear_label(self):
        self.text_pin = ''
        self.ids.label_pin.text = '*' * len(self.text_pin)

    def send_pin(self):
        if Wifi:
            s.send('pa1'.encode('utf-8'))
            s.send(str.encode(self.text_pin))
            self.text_pin = ''
            self.ids.label_pin.text = '*' * len(self.text_pin)


class Pin2(Screen):
    def __init__(self, **kwargs):

        super(Screen, self).__init__(**kwargs)

        self.text_pin = ''

    def on_keyboard(self, instance):
        if len(self.text_pin) < 10:
            if instance.text == 'D':
                self.text_pin = self.text_pin[:-1]
            else:
                self.text_pin += instance.text

            self.ids.label_pin.text = '*' * len(self.text_pin)
        elif instance.text == 'D':
            self.text_pin = self.text_pin[:-1]
            self.ids.label_pin.text = '*' * len(self.text_pin)

    def clear_label(self):
        self.text_pin = ''
        self.ids.label_pin.text = '*' * len(self.text_pin)

    def send_pin(self):
        if Wifi:
            s.send('pa2'.encode('utf-8'))
            s.send(str.encode(self.text_pin))
            self.text_pin = ''
            self.ids.label_pin.text = '*' * len(self.text_pin)


class Pin3(Screen):
    def __init__(self, **kwargs):

        super(Screen, self).__init__(**kwargs)

        self.text_pin = ''

    def on_keyboard(self, instance):
        if len(self.text_pin) < 10:
            if instance.text == 'D':
                self.text_pin = self.text_pin[:-1]
            else:
                self.text_pin += instance.text

            self.ids.label_pin.text = '*' * len(self.text_pin)
        elif instance.text == 'D':
            self.text_pin = self.text_pin[:-1]
            self.ids.label_pin.text = '*' * len(self.text_pin)

    def clear_label(self):
        self.text_pin = ''
        self.ids.label_pin.text = '*' * len(self.text_pin)

    def send_pin(self):
        if Wifi:
            s.send('pa3'.encode('utf-8'))
            s.send(str.encode(self.text_pin))
            self.text_pin = ''
            self.ids.label_pin.text = '*' * len(self.text_pin)


class AddEmployee(Screen):
    def __init__(self, **kwargs):

        super(Screen, self).__init__(**kwargs)

        # self.folder = os.path.dirname(os.path.abspath(__file__))
        self.folder = '/storage/emulated/0/AppDoor_face'
        self.filename = 'face.jpg'
        self.filepath = os.path.join(self.folder, self.filename)

        self.tick = Image(id='tick', source='Images/tick.png',
                          allow_stretch=False,
                          keep_ratio=True,
                          pos_hint={"center_x": 0.65, "center_y": 0.2},
                          size_hint=(0.08, 0.08))

        self.wrong = Image(id='wrong', source='Images/wrong.png',
                           allow_stretch=False,
                           keep_ratio=True,
                           pos_hint={"center_x": 0.65, "center_y": 0.2},
                           size_hint=(0.08, 0.08))

    @run_on_ui_thread
    def android_set_hide_menu(self):
        if android_api_version.SDK_INT >= 19:
            Logger.debug('API >= 19. Set hide menu')
            view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
            view.setSystemUiVisibility(
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )

    def hide_menu(self):
        self.android_set_hide_menu()

    def send_form(self):
        if Wifi:
            if (self.ids.first.text == '') or (self.ids.last.text == '') or (not os.path.exists(self.filepath)):
                self.ids.first.text = ''
                self.ids.last.text = ''
                self.remove_widget(self.tick)
                self.remove_widget(self.wrong)
                self.add_widget(self.wrong)
            else:
                data = io.BytesIO(open(self.filepath, "rb").read())
                im_to_send = pickle.dumps(data)
                len_str = struct.pack('!i', len(im_to_send))
                s.send('new'.encode('utf-8'))
                s.send(len_str)
                s.send(im_to_send)
                s.send(str.encode(self.ids.first.text) +
                       str.encode('/') + str.encode(self.ids.last.text))
                self.ids.first.text = ''
                self.ids.last.text = ''
                os.remove(self.filepath)
                self.remove_widget(self.tick)
                self.remove_widget(self.wrong)
                self.add_widget(self.tick)
        else:
            self.ids.first.text = ''
            self.ids.last.text = ''

    def leave_screen(self):
        self.ids.first.text = ''
        self.ids.last.text = ''
        self.remove_widget(self.tick)
        self.remove_widget(self.wrong)

    def do_capture(self):

        if(os.path.exists(self.filepath)):
            os.remove(self.filepath)

        try:
            camera.take_picture(filename=self.filepath,
                                on_complete=self.camera_callback)
        except NotImplementedError:
            popup = MsgPopup(
                "This feature has not yet been\nimplemented for this platform.")
            popup.open()

    def camera_callback(self, filepath):

        self.android_set_hide_menu()

        if(os.path.exists(filepath)):
            popup = MsgPopup("Picture saved!")
            popup.open()
        else:
            popup = MsgPopup("Path not found!")
            popup.open()


class MsgPopup(Popup):
    def __init__(self, msg):
        super(MsgPopup, self).__init__()
        self.ids.message_label.text = msg


class MyApp(App):

    @run_on_ui_thread
    def android_set_hide_menu(self):
        if android_api_version.SDK_INT >= 19:
            Logger.debug('API >= 19. Set hide menu')
            view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
            view.setSystemUiVisibility(
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )

    def on_start(self):
        self.android_set_hide_menu()

    def on_resume(self):
        self.android_set_hide_menu()

    def on_pause(self):
        return True

    def on_stop(self):
        Window.close()

    def build(self):

        self.android_set_hide_menu()

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(Machine1(name='machine1'))
        sm.add_widget(Machine2(name='machine2'))
        sm.add_widget(Machine3(name='machine3'))
        sm.add_widget(AddEmployee(name='add_emp'))
        sm.add_widget(Pin1(name='pin1'))
        sm.add_widget(Pin2(name='pin2'))
        sm.add_widget(Pin3(name='pin3'))

        return sm


if __name__ == '__main__':
    try:
        MyApp().run()
    except KeyboardInterrupt:
        pass
