import os
from CommonFunctions import CommonFunctions
import numpy as np
from logFile import logFile
from PIL import Image


class CheckFactSheet:
    def __init__(self,root,conf_param,activ_code):
        CommonFunctions.__init__(self,root,conf_param,activ_code)
        self.root = root
        self.logFile = logFile()
        self.conf_param = conf_param
        self.activ_code = activ_code
        self.logs_text = conf_param["logsText"]["report"]
        self.ds =""

    def CheckFactSheet(self):
        """
        Descrpition: check report file 
        """
        pass

    def CheckFlayer(self):
        pass

    def _check_file_size(self,files,extension_config,error_config_attr):
        for file in files:
            file_extension = file.split('.')[1].lower()
            path = os.path.join(self.root, file)
            statinfo = os.stat(path)
            for extension in file_extension:
                if extension in extension_config:
                    if statinfo.st_size > extension_config[file_extension]["MaxFileSize"]:
                        err = self.logs_text["overSize"].copy()
                        #need change conf for the name file  
                        initial_err = self.activ_code + "|" + CommonFunctions.split_root(self,self.root,self.activ_code) + "|" + file + "|" +  self.logFile.getCatValue(error_config_attr) + "|" +  self.logFile.getIssueValue(error_config_attr) + "|"
                        err.insert(0,initial_err)
                        err.insert(2 ,file)
                        self.logFile.writelogs(err)
    """
    def _check_image_corrupted(self):
        try:
            img = Image.open('./'+filename) # open the image file
            img.verify() # verify that it is, in fact an image
        except (IOError, SyntaxError) as e:
            print('Bad file:', filename) # print out the names of corrupt files
    """
    def _writeFieldError(self,match, check_array, error_config_attr,files):
        for conf in check_array:
            checkField= True
            #if 'ignorefields' in self.conf_param['VectorFormats'][self.type]:
                #if conf in self.conf_param['VectorFormats'][self.type]['ignorefields']:
                    #checkField = False

            if checkField:  
                #need change conf for the name file 
                err = self.logs_text[match].copy() 
                initial_err = self.activ_code + "|" + CommonFunctions.split_root(self,self.root,self.activ_code) + "|" +" "+ "|" +  self.logFile.getCatValue(error_config_attr) + "|" +  self.logFile.getIssueValue(error_config_attr) + "|"
                err.insert(0,initial_err)
                err.insert(2 ,conf)
                self.logFile.writelogs(err)
    

    def _check_corrupted_files(self,files,error_config_attr):
        try:
            image_extension_conf = self.conf_param["VectorFormats"]["report"]["image"]
            file_extension_conf = self.conf_param["VectorFormats"]["report"]["files"]
            for file in files:
                if file.split(".")[1] in image_extension_conf:
                    image = os.path.join(self.root,file)
                    img = Image.open(image) # open the image file
                    img.verify() # verify that it is, in fact an image
            for file in files:
                if file.split(".")[1] in file_extension_conf:
                    file_check = os.path.join(self.root,file)
                    fil = open(file_check) # open the image file
                    fil.close()
        except (IOError, SyntaxError) as e:
            err = self.logs_text["corrupted"].copy()
            #need change conf for the name file  
            initial_err = self.activ_code + "|" + CommonFunctions.split_root(self,self.root,self.activ_code) + "|" + file + "|" +  self.logFile.getCatValue(error_config_attr) + "|" +  self.logFile.getIssueValue(error_config_attr) + "|"
            err.insert(0,initial_err)
            err.insert(2 ,file)
            self.logFile.writelogs(err)
    
    
    def checkextension(self,files):
        try:
            extension_config = self.conf_param["VectorFormats"]["report"]["FactSheetFormats"]
            file_extension = list(map(lambda x:x.split('.')[1].lower(),  files))
            config_extension = list(map(lambda x:x,  extension_config))
            self._check_file_size(files,extension_config,self.conf_param["VectorFormats"]["report"])
            missing_extension = np.setdiff1d(config_extension,file_extension)
            extra_extension = np.setdiff1d(file_extension,config_extension)
            self._check_corrupted_files(files,self.conf_param["VectorFormats"]["report"])
            if len(missing_extension) > 0:
                self._writeFieldError("hasNotExtension",missing_extension,self.conf_param["VectorFormats"]["report"],files)
            if len(extra_extension) > 0:
                self._writeFieldError("hasExtra",extra_extension,self.conf_param["VectorFormats"]["report"],files)
        except Exception as ex:
            print (ex)
