#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
import webbrowser
import os

from kivy.app import App
from os.path import dirname, join
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import BooleanProperty, ObjectProperty,\
    NumericProperty, StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.listview import ListItemButton
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout


from api.api import APIMethods
from modals.modalViewCustom import ModalViewCustom
from modals.popUpPrinters import PopUpPrinters
from modals.modalViewCustom import PopUpWarning
from modals.modalStats import StatsModal

# Opening size
Config.set('graphics', 'width', '1366')
Config.set('graphics', 'height', '768')


class topMenu(BoxLayout):


    # *************************************************************************
    #       Init Function
    # *************************************************************************
    def __init__(self, *args, **kwargs):
        super(topMenu, self).__init__(**kwargs)
        # Title default value: BeeVeryCreative
        self.title="[b]BEE[color=ffffff]VERY[/b]CREATIVE[/color]"



    # *************************************************************************
    #       Function that creates and open a popUp that allows the user to:
    #           - Add a printer;
    #           - Replace a printer;
    #           - Delete a printer;
    # *************************************************************************
    def settingsPopUp(self):
        view = PopUpPrinters()
        view.open()



    # *************************************************************************
    #       Function that creates and open a Modal that allows the user to check the below information:
    #           - Connected Printers;
    #           - Printers currently printing;
    #           - Next printer to finish print;
    #           - Average files size;
    # *************************************************************************
    def statsModal(self):
        view = StatsModal()
        view.open()



class PrintersListButton(ListItemButton):
    pass



class ImageButton(ButtonBehavior, Image):
    pass



