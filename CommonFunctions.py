import os
from logFile import logFile

class CommonFunctions(object):
    def __init__(self,root,conf_param,activ_code):
        self.root = root
        self.conf_param = conf_param
        self.activ_code = activ_code
        self.logFile = logFile()
    
    def split_root(self,root,activation_code):
        path= root[root.index(activation_code):]
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
        return "_".join(allparts)
    

    def checkLayerNomenclature(self,activ_cod,root,layer):
        #check the nomenclature of the layer
                        
        #name in folder structure
        path_in_system= root[root.index(activ_cod):].split("\\")
        #name of layer file
        splited_layer = layer.split("_")

        if not (splited_layer[0] == path_in_system[0] and splited_layer[1] == path_in_system[1] and splited_layer[2] == path_in_system[2] and
            splited_layer[3] == path_in_system[3] and splited_layer[6] == path_in_system[4]):
            return False

        x = re.search("r\d", splited_layer[5])
        if (x):
            return True

        return False






