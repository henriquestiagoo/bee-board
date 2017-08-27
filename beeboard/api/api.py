# -*- coding: utf-8 -*-
import codecs
import sys

import httplib2
import json
import requests

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)


class APIMethods(object):

    # ****************************************************************************************
    #       Init Function
    # ****************************************************************************************
    def __init__(self):
        super(self.__class__, self).__init__()



    # ****************************************************************************************
    #       GET API: example: urlPrefix=http://10.0.0.178/ , command=api/connection
    # ****************************************************************************************
    def getConnection(self, ip, key):
        # If on localhost, need to add the port for the api communication to work properly
        ip = self.checkIfLocalhost(ip)
        try:
            url = ('http://%s/api/connection?apikey=%s' % (ip, key))
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            connection = result['current']
            return connection
        except Exception as err:
            print err.args


    # ****************************************************************************************
    #       GET API: example: urlPrefix=http://10.0.0.178/ , command=api/maintenance/get_filament
    # ****************************************************************************************
    def getFilament(self, ip, key):
        # If on localhost, need to add the port for the api communication to work properly
        ip = self.checkIfLocalhost(ip)
        try:
            url = ('http://%s/api/maintenance/get_filament?apikey=%s' % (ip, key))
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            return result
        except Exception as err:
            print err.args


    # ****************************************************************************************
    #       GET API: example: urlPrefix=http://10.0.0.178/ , command=api/maintenance/get_nozzles_and_filament
    # ****************************************************************************************
    def getNozzlesAndFilament(self, ip, key):
        # If on localhost, need to add the port for the api communication to work properly
        ip = self.checkIfLocalhost(ip)
        try:
            url = ('http://%s/api/maintenance/get_nozzles_and_filament?apikey=%s' % (ip, key))
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            return result
        except Exception as err:
            print err.args



    # ****************************************************************************************
    #       GET API: example: urlPrefix=http://10.0.0.178/ , command=api/printer/serial
    # ****************************************************************************************
    def getSerialNum(self, ip, key):
        # If on localhost, need to add the port for the api communication to work properly
        ip = self.checkIfLocalhost(ip)
        try:
            url = ('http://%s/bee/api/printer/serial?apikey=%s' % (ip, key))
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            return result
        except Exception as err:
            print err.args


    # ****************************************************************************************
    #       GET API: example: urlPrefix=http://10.0.0.178/ , command=api/job
    # ****************************************************************************************
    def getJobInfo(self, ip, key):
        # If on localhost, need to add the port for the api communication to work properly
        ip = self.checkIfLocalhost(ip)
        try:
            url = ('http://%s/api/job?apikey=%s' % (ip, key))
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            return result
        except Exception as err:
            print err.args



    # ****************************************************************************************
    #       Function that checks if the ip address is localhost; It needs to add the port in that case
    # ****************************************************************************************
    def checkIfLocalhost(self, ip):
        if ip == "127.0.0.1":
            ip = ip + ":5007"
        return ip



    # ****************************************************************************************
    #       GET API: example: urlPrefix=http://10.0.0.178/ , command=api/maintenance/temperature
    # ****************************************************************************************
    def getTemperatureOnHeating(self, ip, key):
        # If on localhost, need to add the port for the api communication to work properly
        ip = self.checkIfLocalhost(ip)
        try:
            url = ('http://%s/api/maintenance/temperature?apikey=%s' % (ip, key))
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            return result
        except Exception as err:
            print err.args


    # ****************************************************************************************
    #       GET API: example: urlPrefix=http://10.0.0.178/ , command=bee/api/printer
    # ****************************************************************************************
    def getName(self, ip, key):
        # If on localhost, need to add the port for the api communication to work properly
        ip = self.checkIfLocalhost(ip)
        try:
            url = ('http://%s/bee/api/printer?apikey=%s' % (ip, key))
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            return result
        except Exception as err:
            print err.args


    # ****************************************************************************************
    #       Function that checks if the ip and api key are valid; Returns 200 if valid; Returns code 400 otherwise
    # ****************************************************************************************
    def checkValidIpAndKey(self, ip, key):
        try:
            ip = self.checkIfLocalhost(ip)
            url = ('http://%s/api/connection?apikey=%s' % (ip, key))
            r = requests.head(url)
            return r.status_code
        except requests.ConnectionError:
            return 400