class ShowcaseScreen(Screen):
    fullscreen = BooleanProperty(False)
    api = None

    # Kivy ids
    printersIP = ObjectProperty()
    printersKey = ObjectProperty()
    printersList = ObjectProperty()
    printersListScreen2 = ObjectProperty()
    printersListScreen2MoreInfo = ObjectProperty()
    screenManager = ObjectProperty()
    screen = ObjectProperty()
    floatLayout = ObjectProperty()
    labelSearching = ObjectProperty()
    labelPrinters = ObjectProperty()
    spinnerStates = ObjectProperty()
    spinnerFilaments = ObjectProperty()
    labelFilterPrinters = ObjectProperty()
    boxLayoutLeft = ObjectProperty()
    stackLayout = ObjectProperty()


    # Global variables
    initialIdx = 14
    printersIPs = []
    printersKeysDict = {}
    lastPrintersColors = {}
    lastPrintersTemps = {}
    gridLayoutMoreInfo = None
    ip = None
    button = None
    pb = None
    lastState = None
    popUp = None
    popUp2 = None
    popUp3 = None
    clearPopUp = False
    image = None
    showScreen = False
    showLogoAndInfo = True
    tmpBee = None
    tmpInfo = None
    tmpInfoImage = None
    firstTime = True
    noFilter = False
    error = False
    tmpState = None
    selectedState = "All"
    selectedFilament = "All"
    colorHashMap = {'021': [0.95, 0.95, 0.95, 1], '022': [1, 1, 1, 1], '023': [0, 0, 0, 1], '024': [1, 0, 0, 1], '025': [1, 1, 0, 1],
                    '026': [0, 0, 1, 1], '027': [0.34, 0.42, 0.18, 1], '028': [1, 0, 0.5, 1], '029': [0.7, 0.7, 0.7, 1],
                    '030': [0.25, 0.96, 0.82, 1], '031': [0.22, 1, 0.08, 1],
                    '032': [1, 0.6, 0, 1], '101': [0.95, 0.95, 0.95, 1], '102': [1, 1, 1, 1], '103': [0.98, 0.78, 0.18, 1],
                    '104': [1, 0.66, 0.01, 1], '105': [0.730, 0.203, 0.062, 1], '106': [0.730, 0.117, 0.062, 1],
                    '107': [0.585, 0.179, 0.144, 1],
                    '108': [0.839, 0.625, 0.625, 1], '109': [0.562, 0.199, 0.449, 1], '110': [0.371, 0.144, 0.621, 1],
                    '111': [0.011, 0.484, 0.687, 1], '112': [0.011, 0.355, 0.546, 1], '113': [0.011, 0.218, 0.480, 1],
                    '114': [0.378, 0.597, 0.230, 1],
                    '115': [0.011, 0.542, 0.160, 1], '116': [0.214, 0.257, 0.183, 1], '117': [0.265, 0.183, 0.160, 1],
                    '118': [0.550, 0.570, 0.582, 1], '119': [0.156, 0.156, 0.156, 1], '120': [0.5	,  0.390,  0.246, 1]
                    ,'121' :[0.550,	0.570,	0.582, 1]}



    # *************************************************************************
    #       Init Function
    # *************************************************************************
    def __init__(self):
        super(self.__class__, self).__init__()
        self.api = APIMethods()
        # Add printers from 'printers.txt'
        self.addPrintersFromFile()
        Clock.schedule_interval(self._update_clock, 1 / 60.)
        Clock.schedule_interval(self.timer, 5)  # 5s in 5s




    # *************************************************************************
    #       Function creates a stack containing all printers main information
    #           - State - Represented as an image;
    #               - Closed/Ready/Connecting/Printing/Heating/Transferring;
    #           - Percentage of print process (If Printing);
    #           - Printer Temperature (If Heating)
    #           - Filament loaded color;
    # *************************************************************************
    def createStackLayout(self, tmpPrinters):
        try:
            for ip in tmpPrinters:
                connection = self.api.getConnection(ip, self.printersKeysDict[ip])
                result = self.api.getNozzlesAndFilament(ip, self.printersKeysDict[ip])
                color = result['filament'][1:4]

                if result == None:
                    try:
                        code = self.lastPrintersColors[ip]
                    except Exception as err:
                        code = (0.95, 0.95, 0.95)
                else:
                    try:
                        code = self.colorHashMap[color]
                    except Exception as err:
                        code = (0.95, 0.95, 0.95)

                # General for all states - No need to change
                self.lastPrintersColors[ip] = code

                if connection['state'] == 'Closed':
                    self.lastState = connection['state']
                    image = ImageButton(id=ip, size_hint=(None, .15), width=65, size=(80, 80),
                                        source=('images/closedT.png'),
                                        y=self.parent.y + self.parent.height / 4,
                                        x=self.parent.x + self.parent.width / 5)
                    self.stackLayout.add_widget(image)

                    tmpButton2 = Button(id=ip, background_color=(0, 0, 0, .1), font_size=18, text="PLA", color=(0, 0, 0, 1),
                                        size_hint=(.35, .15), width=30)
                    self.stackLayout.add_widget(tmpButton2)

                    tmpImage = Image(id=ip, size_hint=(.35, .15), color=code)
                    self.stackLayout.add_widget(tmpImage)

                    imageButton = ImageButton(id=ip, size_hint=(None, .15), width=45, size=(50, 50), source=('images/infoT.png'),
                                              y=self.parent.y + self.parent.height / 4,
                                              x=self.parent.x + self.parent.width / 5,
                                              on_press=self.showPrinterInfo)

                    self.stackLayout.add_widget(imageButton)

                elif connection['state'] == 'Ready':
                    self.lastState = connection['state']

                    image = ImageButton(id=ip, size_hint=(None, .15), width=60, size=(80, 80),
                                              source=('images/checkLittleT.png'),
                                              y=self.parent.y + self.parent.height / 4,
                                              x=self.parent.x + self.parent.width / 5)

                    self.stackLayout.add_widget(image)

                    tmpButton2 = Button(id=ip, background_color=(0, 0, 0, .1), font_size=18, text="PLA", color=(0,0,0,1), size_hint=(.35, .15), width=150)
                    self.stackLayout.add_widget(tmpButton2)

                    tmpImage = Image(id=ip, size_hint=(.35,.15), color=code)
                    self.stackLayout.add_widget(tmpImage)

                    imageButton = ImageButton(id=ip, size_hint=(None, .15), width=45, size=(50, 50), source=('images/infoT.png')
                                              ,y=self.parent.y + self.parent.height/4, x=self.parent.x+self.parent.width/5,
                                              on_press=self.showPrinterInfo)
                    self.stackLayout.add_widget(imageButton)

                elif connection['state'] == 'Heating':
                    self.lastState = connection['state']

                    temperature = self.api.getTemperatureOnHeating(ip, self.printersKeysDict[ip])
                    tmpTemp = int(temperature['temperature'])

                    if tmpTemp > 210:
                        tmpTemp = 210

                    self.lastPrintersTemps[ip] = str(tmpTemp)

                    image = ImageButton(id=ip, size_hint=(None, .15), width=60, size=(80, 80),
                                        source=('images/temperatureT.png'),
                                        y=self.parent.y + self.parent.height / 4,
                                        x=self.parent.x + self.parent.width / 5)
                    self.stackLayout.add_widget(image)

                    tmpButton2 = Button(id=ip, background_color=(0, 0, 0, .1), font_size=18, text=str(tmpTemp)+".0º/210.0ºC", color=(0, 0, 0, 1),
                                        size_hint=(.35, .15), width=150)
                    self.stackLayout.add_widget(tmpButton2)

                    tmpImage = Image(id=ip, size_hint=(.35, .15), color=code)
                    self.stackLayout.add_widget(tmpImage)

                    imageButton = ImageButton(id=ip, size_hint=(None, .15),  width=45, size=(50, 50),
                                              source=('images/infoT.png'),
                                              y=self.parent.y + self.parent.height / 4,
                                              x=self.parent.x + self.parent.width / 5,
                                              on_press=self.showPrinterInfo)
                    self.stackLayout.add_widget(imageButton)

                elif connection['state'] == 'Transferring':
                    self.lastState = connection['state']

                    job = self.api.getJobInfo(ip, self.printersKeysDict[ip])
                    progress = int(job['progress']['completion'])

                    # Something the API returns negative values
                    if progress < 0:
                        progress = 0

                    image = ImageButton(id=ip, size_hint=(None, .15), width=60, size=(80, 80),
                                        source=('images/transferringT.png'),
                                        y=self.parent.y + self.parent.height / 4,
                                        x=self.parent.x + self.parent.width / 5)
                    self.stackLayout.add_widget(image)

                    tmpButton2 = Button(id=ip, background_color=(0, 0, 0, .1), font_size=18, text=str(progress) + "%",
                                        color=(0, 0, 0, 1),
                                        size_hint=(.35, .15), width=150)
                    self.stackLayout.add_widget(tmpButton2)

                    tmpImage = Image(id=ip, size_hint=(.35, .15), color=code)
                    self.stackLayout.add_widget(tmpImage)

                    imageButton = ImageButton(id=ip, size_hint=(None, .15), width=45, size=(50, 50), source=('images/infoT.png'),
                                              y=self.parent.y + self.parent.height / 4,
                                              x=self.parent.x + self.parent.width / 5,
                                              on_press=self.showPrinterInfo)
                    self.stackLayout.add_widget(imageButton)

                elif connection['state'] == 'Printing':
                    self.lastState = connection['state']

                    job = self.api.getJobInfo(ip, self.printersKeysDict[ip])
                    progress = int(job['progress']['completion'])

                    # Something the API returns negative values
                    if progress < 0:
                        progress = 0

                    image = ImageButton(id=ip, size_hint=(None, .15), width=60, size=(80, 80),
                                        source=('images/print_Menu.png')
                                        , y=self.parent.y + self.parent.height / 4,
                                        x=self.parent.x + self.parent.width / 5)
                    self.stackLayout.add_widget(image)

                    tmpButton2 = Button(id=ip, background_color=(0, 0, 0, .1), font_size=18, text=str(progress)+"%", color=(0, 0, 0, 1),
                                        size_hint=(.35, .15), width=150)
                    self.stackLayout.add_widget(tmpButton2)

                    tmpImage = Image(id=ip, size_hint=(.35, .15), color=code)
                    self.stackLayout.add_widget(tmpImage)

                    imageButton = ImageButton(id=ip, size_hint=(None, .15),  width=45, size=(50, 50), source=('images/infoT.png'),
                                              y=self.parent.y + self.parent.height / 4,
                                              x=self.parent.x + self.parent.width / 5,
                                              on_press=self.showPrinterInfo)
                    self.stackLayout.add_widget(imageButton)

                elif connection['state'] == 'Connecting':
                    self.lastState = connection['state']

                    image = ImageButton(id=ip, size_hint=(None, .15), width=60, size=(80, 80),
                                        source=('images/connectingT.png')
                                        , y=self.parent.y + self.parent.height / 4,
                                        x=self.parent.x + self.parent.width / 5)
                    self.stackLayout.add_widget(image)

                    tmpButton2 = Button(id=ip, background_color=(0, 0, 0, .1), font_size=18, text="PLA", color=(0, 0, 0, 1),
                                        size_hint=(.35, .15), width=150)
                    self.stackLayout.add_widget(tmpButton2)

                    tmpImage = Image(id=ip, size_hint=(.35, .15), color=self.lastPrintersColors[ip])
                    self.stackLayout.add_widget(tmpImage)

                    imageButton = ImageButton(id=ip, size_hint=(None, .15), width=45, size=(50, 50),
                                              source=('images/infoT.png')
                                              , y=self.parent.y + self.parent.height / 4,
                                              x=self.parent.x + self.parent.width / 5,
                                              on_press=self.showPrinterInfo)
                    self.stackLayout.add_widget(imageButton)

                else:
                    print "SHOULD NOT ENTER HERE :)"

            # Add to left boxLayout
            self.boxLayoutLeft.add_widget(self.stackLayout)
        except Exception as err:
            print err.args

            image = ImageButton(id=ip, size_hint=(None, .15), width=60, size=(80, 80),
                                source=('images/transferringT.png'),
                                y=self.parent.y + self.parent.height / 4,
                                x=self.parent.x + self.parent.width / 5)
            self.stackLayout.add_widget(image)

            tmpButton2 = Button(id=ip, background_color=(0, 0, 0, .1), font_size=17, text="Stabilizing ...",
                                color=(0, 0, 0, 1),
                                size_hint=(.35, .15), width=150)
            self.stackLayout.add_widget(tmpButton2)

            tmpImage = Image(id=ip, size_hint=(.35, .15), color=self.lastPrintersColors[ip])
            self.stackLayout.add_widget(tmpImage)

            imageButton = ImageButton(id=ip, size_hint=(None, .15), width=45, size=(50, 50),
                                      source=('images/infoT.png'),
                                      y=self.parent.y + self.parent.height / 4,
                                      x=self.parent.x + self.parent.width / 5,
                                      on_press=self.showPrinterInfo)

            self.stackLayout.add_widget(imageButton)
            # Add to Left boxLayout
            self.boxLayoutLeft.add_widget(self.stackLayout)



    # *************************************************************************
    #       Function that enables the right gridLayout on a button click and shows the following information:
    #           - Printer Model;
    #           - Printer IP Address;
    #           - Printer Serial Number;
    #           - Printer loaded filament;
    #           - More info if the printer is Printing or Heating
    # *************************************************************************
    def showPrinterInfo(self, instance):
        self.ip = instance.id
        self.showScreen = True

        if self.tmpBee != None and self.tmpInfo != None and self.tmpInfoImage != None:
            self.screen.remove_widget(self.tmpBee)
            self.tmpBee = None
            self.screen.remove_widget(self.tmpInfo)
            self.screen.remove_widget(self.tmpInfoImage)
            self.tmpInfo = None
            self.tmpInfoImage = None
        try:
            self.updatePrintersInfo(self.ip)
        except Exception as err:
            print err.args
            self.generatePopUp("Printer not responding", "Verify if the cable is connected ...", "OK")



    # *************************************************************************
    #       Function that adds to the printers list the printers that
    #           are on the file ('printers.txt')
    # *************************************************************************
    def addPrintersFromFile(self):
        try:
            with open('printers.txt') as fp:
                for line in fp:
                    if len(line.strip()) != 0:
                        ipAndKey = line.split(", ")
                        # If ip not in list and gets response from api -> add
                        if len(ipAndKey) > 1:  # correct format
                            key = ipAndKey[1]
                            if "\n" in key:
                                key = key[0:len(key)-1]

                            if self.firstTime:
                                code = self.api.checkValidIpAndKey(ipAndKey[0], key)
                                if code != 200:
                                    if self.removeInvalidIpFromFile(ipAndKey[0], ipAndKey[1]) == -1:
                                        self.removeInvalidIpFromFileHardWay(ipAndKey[0], ipAndKey[1])

                                    labelText = "Could not get a response from %s ... \n %s removed from file" %(ipAndKey[0], ipAndKey[0])
                                    if not self.error:
                                        self.generatePopUp2("Invalid IP on file", labelText, "Ok")
                                        self.error = True
                                else:
                                    if ipAndKey[0] not in self.printersIPs and code == 200:
                                        self.addPrintersInfo(ipAndKey[0], key)
                            else:
                                if ipAndKey[0] not in self.printersIPs:
                                    self.addPrintersInfo(ipAndKey[0], key)
                fp.close()
                self.firstTime = False
        except Exception as err:
            print err.args



    # *************************************************************************
    #       Function that removes from the file a invalid IP or api key
    #           - To prevent deficient user behavior that could lead to errors
    # *************************************************************************
    def removeInvalidIpFromFile(self, ip, key=None):
        try:
            targetLine = "%s, %s" % (ip, key)
            f = open("printers.txt", "r+")
            d = f.readlines()
            f.seek(0)
            for i in d:
                if i != targetLine:
                    f.write(i)
                    f.write("\n")
            f.truncate()
            f.close()
            return 0
        except Exception as err:
            print err.args
            return -1



    # *************************************************************************
    #       Function that removes from the file a invalid IP or api key
    #           - To prevent deficient user behavior that could lead to errors
    # *************************************************************************
    def removeInvalidIpFromFileHardWay(self, ip, key=None):
        try:
            targetLine = "%s, %s" % (ip, key)
            f = open("printers.txt", "r+")
            d = f.readlines()
            f.seek(0)
            for i in d:
                if "\n" in i:
                    i = i[0:len(i)-1]
                if i != targetLine:
                    f.write(i)
                    f.write("\n")
            f.truncate()
            f.write("\n") # IMP
            self.generateWarning("Valid IP and Key", "Printer removed successfully", "OK")
            f.close()
            return 0
        except Exception as err:
            print err.args
            return -1



    # *************************************************************************
    #       Function that adds to the global list and dict the printers information
    # *************************************************************************
    def addPrintersInfo(self, printerIP, printerKey):
        self.printersIPs.append(printerIP)
        self.printersKeysDict[printerIP] = printerKey



    # *************************************************************************
    #       To enable widgets add option
    # *************************************************************************
    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(ShowcaseScreen, self).add_widget(*args)




    def _update_clock(self, dt):
        self.time = time()



    # *************************************************************************
    #       Function that finds the position of a given ip on the printers list
    # *************************************************************************
    def findPos(self, replaceIP, listIPs):
        idx = 0
        for ip in listIPs:
            if replaceIP == ip:
                return idx
            idx = idx + 1
        return -1



    # *************************************************************************
    #       Function that creates a Modal View on button click
    # *************************************************************************
    def modalViewPrinter(self, textModal):
        view = ModalViewCustom(size_hint=(None, None))
        view.add_widget(Label(size_hint=(None, None), pos_hint={'center_x': .5, 'center_y': .8},
                              text=textModal, font_size="17", color=(0, 0, 0, 1)))
        view.open()



    # *************************************************************************
    #       Function called on the timer
    #           - Updates the right detailed information grid
    # *************************************************************************
    def updatePrintersInfo(self, ip=None):
        if self.button != None:
            self.screen.remove_widget(self.button)
        if self.image != None:
            self.screen.remove_widget(self.image)

        if ip != None:
            if self.gridLayoutMoreInfo != None:
                self.gridLayoutMoreInfo.clear_widgets()
                if self.button != None:
                    self.floatLayout.remove_widget(self.button)
                if self.pb != None:
                    self.floatLayout.remove_widget(self.pb)

            # Create grid Layout based on the ip selected and correspondent state
            # Get key to api call
            key = self.printersKeysDict[ip]
            # Call api
            connection = self.api.getConnection(ip, key)
            serialNum = self.api.getSerialNum(ip, key)
            namePrinter = self.api.getName(ip, key)
            resultFilament = self.api.getFilament(ip, key)

            if resultFilament['filament'] == None or resultFilament == "Printer is not operational":
                filament = "Still stabilizing ..."
            else:
                filament = resultFilament['filament']

            # TODO - FUTURE WORK - Live Image Stream
            self.image = Image(source=self.getImage(), pos_hint={"x": 0.23, "top": 1.17})

            self.gridLayoutMoreInfo = GridLayout(cols=2, pos_hint={"x": .55, "top": .5}, size_hint=(.35, .3), text_size=15)
            self.gridLayoutMoreInfo.add_widget(Label(text='[i]IP ADDRESS:[/i]', font_size=18, markup=True, color=(0, 0, 0, 1)))
            self.gridLayoutMoreInfo.add_widget(Label(text=str(ip), color=(0, 0, 0, 1)))
            self.gridLayoutMoreInfo.add_widget(Label(text='[i]SERIAL NUMBER:[/i]', font_size=18, markup=True, color=(0, 0, 0, 1)))
            self.gridLayoutMoreInfo.add_widget(Label(text=str(serialNum['serial']), color=(0, 0, 0, 1)))
            self.gridLayoutMoreInfo.add_widget(Label(text='[i]MODEL:[/i]', font_size=18, markup=True, color=(0, 0, 0, 1)))
            self.gridLayoutMoreInfo.add_widget(Label(text=namePrinter['printer'], color=(0, 0, 0, 1)))
            self.gridLayoutMoreInfo.add_widget(Label(text='[i]LOADED FILAMENT:[/i]', font_size=18, markup=True, color=(0, 0, 0, 1)))
            self.gridLayoutMoreInfo.add_widget(Label(text=filament, color=(0,0,0,1)))

            # Add gridLayoutFilePrinting
            if connection['state'] == 'Transferring' or connection['state'] == 'Printing':
                job = self.api.getJobInfo(ip, key)
                self.gridLayoutMoreInfo.add_widget(Label(text='[i]FILE BEING PRINTED:[/i] ', font_size=18, markup=True, color=(0, 0, 0, 1)))

                gridLayoutFilePrinting = GridLayout(cols=1, pos_hint={"right": 1, "top": .8}, row_force_default=True,
                                                    row_default_height=40)
                self.gridLayoutMoreInfo.add_widget(gridLayoutFilePrinting)
                try:
                    if job['progress']['printTimeLeft'] == None:
                        printTimeLeft = "Still stabilizing ..."
                        printTimeLeftStr = printTimeLeft
                    else:
                        printTimeLeft = int(job['progress']['printTimeLeft'])/60
                        if printTimeLeft == 1:
                            printTimeLeftStr = "a minute"
                        elif printTimeLeft < 1:
                            printTimeLeftStr = "a couple of seconds"
                        else:
                            printTimeLeftStr = "%s minutes" % (printTimeLeft)

                    fileBeingPrinted = job['job']['file']['name']

                    filamentLength = round((float(job['job']['filament']['tool0']['length']) / 1000), 2)
                    filamentVolume = round((float(job['job']['filament']['tool0']['volume'])), 2)

                    filamentInfo = "Filament (Tool 0): %sm/%scm^3" % (str(filamentLength), str(filamentVolume))
                    gridLayoutFilePrinting.add_widget(Label(text=filamentInfo, color=(0, 0, 0, 1)))
                    gridLayoutFilePrinting.add_widget(Label(text=fileBeingPrinted, color=(0, 0, 0, 1)))
                    # Progress bar
                    # If negative, turn equals to 0
                    completion = 0
                    progressBar = 0
                    if int(job['progress']['completion']) >= 0:
                        progressBar = int(job['progress']['completion'])
                        completion = int(job['progress']['completion'])
                    completion = str(completion)+"%"

                    if printTimeLeft == "Still stabilizing ...":
                        completionAndLeft = printTimeLeft
                    else:
                        completionAndLeft = "%s (%s remaining)" %(completion,printTimeLeftStr)

                    gridLayoutFilePrinting.add_widget(Label(text=completionAndLeft, color=(0, 0, 0, 1)))
                    # Progress bar
                    self.pb = ProgressBar(max=100, value=progressBar, pos_hint={"x": 0.743, "top": .61}, size_hint_x=(.14))
                    self.floatLayout.add_widget(self.pb)

                    self.button = Button(id="buttonPrint", text="GO TO PRINTER ...",
                                                              background_color=(0, 1, 0, .7), pos_hint={"x": 0.57, "top": .09}, size_hint=(.36, 0.08),
                                                              on_press=self.redirectPrint)
                except KeyError as err:
                    print err.args
                    gridLayoutFilePrinting.add_widget(Label(text="Could not retrieve info ...", color=(0, 0, 0, 1)))
                    gridLayoutFilePrinting.add_widget(Label(text="Check if there's some problem with the printer ...", color=(0, 0, 0, 1)))
                    self.button = Button(id="buttonPrint", text="PRINT ...",
                                         background_color=(0, 1, 0, .7), pos_hint={"x": 0.57, "top": .2}, size_hint=(.305, 0.08),
                                         on_press=self.redirectPrint)

            elif connection['state'] == "Ready":
                self.button = Button(id="buttonPrint", text="PRINT ...",
                                                   background_color=(0, 1, 0, .7), pos_hint={"x": 0.57, "top": .2},
                                                   size_hint=(.305, 0.08),
                                                   on_press=self.redirectPrint)

            elif connection['state'] == "Heating":
                # Temperature
                temperature = self.api.getTemperatureOnHeating(ip, key)
                self.gridLayoutMoreInfo.add_widget(Label(text='[i]TEMPERATURE:[/i]', font_size=18, markup=True, color=(0, 0, 0, 1)))
                temp = int(temperature['temperature'])
                # If greater than 210, turn 210
                if temp > 210:
                    temp = 210
                self.gridLayoutMoreInfo.add_widget(Label(text=str(temp)+".0º"+"/210ºC", color=(0, 0, 0, 1)))
                self.button = Button(id="buttonPrint", text="PRINT ...",
                                     background_color=(0, 1, 0, .7), pos_hint={"x": 0.57, "top": .2},
                                     size_hint=(.305, 0.08),
                                     on_press=self.redirectPrint)
            else:
                print "SHOULD NOT ENTER HERE :)"

            self.screen.add_widget(self.image)
            self.screen.add_widget(self.gridLayoutMoreInfo)
            self.screen.add_widget(self.button)


    # *************************************************************************
    #       Function that returns a live image from a printer webcam
    # *************************************************************************
    # TODO - FUTURE WORK - LIVE WEBCAM STREAM ON THE PRINTERS
    def getImage(self):
        # return image depending on the selected ip
        return 'images/cam.png'



    # *************************************************************************
    #       Function that redirects the user to the printer browser page
    # *************************************************************************
    def redirectPrint(self, error):
        ip = self.api.checkIfLocalhost(self.ip)
        url = "http://%s/" %(ip)
        webbrowser.open_new_tab(url)



    # *************************************************************************
    #       Function that closes the current PopUp
    # *************************************************************************
    def dismissPopUp(self, ip):
        self.floatLayout.remove_widget(self.popUp)



    # *************************************************************************
    #       Function that closes the current PopUp
    # *************************************************************************
    def dismissPopUp2(self, ip):
        self.floatLayout.remove_widget(self.popUp2)



    # *************************************************************************
    #       Function that closes the current PopUp
    # *************************************************************************
    def dismissPopUp3(self, ip):
        self.screen.remove_widget(self.popUp3)



    # *************************************************************************
    #       Function that generates a PopUp
    # *************************************************************************
    def generatePopUp(self, titleText, labelText, buttonText):
        self.popUp = PopUpWarning(title=titleText, pos_hint={'center_x': .5, 'center_y': .5})
        float = FloatLayout()
        label = Label(size_hint=(.4, .3), pos_hint={'center_x': .5, 'center_y': .7},
                      text=labelText, font_size="17", color=(0, 0, 0, 1))
        button = Button(pos_hint={'center_x': .5, 'center_y': .3}, size_hint=(.8, .3), size=(150, 50),
                        text=buttonText,
                        on_press=self.dismissPopUp)
        float.add_widget(label)
        float.add_widget(button)
        self.popUp.add_widget(float)
        self.floatLayout.add_widget(self.popUp)



    # *************************************************************************
    #       Function that generates a PopUp
    # *************************************************************************
    def generatePopUp2(self, titleText, labelText, buttonText):
        self.popUp2 = PopUpWarning(title=titleText, pos_hint={'center_x': .5, 'center_y': .5})
        float = FloatLayout()
        label = Label(size_hint=(.4, .3), pos_hint={'center_x': .5, 'center_y': .7},
                      text=labelText, font_size="17", color=(0, 0, 0, 1))
        button = Button(pos_hint={'center_x': .5, 'center_y': .3}, size_hint=(.8, .3), size=(150, 50),
                        text=buttonText,
                        on_press=self.dismissPopUp2)
        float.add_widget(label)
        float.add_widget(button)
        self.popUp2.add_widget(float)
        self.floatLayout.add_widget(self.popUp2)



    # *************************************************************************
    #       Function that generates a PopUp
    # *************************************************************************
    def generatePopUp3(self, titleText, labelText, buttonText):
        self.popUp3 = PopUpWarning(title=titleText, pos_hint={'center_x': .5, 'center_y': .5})
        float = FloatLayout()
        label = Label(size_hint=(.4, .3), pos_hint={'center_x': .5, 'center_y': .7},
                      text=labelText, font_size="17", color=(0, 0, 0, 1))
        button = Button(pos_hint={'center_x': .5, 'center_y': .3}, size_hint=(.8, .3), size=(150, 50),
                        text=buttonText,
                        on_press=self.dismissPopUp3)
        float.add_widget(label)
        float.add_widget(button)
        self.popUp3.add_widget(float)
        self.screen.add_widget(self.popUp3)



    # *************************************************************************
    #       Function that filters the printers depending on the spinner values
    #           - Spinners Available:
    #               - State;
    #               - Loaded Filament;
    # *************************************************************************
    def filterPrinters(self):
        tmpStates = {}
        tmpFilaments = {}
        try:
            for ip in self.printersIPs:
                connection = self.api.getConnection(ip, self.printersKeysDict[ip])
                result = self.api.getNozzlesAndFilament(ip, self.printersKeysDict[ip])
                tmpStates[ip] = connection['state']
                tmpFilaments[ip] = result['filament']

            tmpPrinters = []
            finalPrinters = []
            if self.selectedState != "All" and self.selectedState != "State":
                for ip in tmpStates:
                    if tmpStates[ip] == self.selectedState:
                        tmpPrinters.append(ip)
            else:
                tmpPrinters = self.printersIPs

            # Iterate over tmpPrinters
            if self.selectedFilament != "All" and self.selectedFilament != "Filament":
                for ip in tmpPrinters:
                    if tmpFilaments[ip] == self.selectedFilament:
                        finalPrinters.append(ip)
            else:
                finalPrinters = tmpPrinters

        except Exception as err:
            print err.args
            finalPrinters = self.printersIPs

        return finalPrinters



    # *************************************************************************
    #       Function that checks if any printer was removed from the file
    # *************************************************************************
    def checkIfDeleted(self):

        # If the file is empty
        if os.path.getsize('printers.txt') == 0:
            print self.printersIPs
            try:
                for i in range(0,len(self.printersIPs)):
                    ip = self.printersIPs[i]

                    self.printersIPs.pop(i)
                    self.boxLayoutLeft.clear_widgets()
                    self.stackLayout.clear_widgets()

                    if self.gridLayoutMoreInfo != None:
                        self.gridLayoutMoreInfo.clear_widgets()
            except Exception:
                self.screen.remove_widget(self.image)
                if self.gridLayoutMoreInfo != None:
                    self.gridLayoutMoreInfo.clear_widgets()
        # If the file is not empty
        else:
            try:
                printersFromFile = []
                with open("printers.txt") as fp:
                    for line in fp:
                        if line != "\n":
                            ipAndKey = line.split(", ")
                            # if ip not in list and gets response from api -> add
                            printersFromFile.append(ipAndKey[0])
                fp.close()


                for ip in self.printersIPs:
                    if ip not in printersFromFile:
                        idx = self.findPos(ip, self.printersIPs)

                        self.printersIPs.pop(idx)
                        if self.gridLayoutMoreInfo != None:
                            self.gridLayoutMoreInfo.clear_widgets()

                        if self.floatLayout != None and self.pb != None:
                            self.floatLayout.remove_widget(self.pb)

                        # Remove elements of stack layout
                        for child in self.stackLayout.children[:]:
                            if child.id == ip:
                                self.stackLayout.remove_widget(child)

                        self.showScreen = False
                        self.screen.remove_widget(self.button)
                        self.screen.remove_widget(self.image)
                        if self.gridLayoutMoreInfo != None:
                            self.gridLayoutMoreInfo.clear_widgets()
            except Exception as err:
                print err.args
                self.showScreen = False
                if self.button != None:
                    self.screen.remove_widget(self.button)
                if self.image != None:
                    self.screen.remove_widget(self.image)
                if self.gridLayoutMoreInfo != None:
                    self.gridLayoutMoreInfo.clear_widgets()


    def timer(self, dt):
        self.addPrintersFromFile()
        # If file exists
        if os.path.isfile("printers.txt"):
            self.checkIfDeleted()

        try:
            if len(self.printersIPs) != 0:
                # Enable spinners filters
                self.spinnerStates.opacity = 1
                self.spinnerFilaments.opacity = 1
                self.labelFilterPrinters.opacity = 1

                try:
                    if self.boxLayoutLeft != None:
                        self.boxLayoutLeft.clear_widgets()
                    if self.stackLayout != None:
                        self.stackLayout.clear_widgets()

                    tmpPrinters = self.filterPrinters()

                    if len(tmpPrinters) != 0:
                        self.noFilter = False
                        self.createStackLayout(tmpPrinters)
                    else:
                        # Clear gridLayoutMoreInfo, button and image
                        if self.gridLayoutMoreInfo != None:
                            self.gridLayoutMoreInfo.clear_widgets()
                        if self.image != None:
                            self.screen.remove_widget(self.image)
                        if self.button != None:
                            self.screen.remove_widget(self.button)

                        self.noFilter = True
                        if self.popUp3 == None:
                            self.generatePopUp3("No printers founds ...", "Try to change the search filters", "OK")
                except Exception as err:
                    print "OUPA"
                    print err.args
                    #
                    print "TMP PRINTERS: ",tmpPrinters
                    tmpPrinters = self.filterPrinters()
                    self.createStackLayout(tmpPrinters)

                self.boxLayoutLeft.opacity = 1
                tmpStates = []
                tmpFilaments = []

                for ip in self.printersIPs:
                    connection = self.api.getConnection(ip, self.printersKeysDict[ip])
                    resultFilament = self.api.getFilament(ip, self.printersKeysDict[ip])
                    if connection['state'] not in tmpStates:
                        tmpStates.append(str(connection['state']))

                    if resultFilament['filament'] not in tmpFilaments:
                        tmpFilaments.append(str(resultFilament['filament']))
                # Append to dropdown the 'All' item
                tmpStates.append("All")
                tmpFilaments.append("All")

                self.spinnerStates.values = tmpStates
                self.spinnerFilaments.values = tmpFilaments
                self.selectedState = self.spinnerStates.text
                self.selectedFilament = self.spinnerFilaments.text
            else:
                # Clear dropdowns and labels
                if self.spinnerFilaments != None and self.spinnerStates != None:
                    self.spinnerStates.opacity = 0
                    self.spinnerFilaments.opacity = 0
                    self.labelFilterPrinters.opacity = 0
        except Exception as err:
            print err.args

        if self.showScreen and not self.noFilter:
            try:
                self.updatePrintersInfo(self.ip)
            except Exception as err:
                print err.args
        else:
            if self.showLogoAndInfo:
                self.tmpBee = Image(size=(600,600), pos_hint={'center_x': .8, 'center_y': .5}, source="images/beeLogo.png")
                self.screen.add_widget(self.tmpBee)
                if len(self.printersIPs) != 0:
                    info = "(Click on the available printers for more info)"
                    self.tmpInfoImage = ImageButton(pos_hint={'center_x': .97, 'center_y': .3}, size_hint=(None, .25),
                                                    width=45, size=(50, 50),
                                                    source=('images/infoT.png'),
                                                    y=self.parent.y + self.parent.height / 4,
                                                    x=self.parent.x + self.parent.width / 5)
                else:
                    info = "(Click on the printers for more info)\n    Go to settings to add printers ..."

                self.tmpInfo = Label(text=info, font_size=20,
                                     color=(0, 0, 0, 1), pos_hint={'center_x': .8, 'center_y': .3})

                self.screen.add_widget(self.tmpInfo)
                if self.tmpInfoImage != None:
                    self.screen.add_widget(self.tmpInfoImage)
                self.showLogoAndInfo = False

        self.labelSearching.color = (0, 0, 0, 0)
        self.labelPrinters.color = (0, 0, 0, 1)
        connectedPrinters = str(len(self.printersIPs))
        self.labelPrinters.text = "Connected Printers: %s" % connectedPrinters

        if len(self.printersIPs) == 0 and not self.clearPopUp:
            self.generatePopUp("No printers found", "Go to settings to add ...", "OK")
            self.clearPopUp = True


