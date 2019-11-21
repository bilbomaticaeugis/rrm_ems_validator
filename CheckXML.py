import ogr,os,json
import numpy as np
from logFile import logFile
from CheckVectorFile  import CheckVectorFile 

class CheckXml(CheckVectorFile):
    def __init__(self,root,layer,conf_param,activ_cod):
        CheckVectorFile.__init__(self,root,conf_param,activ_cod)        
        self.shape_array=[]
        self.layer= layer
        self.type ='xml'
        self.extension = 'xml'
        self.file =os.path.join(self.root, self.layer) + '.' + self.extension
        self.logs_text = self.conf_param['logsText']["xml"]

    def checkgeometry(self,aoi):
        return aoi        



    def checkextension(self):
        pass

    def checkattributes(self):
        pass