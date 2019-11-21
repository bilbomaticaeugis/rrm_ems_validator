import os,sys, shutil
import re
from datetime import datetime
from CheckShapeFile import CheckShapeFile
from ConfigFile import ConfigFile
from CheckGeoPDF import CheckGeoPDF
from CheckImage import CheckImage
from logFile import logFile
from CheckKML import CheckKML
from CheckGeoJson import CheckGeoJson
from CheckDBF import CheckDBF
from CheckConsequence import CheckConsequence
from CheckSld import CheckSld
from CheckXml import CheckXml
from CheckFiles import CheckFiles


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
                return sorted(shp_dict)
        except Exception as ex:
            print (ex)
            continue

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


def _checkLayerNomenclature(activ_cod,root,layer ):        
    #check the nomenclature of the layer
                        
    #name in folder structure
    path_in_system= splitall(root[root.index(activ_cod):])
    #name of layer file
    splited_layer = layer.split("_")

    if not (splited_layer[0] == path_in_system[0] and splited_layer[1] == path_in_system[1] and splited_layer[2] == path_in_system[2]             
        and splited_layer[3] == path_in_system[3] and splited_layer[6] == path_in_system[4]):
        return False

    x = re.search("r\d", splited_layer[5])
    if (x):
        return True

    return False

def splitroot(root,act):
    ac= splitall(root[root.index(act):])
    return "_".join(ac)

def main(activation_path,logFile):
    startTime = datetime.now()
    conf_file = ConfigFile("config.json")
    attri = conf_file.readJson()
    path =activation_path
    logs_text = attri['logsText']["main"]
    if os.path.isdir(path):
        activation_code = os.path.basename(path)

    try:
        dirct_arr = []
        #save the retunr of each function valid to storage the shapefile array that after is insert in geopdf
        #hacer que guarde todas dentro del diccionario ver como lo actualiza para luego cuando valla ala otra carpeta tire de estas
        values={}
        for root, dirs, files in os.walk(path):
            #walk inside each main folder "VECTOR, RASTER and RTP"
            vector=attri["FoldersToCheck"][0]
            rtp=attri["FoldersToCheck"][1]
            raster=attri["FoldersToCheck"][2]
            if root.find("AEM") != -1:
                pass
            else:
                dirs.sort()   
                             
                #check the different folders inside the product_version folder.
                #1.Check the VECTOR folder
                sources =[]
                consecuences = []
                numSource =0
                numConsequence =0

                if (vector in dirs):
                    root2= os.path.join(root,vector)
                    #get the different vector layer names
                    layers_group=checklayer(root2)
                    
                    sources.clear()
                    consecuences.clear()
                    numSource =0
                    numConsequence =0
                    
                    aoi=None
                    #validate each vector layer
                    for layer in layers_group:
                        _nameCorrect = True
                        
                        if not _checkLayerNomenclature(activation_code,root,layer):
                            _nameCorrect = False
                            err =  attri['logsText']['namingconvention']['incorrect'].copy()
                            initial_err = activation_code + "|" + splitroot(root2,activation_code) + "|" + layer + "|" +  logFile.getCatValue(attri['namingconvention']) + "|" +  logFile.getIssueValue(attri['namingconvention']) + "|"
                            err.insert(0,initial_err)
                            logFile.writelogs(err)            

                        if "source" in layer:
                            numSource = numSource+1
                            if not layer in sources:
                                sources.append(layer)
                            

                        elif "summarytable" in layer:                                
                            numConsequence= numConsequence+1
                            if not layer in consecuences:
                                consecuences.append(layer)

                        #validate the layer for each vector format
                        for key,val in attri["VectorFormats"].items():             
                            VectorLayer=globals()[val["className"]]
                            vectortype = VectorLayer(os.path.join(root,vector),layer,attri,activation_code)                            
                            vectortype.setCorrectName(_nameCorrect)
                            if _nameCorrect or ("source" in layer or "summarytable" in layer) :
                                vectortype.checkextension()  
                                aoi = vectortype.checkgeometry(aoi)
                                vectortype.checkattributes()
                                vectortype.close()

                            elif key== "others":
                                vectortype.checkextension()

                    #check if there are missing layers
                    vectortype = CheckFiles(os.path.join(root,vector),"",attri,activation_code)                            
                    vectortype.checkMissingLayers(layers_group)
                        

                    #check if consequence table exists or if it´s present more than once
                    if numConsequence == 0:
                        err =  attri['logsText']['consequence']['extension']['NoExist'].copy()
                        initial_err = activation_code + "|" + splitroot(root2,activation_code) + "|" + 'summarytable' + "|" +  logFile.getCatValue(attri['VectorFormats']['consequence']) + "|" +  logFile.getIssueValue(attri['VectorFormats']['consequence']) + "|"
                        err.insert(0,initial_err)
                        logFile.writelogs(err)    

                    elif numConsequence >1 and len(consecuences)!= numConsequence :
                        err =  attri['logsText']['consequence']['extension']['MoreThanOne'].copy()
                        initial_err = activation_code + "|" + splitroot(root2,activation_code) + "|" + 'summarytable' + "|" +  logFile.getCatValue(attri['VectorFormats']['consequence']) + "|" +  logFile.getIssueValue(attri['VectorFormats']['consequence']) + "|"
                        err.insert(0,initial_err)
                        logFile.writelogs(err)    

                    #check if source.dbf table exists or if it´s present more than once
                    if numSource == 0:
                        err =  attri['logsText']['dbf']['extension']['NoExist'].copy()
                        initial_err = activation_code + "|" + splitroot(root2,activation_code) + "|" + 'source.dbf' + "|" +  logFile.getCatValue(attri['VectorFormats']['consequence']) + "|" +  logFile.getIssueValue(attri['VectorFormats']['consequence']) + "|"
                        err.insert(0,initial_err)
                        logFile.writelogs(err)    

                    elif numSource >1 and len(sources)!= numSource:
                        err =  attri['logsText']['dbf']['extension']['MoreThanOne'].copy()
                        initial_err = activation_code + "|" + splitroot(root2,activation_code) + "|" + 'source.dbf' + "|" +  logFile.getCatValue(attri['VectorFormats']['consequence']) + "|" +  logFile.getIssueValue(attri['VectorFormats']['consequence']) + "|"
                        err.insert(0,initial_err)
                        logFile.writelogs(err) 

                    numConsequence=0;
                    numSource=0;
                    
                    ##2.Check RTP
                    if (rtp in dirs) :
                        v=rtp
                    else:
                        v=raster  
                    for key,val in attri["ImageFormats"].items():
                        raster_Layer=globals()[val["className"]]
                        rastertype = raster_Layer( os.path.join(root,v),attri,activation_code)
                        if val["className"] == "CheckGeoPDF":
                            rastertype.checkextension(layers_group)
                        else:
                            rastertype.checkextension()
              

        time = logs_text["time"]
        #shutil.rmtree(attri["Temp_root"])
        time.append(str(datetime.now() - startTime))
        #logFile.writelogs(time)
        #print("FINISH")

    except Exception as ex:
        e = logs_text["e"]
        e.append(str(ex))
        logFile.writelogs(e)
        time = logs_text["time"]
        time.append(str(datetime.now() - startTime))
        logFile.writelogs(time)

logFile = logFile()

main(sys.argv[1],logFile)

