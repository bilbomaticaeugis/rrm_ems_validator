import os
from logFile import logFile
from CommonFunctions import CommonFunctions

class CheckSymbology:
    def __init__(self,root,conf_param,activ_code):
        CommonFunctions.__init__(self,root,conf_param,activ_code)
        self.root = root
        self.logFile = logFile()
        self.conf_param = conf_param
        self.activ_code = activ_code

    def checkesrilayer(self,layer):
        """
        Descrpition: check the if the  folder contain esri symbology layer 
        """
        print (layer)
    def checkogclayer(self,layer):
        """
        Descrpition: check the if the  folder contain OGC symbology layer 
        """
        print (layer)
    def checkextension(self,files):
        try:
            for layer in files:
                if self.conf_param["VectorFormats"]["symbology"]["types"][1] in layer:
                    self.checkogclayer(layer)
                elif self.conf_param["VectorFormats"]["symbology"]["types"][0] in layer:
                    self.checkesrilayer(layer)
                else:
                    err =  self.conf_param['logsText']['symbology']['NoExist'].copy()
                    initial_err = self.activ_code + "|" + CommonFunctions.split_root(self,self.root,self.activ_code) + "|" + layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats']['symbology']) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats']['symbology']) + "|"
                    err.insert(0,initial_err)
                    err.insert(2,layer)
                    self.logFile.writelogs(err)
        except Exception as ex:
            print (ex)
