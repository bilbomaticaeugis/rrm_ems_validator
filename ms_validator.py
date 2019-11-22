import os,sys, shutil
import re
from datetime import datetime
from CheckShapeFile import CheckShapeFile
from ConfigFile import ConfigFile
from CheckGeoPDF import CheckGeoPDF
from CheckImage import CheckImage
from logFile import logFile
from CheckGDB import CheckGDB
from CheckSymbology import CheckSymbology
from checkFactSheet import CheckFactSheet
#from CheckKML import CheckKML
#from CheckGeoJson import CheckGeoJson
#from CheckDBF import CheckDBF
#from CheckConsequence import CheckConsequence
#from CheckSld import CheckSld
#from CheckXml import CheckXml
#from CheckFiles import CheckFiles


def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def checklayer(root):
    for path, dirs, files in os.walk(root):
        try:
            if len(dirs) == 0:
                shp_dict={}
                for file in files:
                    n_file = file.split(".")
                    if n_file[0] in shp_dict:
                        shp_dict[n_file[0]].append(file)
                    else:
                        shp_dict[n_file[0]] = [file]
                #man = self.check_dict(shp_dict)
                return shp_dict
        except Exception as ex:
            print (ex)
            continue

def _checkLayerNomenclature(activ_cod,root,layer ):        
    #check the nomenclature of the layer
                        
    #name in folder structure
    path_in_system= splitall(root[root.index(activ_cod):])
    #name of layer file
    splited_layer = layer.split("_")

    if not (splited_layer[0] == path_in_system[0] and splited_layer[1] == path_in_system[1] and splited_layer[2] == path_in_system[2]             
        and splited_layer[3] == path_in_system[3] and splited_layer[6] == path_in_system[4]):
        return False


def splitall(path):
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
    
def splitroot(root,act):
    ac= splitall(root[root.index(act):])
    return "_".join(ac)


def main(activation_path,logFile):
    startTime = datetime.now()
    conf_file = ConfigFile("config.json")
    attri = conf_file.readJson()
    path = activation_path
    logs_text = attri['logsText']["main"]
    if os.path.isdir(path):
        activation_code = os.path.basename(path)

    try:
        dirct_arr = []
        #save the retunr of each function valid to storage the shapefile array that after is insert in geopdf
        #hacer que guarde todas dentro del diccionario ver como lo actualiza para luego cuando valla ala otra carpeta tire de estas
        values={}
        for dirs in os.listdir(path):
            #walk inside each main folder "VECTOR, RASTER and RTP"
            gdb = attri["FoldersToCheck"][0]
            lyr = attri["FoldersToCheck"][1]
            report = attri["FoldersToCheck"][2]
            has_gdb = False
            if path.find("AEM") != -1:
                pass
            else:
                #check the different folders inside the product_version folder.
                #1.Check the VECTOR folder
                if gdb in dirs:
                    root2 = os.path.join(path, gdb)
                    for root3, dirs_gdb, files in os.walk(root2):
                        #get the different vector layer names
                        if len(dirs_gdb) > 0:
                            for dir in dirs_gdb:
                                if attri["VectorFormats"]["GDB"]["types"][0] in dir:
                                    path = os.path.join(root3, dir)
                                    VectorLayer = globals()[attri["VectorFormats"]["GDB"]["className"]]
                                    vectortype = VectorLayer(root3,attri,activation_code)
                                    vectortype.checkextension(path)
                            has_gdb= True
                        elif len(dirs_gdb) == 0 and len(files) > 0 and has_gdb== False:
                            err = logs_text["no_gdb"].copy()
                            initial_err = activation_code + "|" + splitroot(root3,activation_code) + "|" + gdb + "|" +  logFile.getCatValue( attri['VectorFormats']['GDB']['not_correct_file']) + "|" + logFile.getIssueValue(attri['VectorFormats']['GDB']['not_correct_file']) +"|"
                            err.insert(0,initial_err)
                            logFile.writelogs(err)
                            for file in files:
                                err2 = logs_text["extension"].copy()
                                initial_err = activation_code + "|" + splitroot(root3,activation_code) + "|" + gdb + "|" +  logFile.getCatValue( attri['VectorFormats']['GDB']['not_correct_file']) + "|" + logFile.getIssueValue(attri['VectorFormats']['GDB']['not_correct_file']) +"|"
                                err2.insert(0,initial_err)
                                err2.insert(2,file)
                                logFile.writelogs(err2)
                            #validate each vector layer                   
                elif lyr in dirs:
                    root2 = os.path.join(path, lyr)
                    for root3, dirs_lyr, files in os.walk(root2):
                        VectorLayer = globals()[attri["VectorFormats"]["symbology"]["className"]]
                        vectortype = VectorLayer(root3,attri,activation_code)
                        vectortype.checkextension(files)
                elif report in dirs:
                        root2 = os.path.join(path, report)
                        for root3, dirs_lyr, files in os.walk(root2):
                            VectorLayer = globals()[attri["VectorFormats"]["report"]["className"]]
                            vectortype = VectorLayer(root3,attri,activation_code)
                            vectortype.checkextension(files)


        time = logs_text["time"]
        #shutil.rmtree(attri["Temp_root"])
        time.append(str(datetime.now() - startTime))
        logFile.writelogs(time)
        print("FINISH")

    except Exception as ex:
        e = logs_text["e"]
        e.append(str(ex))
        logFile.writelogs(e)
        time = logs_text["time"]
        time.append(str(datetime.now() - startTime))
        logFile.writelogs(time)

logFile = logFile()

main(sys.argv[1],logFile)