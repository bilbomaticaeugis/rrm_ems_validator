import os
from logFile import logFile
class CheckImage:
    def __init__(self,root,conf_param,activ_cod):
        self.root = root
        self.logFile = logFile()
        self.conf_param = conf_param
        self.activ_cod = activ_cod

    def splitall(self,path):
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts


    def splitroot(self,root,act):
        ac= self.splitall(root[root.index(act):])
        return "_".join(ac)

    def checkextension(self):
        """
        Descrpition: check the if the  imagen has the propertly format
            path: string that contain the path where the tiff is located
        """
        img = False
        for path1, dirs, files in os.walk(self.root):
            for file in files:
                if file.lower().endswith(self.conf_param["ImageFormats"]['image']["types"][0]):
                    img = True
                elif file.lower().endswith(self.conf_param["ImageFormats"]['image']["types"][1]):
                    img = True
                elif file.lower().endswith(self.conf_param["ImageFormats"]['image']["types"][2]):
                    img = True
                elif file.lower().endswith(self.conf_param["ImageFormats"]['pdf']["types"][0]):
                    img = True
            if img == False:
                no_image = self.conf_param["logsText"]['img']['notimg']
                if len(files) > 0:
                    initial_err =self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + file + "|" +  self.logFile.getCatValue(self.conf_param['ImageFormats']['image']) + "|" +  self.logFile.getIssueValue(self.conf_param['ImageFormats']['image']) + "|"
                else:
                    initial_err =self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + "|" +  self.logFile.getCatValue(self.conf_param['ImageFormats']['image']) + "|" +  self.logFile.getIssueValue(self.conf_param['ImageFormats']['image']) + "|"                        
                no_image.insert(0,initial_err)
                self.logFile.writelogs(no_image)
                no_image.pop(0)  