
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView

from api.api import APIMethods
import math


class StatsModal(ModalView):

    # Kivy
    labelConnectedPrinters = ObjectProperty()
    labelNextPrinterToFinish = ObjectProperty()
    labelAvgFilesSize = ObjectProperty()
    labelPrintingPrinters = ObjectProperty()
    boxLayoutNextPrinter = ObjectProperty()
    boxLayoutAvgFilesSize = ObjectProperty()

    # global
    printersDicStatsModal = {}
    avgFilesSizeList = {}
    printersStates = {}
    printersPrintTime = {}
    printersTime = []
    api = None
    nrPrintersPrinting = 0


    # ****************************************************************************************
    #       Init Function
    # ****************************************************************************************
    def __init__(self):
        super(self.__class__, self).__init__()
        self.getPrintersFromFile()
        self.api = APIMethods()
        self.populateStatsModal()


    # ****************************************************************************************
    #       Function that populates the statistics Modal:
    #           - Connected Printers;
    #           - Printers currently printing;
    #           - Next printer to finish print;
    #           - Average files size;
    # ****************************************************************************************
    def populateStatsModal(self):
        self.labelConnectedPrinters.text = str(len(self.printersDicStatsModal))
        self.labelPrintingPrinters.text = self.returnNumberPrintingPrinters()
        self.labelNextPrinterToFinish.text = self.returnNextPrinterToFinish()
        self.labelAvgFilesSize.text = self.returnAvgFilesSize()


    # ****************************************************************************************
    #       Functions that returns the number of printers currently printing
    # ****************************************************************************************
    def returnNumberPrintingPrinters(self):
        for ip in self.printersDicStatsModal:
            try:
                job = self.api.getJobInfo(ip, self.printersDicStatsModal[ip])
                self.printersStates[ip] = job['state']
            except Exception as err:
                print err.args
        self.nrPrintersPrinting = sum( state == 'Printing' for state in self.printersStates.values())
        return str(sum( state == 'Printing' for state in self.printersStates.values()))


    # ****************************************************************************************
    #       Function that returns the next printer to finish print
    # ****************************************************************************************
    def returnNextPrinterToFinish(self):
        # Clean
        self.printersPrintTime = {}
        self.printersTime = []
        self.boxLayoutNextPrinter.size_hint_x = .68
        self.boxLayoutNextPrinter.pos_hint = {'center_x': .493, 'center_y': .5}

        for ip in self.printersDicStatsModal:
            try:
                job = self.api.getJobInfo(ip, self.printersDicStatsModal[ip])
                if job['state'] == 'Printing':
                    estTime = int(job['progress']['printTimeLeft']) / 60 #minutes
                    self.printersPrintTime[ip] = estTime
                    self.printersTime.append(estTime)
            except Exception as err:
                print err.args

        if len(self.printersPrintTime) > 0:
            self.boxLayoutNextPrinter.size_hint_x = .76
            self.boxLayoutNextPrinter.pos_hint = {'center_x': .51, 'center_y': .5}
            minPrintTime = min(self.printersTime)
            for ip in self.printersPrintTime:
                if self.printersPrintTime[ip] == minPrintTime:
                    if minPrintTime == 1:
                        minPrintTimeStr = "Printer: %s, app. a minute left" %(ip)
                    elif minPrintTime < 1:
                        minPrintTimeStr = "Printer: %s, a couple of seconds left" % (ip)
                    else:
                        minPrintTimeStr = "Printer: %s, app. %s minutes left" %(ip, minPrintTime)
                    return minPrintTimeStr

        if self.nrPrintersPrinting != 0:
            self.boxLayoutNextPrinter.size_hint_x = .68
            self.boxLayoutNextPrinter.pos_hint = {'center_x': .49, 'center_y': .5}
            return "Still stabilizing ... Please wait ..."
        return "No printers currently printing ..."



    # ****************************************************************************************
    #       Function that returns the average files size
    # ****************************************************************************************
    def returnAvgFilesSize(self):
        # Clean
        self.avgFilesSizeList = {}
        self.boxLayoutAvgFilesSize.size_hint_x = .55
        self.boxLayoutAvgFilesSize.pos_hint = {'center_x': .395, 'center_y': .5}

        for ip in self.printersDicStatsModal:
            try:
                job = self.api.getJobInfo(ip, self.printersDicStatsModal[ip])
                if job['state'] == 'Printing':
                    avgSize = int(job['job']['file']['size'])# / 3600 #minutes
                    self.avgFilesSizeList[ip] = avgSize
            except Exception as err:
                print err.args

        if len(self.avgFilesSizeList) > 0:
            avgFilesSize = (sum(size for size in self.avgFilesSizeList.values())/len(self.avgFilesSizeList))* math.pow(10,-6)#,1)
            avgFilesSizeLabel = "Approximately %s Mbytes ..." %str(round(avgFilesSize,2))
            return avgFilesSizeLabel

        if self.nrPrintersPrinting != 0:
            return "Still stabilizing ..."
        return "No printers currently printing ..."



    # ****************************************************************************************
    #       Function that returns the number of connected printers on the network
    # ****************************************************************************************
    def getConnectedPrinters(self):
        return "Connected Printers: %s" %len(self.printersDicStatsModal)



    # ****************************************************************************************
    #       Function that checks what printers are connected
    # ****************************************************************************************
    def getPrintersFromFile(self):
        try:
            with open('printers.txt') as fp:
                for line in fp:
                    if len(line.strip()) != 0:
                        ipAndKey = line.split(", ")
                        # if ip not in list and gets response from api -> add to the dict
                        if len(ipAndKey) > 1: # correct format
                            key = ipAndKey[1]
                            if "\n" in key:
                                key = key[0:len(key)-1]
                            self.printersDicStatsModal[ipAndKey[0]] = key
                fp.close()
        except Exception as err:
            print err.args