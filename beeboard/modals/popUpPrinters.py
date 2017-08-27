from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from api.api import APIMethods
from modals.modalViewCustom import ModalViewCustom
from modals.modalViewCustom import PopUpWarning


class PopUpPrinters(ModalView):

    # kv
    printersIP = ObjectProperty()
    printersKey = ObjectProperty()
    printersList = ObjectProperty()

    # py
    initialIdx = 14
    printersIPs = []
    printersKeysDict = {}
    popUp = None


    # ****************************************************************************************
    #       Init function
    # ****************************************************************************************
    def __init__(self):
        super(self.__class__, self).__init__()
        self.getPrintersFromFile(self.printersList)



    # ****************************************************************************************
    #       Function that checks what printers are on the printers file:
    #           - 'printers.txt'
    # ****************************************************************************************
    def getPrintersFromFile(self, printersList):
        # Check if list is empty
        if len(self.printersIPs) != 0:
            for ip in self.printersIPs:
                printer = "Printer: {IP: " + ip + ", Key: " + self.printersKeysDict[ip] + "}"
                # Add to ListView
                printersList.adapter.data.extend([printer])
                # Reset the ListView
                printersList._trigger_reset_populate()
        try:
            with open('printers.txt') as fp:
                for line in fp:
                    ipAndKey = line.split(", ")
                    # check if has empty lines in the middle of the file
                    if len(line.strip()) != 0:
                        key = ipAndKey[1]
                        if "\n" in key:
                            key = key[0:len(key)-1]
                        if ipAndKey[0] not in self.printersIPs:
                            printer = "Printer: {IP: " + ipAndKey[0] + ", Key: " + key + "}"
                            # Add to ListView
                            printersList.adapter.data.extend([printer])
                            # Reset the ListView
                            printersList._trigger_reset_populate()
                            # Add printer to global array and dict
                            self.addPrintersInfo(ipAndKey[0], key)
        except Exception as err:
            print err.args



    # ****************************************************************************************
    #       Function that adds printers to the data structures:
    #           - printersIPs - List of IP printers;
    #           - printersKeysDict - Dict of IPs and corresponding Keys;
    # ****************************************************************************************
    def addPrintersInfo(self, printerIP, printerKey):
        if printerIP not in self.printersIPs:
            self.printersIPs.append(printerIP)
            self.printersKeysDict[printerIP] = printerKey



    # ****************************************************************************************
    #       Function that closes the current PopUp
    # ****************************************************************************************
    def dismissPopUp(self, pi):
        self.remove_widget(self.popUp)



    # ****************************************************************************************
    #       Function that verifies if the IP and Key are valid to add to the printers list
    # ****************************************************************************************
    def checkValidIpAndKeyPopUp(self, ip, key, message):
        self.api = APIMethods()
        code = self.api.checkValidIpAndKey(ip, key)
        if code != 200:
            # Generate error popup ...
            warning = "Couldn't get a response on %s..." % (ip)
            self.generateWarning("Invalid IP or Key", warning, "REPLACE/DELETE")
        else:
            # Valid ip and key
            self.generateWarning("Valid IP and Key", message, "OK")
            # Write to file
            self.writeToFile(ip, key)



    # ****************************************************************************************
    #       Function that generates a PopUp Warning
    # ****************************************************************************************
    def generateWarning(self, title, warning, buttonText):
        self.popUp = PopUpWarning(title=title)
        float = FloatLayout()
        label = Label(size_hint=(.4, .3), pos_hint={'center_x': .5, 'center_y': .7},
                      text=warning, font_size="17", color=(0, 0, 0, 1))
        button = Button(pos_hint={'center_x': .5, 'center_y': .3}, size_hint=(.8, .3), size=(150, 50), text=buttonText,
                        on_press=self.dismissPopUp)
        float.add_widget(label)
        float.add_widget(button)
        self.popUp.add_widget(float)
        self.add_widget(self.popUp)


    # ****************************************************************************************
    #       Function that writes a printer to a file
    #           - Write process in file: <ip>, <key>
    # ****************************************************************************************
    def writeToFile(self, ip, key):
        with open("printers.txt", "ab") as file:
            file.write("\n")
            file.write(ip)
            file.write(", ")
            file.write(key)
            file.write("\n")
        file.close()



    # ****************************************************************************************
    #       Function that creates a warning PopUp
    # ****************************************************************************************
    def popUpWarning(self, textModal):
        view = PopUpWarning(size_hint=(None, None))
        view.add_widget(Label(size_hint=(None, None), pos_hint={'center_x': .5, 'center_y': .8},
                              text=textModal, font_size="17", color=(0, 0, 0, 1)))
        view.open()


    # ****************************************************************************************
    #       Function that creates a Modal
    # ****************************************************************************************
    def modalViewPrinter(self, textModal):
        view = ModalViewCustom(size_hint=(None, None))
        view.add_widget(Label(size_hint=(None, None), pos_hint={'center_x': .5, 'center_y': .8},
                              text=textModal, font_size="17", color=(0, 0, 0, 1)))
        view.open()


    # ****************************************************************************************
    #       Function that checks if the selected IP already exists in the List
    # ****************************************************************************************
    def checkIpExists(self, ip, listPrinters):
        if ip in listPrinters:
            return True
        return False



    # ****************************************************************************************
    #       Function that adds a printer
    # ****************************************************************************************
    def addPrinter(self, printersList):
        if len(printersList.adapter.selection) > 1:
            print printersList.adapter.selection[1].text
        if len(self.printersIP.text) != 0 and not self.checkIpExists(self.printersIP.text, self.printersIPs):
            printer = "Printer: {IP: " + self.printersIP.text + ", Key: " + self.printersKey.text + "}"
            # Add to ListView
            printersList.adapter.data.extend([printer])
            # Reset the ListView
            printersList._trigger_reset_populate()
            self.addPrintersInfo(str(self.printersIP.text), str(self.printersKey.text))
            self.checkValidIpAndKeyPopUp(str(self.printersIP.text), str(self.printersKey.text), "Printer added successfully")
        else:
            warning = "It exists or invalid format..."
            self.generateWarning("Error on adding printer", warning, "OK")



    # ****************************************************************************************
    #       Function that replaces a printer
    # ****************************************************************************************
    def replacePrinter(self, printersList):
        # If a list item is selected
        if printersList.adapter.selection:
            # Get the text from the selected item
            selection = printersList.adapter.selection[0].text
            [replaceIP, replaceKey] = self.getIpAndKey(selection, self.initialIdx, int(selection.find(",")),
                                                     int(selection.find(",")), -1)

            if len(self.printersIP.text) != 0 and self.printersIP.text not in self.printersIPs:
                # Remove the matching item
                printersList.adapter.data.remove(selection)
                # Remove the Key from the dict
                self.printersKeysDict.pop(replaceIP)
                # Get the text from the selected item
                printer = "Printer: {IP: " + self.printersIP.text + ", Key: " + self.printersKey.text + "}"
                # Add the updated data to the list
                printersList.adapter.data.extend([printer])
                # Reset the ListView
                printersList._trigger_reset_populate()
                # Replace on the list
                idxIP = self.findPos(self.printersIP.text, self.printersIPs)
                self.printersIPs[idxIP] = str(self.printersIP.text)
                self.printersKeysDict[str(self.printersIP.text)] = str(self.printersKey.text)
                # replace on the file
                self.checkValidIpAndKeyPopUp(self.printersIP.text, self.printersKey.text, "Printer replaced successfully")
            else:
                # Generate a warning popUp
                warning = "It exists or invalid format..."
                self.generateWarning("Error on replacing printer", warning, "OK")
        else:
            warning = "No printer selected..."
            self.generateWarning("Error on replacing printer", warning, "OK")



    # ****************************************************************************************
    #       Function that deletes a printer
    # ****************************************************************************************
    def deletePrinter(self, printersList):
        # If a list item is selected
        if printersList.adapter.selection:
            # Get the text from the selected item
            selection = printersList.adapter.selection[0].text
            # Remove the matching item
            printersList.adapter.data.remove(selection)
            # Reset the ListView
            printersList._trigger_reset_populate()
            # Replace on list
            [deleteIP, deleteKey] = self.getIpAndKey(selection, self.initialIdx, int(selection.find(",")), int(selection.find(","))+7, -1)
            idxIP = self.findPos(deleteIP, self.printersIPs)
            self.printersIPs.pop(idxIP)
            self.printersKeysDict.pop(deleteIP)
            # delete on the file
            self.removeFromFile(deleteIP, deleteKey)
        else:
            warning = "No printer selected..."
            self.generateWarning("Error on deleting printer", warning, "OK")



    # ****************************************************************************************
    #       Function that removes a printer in the file
    # ****************************************************************************************
    def removeFromFile(self, ip, key):
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



    # ****************************************************************************************
    #       Function that returns the IP and key in a tuple format
    # ****************************************************************************************
    def getIpAndKey(self, sel, initialIdxIP, finalIdxIP, initialIdxKey, finalIdxKey):
        IP = sel[initialIdxIP:finalIdxIP]
        Key = sel[initialIdxKey:finalIdxKey]
        return [IP, Key]



    # ****************************************************************************************
    #       Function that finds the position of the IP on the printers list
    # ****************************************************************************************
    def findPos(self, replaceIP, listIPs):
        idx = 0
        for ip in listIPs:
            if replaceIP == ip:
                return idx
            idx = idx + 1
        return -1