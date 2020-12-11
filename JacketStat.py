import serial
from serial import Serial
import webbrowser
import time
from threading import Thread
import kivy
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.popup import Popup

global bluetooth
# port = "COM7"
# bluetooth = serial.Serial(port, 9600) #Start communications with the bluetooth unit
# bluetooth.flush()

class Startup(Screen):
    pass

class HomeWindow(Screen):
    lilypad = ObjectProperty(None)
    heatinglabel = ObjectProperty(None)
    coolinglabel = ObjectProperty(None)
    heating_slider = ObjectProperty(None)
    cooling_slider = ObjectProperty(None)
    coolingbutton = ObjectProperty(None)
    heatingbutton = ObjectProperty(None)
    powerswitch = ObjectProperty(None)
    lilypad = ObjectProperty()
    fc = ObjectProperty()

    def heating_label_size(self, *args): #Temperature Setting Number changing on slider
        if self.fc.state == 'normal':
            self.heatinglabel.text = str(int(args[1])) + '°F'
        else:
            self.heatinglabel.text = str(int(args[1])) + '°C'

    def cooling_label_size(self, *args): #Temperature Setting Number changing on slider
        if self.fc.state == 'normal':
            self.coolinglabel.text = str(int(args[1])) + '°F'
        else:
            self.coolinglabel.text = str(int(args[1])) + '°C'

    def heating_restriction(self):# heating slider value cant go above cooling slider value
        if self.heating_slider.value >  self.cooling_slider.value:
            self.heating_slider.value = self.cooling_slider.value

    def cooling_restriction(self):# cooling slider value cant go below heating slider value
        if self.cooling_slider.value < self.heating_slider.value:
            self.cooling_slider.value = self.heating_slider.value

    def coolingbutton_supremacy(self): # pressing cooling button reset sliders value
         while self.powerswitch.state == 'down':
            if self.coolingbutton.state == 'down':
                if self.fc.state == 'normal':
                    self.heating_slider.value = 65
                    self.cooling_slider.value = 65
                if self.fc.state == 'down':
                    self.heating_slider.value = 18
                    self.cooling_slider.value = 18
                break
            else:
                break

    def heatingbutton_supremacy(self): # pressing heating button resets sliders value
        while self.powerswitch.state == 'down':
            if self.heatingbutton.state == 'down':
                if self.fc.state == 'normal':
                    self.cooling_slider.value = 85
                    self.heating_slider.value = 85
                if self.fc.state == 'down':
                    self.cooling_slider.value = 30
                    self.heating_slider.value = 30
                break
            else:
                break

    def button_helper(self):
        while True:
            if self.cooling_slider.value != self.heating_slider.value:
                self.coolingbutton.state = 'normal'
                self.heatingbutton.state = 'normal'
                break
            if self.fc.state == 'normal':
                if(self.cooling_slider.value and self.heating_slider.value) == 65:
                    self.coolingbutton.state = 'down'
                else:
                    self.coolingbutton.state = 'normal'
                if(self.cooling_slider.value and self.heating_slider.value) == 85:
                    self.heatingbutton.state = 'down'
                else:
                    self.heatingbutton.state = 'normal'
            if self.fc.state == 'down':
                if(self.cooling_slider.value and self.heating_slider.value) == 18:
                    self.coolingbutton.state = 'down'
                else:
                    self.coolingbutton.state = 'normal'
                if(self.cooling_slider.value and self.heating_slider.value) == 30:
                    self.heatingbutton.state = 'down'
                else:
                    self.heatingbutton.state = 'normal'
            break

    def power(self):# power functions when off
        if self.powerswitch.state == "normal":
            self.coolinglabel.text = "No Power"
            self.heatinglabel.text = "No Power"
            
        if self.powerswitch.state == "down":
            if self.fc.state == 'normal':# powered on = sliders display values
                self.coolinglabel.text = str(self.cooling_slider.value) + '°F'
                self.heatinglabel.text = str(self.heating_slider.value) + '°F'
            else:
                self.coolinglabel.text = str(self.cooling_slider.value) + '°C'
                self.heatinglabel.text = str(self.heating_slider.value) + '°C'     

    def write_temp(self):
        global bluetooth
        global tempF
        global space
        while self.powerswitch.state == 'down':
            tempF = bluetooth.read(size = 2)#get temperature value from arduino
            tempF = (tempF.decode())
            space = bluetooth.read(size = 2)
            if self.fc.state == "normal": #F
                self.lilypad.text = str(tempF) + '°F'
            else: #C
                tempC = ((int(tempF) - 32) * (5 / 9))
                self.lilypad.text = str(int(tempC)) + '°C'

    def get_temp(self):#Thread for getting temp value
        t1 = Thread(target = self.write_temp)
        t1.start()

    # def write_C(self):
    #     time.sleep(1.0)
    #     global bluetooth
    #     while self.powerswitch.state == 'down':
    #         global tempF
    #         global tempC
    #         tempC = bluetooth.read(size = 2)#get temperature value from arduino
    #         tempC = (tempC.decode())
    #         if self.fc.state == "down":#C
    #             self.lilypad.text = str(tempC) + '°C'
    #         time.sleep(1.0)

    # def get_C(self):#Thread for getting temp value
    #     t2 = Thread(target = self.write_C)
    #     t2.start()

    def send_values(self):
        global bluetooth
        if self.powerswitch.state == 'normal':
            power_status = str(0) + '\n'
        elif self.powerswitch.state == 'down':
            power_status = str(1) + '\n'
        bluetooth.write(power_status.encode('utf-8'))
        time.sleep(0.3)
        while self.powerswitch.state == 'down':
            if self.powerswitch.state == 'normal':
                bluetooth.write(power_status.encode('utf-8'))
                break
            heating_status = str(self.heating_slider.value) + ' '
            cooling_status = str(self.cooling_slider.value) + ' '
            bluetooth.write(heating_status.encode('utf-8'))
            bluetooth.write(cooling_status.encode('utf-8'))
            time.sleep(1.0)
    def get_values(self):
        t3 = Thread(target = self.send_values)
        t3.start()

    def ftoc(self):# changes values for sliders when user changes c -> f, f -> c
        if self.fc.state == "normal":
            self.cooling_slider.value = 75
            self.heating_slider.value = 75
    
        elif self.fc.state == "down":
            self.heating_slider.value = 24
            self.cooling_slider.value = 24
    

class WindowManager(ScreenManager):
    pass

class JacketStat(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(Startup())
        sm.add_widget(HomeWindow())
        return sm

if __name__ == "__main__":
    JacketStat().run()
port = "COM7"