class ShowcaseApp(App):

    index = NumericProperty(-1)
    current_title = StringProperty()
    time = NumericProperty(0)
    show_sourcecode = BooleanProperty(False)
    sourcecode = StringProperty()
    screen_names = ListProperty([])
    hierarchy = ListProperty([])

    def build(self):
        self.title = 'BeeVeryCreative - BeeBoard'
        self.screens = {}
        self.available_screens = list(['ScreenManager'])
        self.screen_names = self.available_screens
        curdir = dirname(__file__)
        self.available_screens = [join(curdir, 'data', 'screens',
            '{}.kv'.format(fn).lower()) for fn in self.available_screens]
        self.go_next_screen()

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def go_previous_screen(self):
        self.index = (self.index - 1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='right')
        self.current_title = screen.name
        self.update_sourcecode()

    def go_next_screen(self):
        self.index = (self.index + 1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='left')
        self.current_title = screen.name
        self.update_sourcecode()

    def go_screen(self, idx):
        self.index = idx
        self.root.ids.sm.switch_to(self.load_screen(idx), direction='left')
        self.update_sourcecode()

    def go_hierarchy_previous(self):
        ahr = self.hierarchy
        if len(ahr) == 1:
            return
        if ahr:
            ahr.pop()
        if ahr:
            idx = ahr.pop()
            self.go_screen(idx)

    def load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = Builder.load_file(self.available_screens[index])
        self.screens[index] = screen
        return screen

    def read_sourcecode(self):
        fn = self.available_screens[self.index]
        with open(fn) as fd:
            return fd.read()

    def toggle_source_code(self):
        self.show_sourcecode = not self.show_sourcecode
        if self.show_sourcecode:
            height = self.root.height * .3
        else:
            height = 0

        Animation(height=height, d=.3, t='out_quart').start(
                self.root.ids.sv)

        self.update_sourcecode()

    def update_sourcecode(self):
        if not self.show_sourcecode:
            self.root.ids.sourcecode.focus = False
            return
        self.root.ids.sourcecode.text = self.read_sourcecode()
        self.root.ids.sv.scroll_y = 1

    def showcase_floatlayout(self, layout):

        def add_button(*t):
            if not layout.get_parent_window():
                return
            if len(layout.children) > 5:
                layout.clear_widgets()
            layout.add_widget(Builder.load_string('''
#:import random random.random
Button:
    size_hint: random(), random()
    pos_hint: {'x': random(), 'y': random()}
    text:
        'size_hint x: {} y: {}\\n pos_hint x: {} y: {}'.format(\
            self.size_hint_x, self.size_hint_y, self.pos_hint['x'],\
            self.pos_hint['y'])
'''))
            Clock.schedule_once(add_button, 1)
        Clock.schedule_once(add_button)

    def showcase_boxlayout(self, layout):

        def add_button(*t):
            if not layout.get_parent_window():
                return
            if len(layout.children) > 5:
                layout.orientation = 'vertical'\
                    if layout.orientation == 'horizontal' else 'horizontal'
                layout.clear_widgets()
            layout.add_widget(Builder.load_string('''
Button:
    text: self.parent.orientation if self.parent else ''
'''))
            Clock.schedule_once(add_button, 1)
        Clock.schedule_once(add_button)

    def showcase_gridlayout(self, layout):

        def add_button(*t):
            if not layout.get_parent_window():
                return
            if len(layout.children) > 15:
                layout.rows = 3 if layout.rows is None else None
                layout.cols = None if layout.rows == 3 else 3
                layout.clear_widgets()
            layout.add_widget(Builder.load_string('''
Button:
    text:
        'rows: {}\\ncols: {}'.format(self.parent.rows, self.parent.cols)\
        if self.parent else ''
'''))
            Clock.schedule_once(add_button, 1)
        Clock.schedule_once(add_button)

    def showcase_stacklayout(self, layout):
        orientations = ('lr-tb', 'tb-lr',
                        'rl-tb', 'tb-rl',
                        'lr-bt', 'bt-lr',
                        'rl-bt', 'bt-rl')

        def add_button(*t):
            if not layout.get_parent_window():
                return
            if len(layout.children) > 11:
                layout.clear_widgets()
                cur_orientation = orientations.index(layout.orientation)
                layout.orientation = orientations[cur_orientation - 1]
            layout.add_widget(Builder.load_string('''
Button:
    text: self.parent.orientation if self.parent else ''
    size_hint: .2, .2
'''))
            Clock.schedule_once(add_button, 1)
        Clock.schedule_once(add_button)

    def showcase_anchorlayout(self, layout):

        def change_anchor(self, *l):
            if not layout.get_parent_window():
                return
            anchor_x = ('left', 'center', 'right')
            anchor_y = ('top', 'center', 'bottom')
            if layout.anchor_x == 'left':
                layout.anchor_y = anchor_y[anchor_y.index(layout.anchor_y) - 1]
            layout.anchor_x = anchor_x[anchor_x.index(layout.anchor_x) - 1]

            Clock.schedule_once(change_anchor, 1)
        Clock.schedule_once(change_anchor, 1)

    def _update_clock(self, dt):
        self.time = time()


if __name__ == '__main__':
    ShowcaseApp().run()