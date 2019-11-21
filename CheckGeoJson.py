import ogr,os,json
from logFile import logFile

class CheckGeoJson:
    def __init__(self,root,conf_param):
        """
        Description: Init function
        ----------
        conf_param : Dictionary
            the config file
           
        root: string
            the folder path
        """
        self.file = ""
        self.root = root
        self.logFile = logFile()
        self.conf_param = conf_param

    def checkattributes(self,value,attribute,logs_text):
        """
        Description: Check if the geojson attributes have the correct datatype
        Parameters
        ----------
        value : Dictionary
            the geojson properties and geometry
        
        attribute:Dictionary
            the attributes of each geojson field
        
        logs_text: Dictionary
            the parameters necessaries to generate the log file

        """
        for key, val in value['properties'].items():
            if attribute[key]['DataType'] == 'str' and isinstance(val,str):
                pass
            elif attribute[key]['DataType'] == 'int' and isinstance(val,int):
                pass
            else:
                pass
                #self.logFile.writelogs(root + " " + key + " hasn't the correct DataType\n")
                geojson = logs_text["attributes"]["datatype"]
                geojson.insert(0,key)
                geojson.insert(2,key)
                self.logFile.writelogs(geojson,self.conf_param["root_path"])
                geojson.pop(2)
                geojson.pop(0)
 

    def checkstructure(self,geoson_data):
        """
        Description: Check if the geojson structure is the correct and it contain all the properties required and fields
        Parameters
        ----------
        
        geoson_data:Dictionary
            the geojson schema to check

        """
        logs_text=self.conf_param['logsText']["geojson"]
        string_chain = self.file.split("_")
        name_comp=string_chain[4].lower()
        if geoson_data:
            if geoson_data['features']:
                for value in geoson_data['features']:
                    geometry = value['geometry']
                    if geometry:
                        if geometry['coordinates']:
                            pass
                        if geometry['type']:
                            pass
                        if value['properties']:
                            #check the geojson attributes with config file atributted defined
                            attribute=self.conf_param["files_to_check"][name_comp]["Attributes"]
                            compare = value['properties'].keys() - attribute.keys()
                            if len(compare) == 0:
                               self.checkattributes(value,attribute,logs_text)
                            else:
                                geojson = logs_text["structure"]["fieldNotCorrect"]
                                geojson.insert(0,self.file)
                                self.logFile.writelogs(geojson,self.root)
                                geojson.pop(0)
                                break
                        if value['type']:
                            pass
                        if geoson_data['type']:
                            pass
                        else:
                            geojson = logs_text["structure"]["notGeojson"]
                            geojson.insert(0,self.file)
                            self.logFile.writelogs(geojson,self.conf_param["root_path"])
                            geojson.pop(0)

    def checkextension(self):
        """
        Descrpition: check if the file contains json extension to continue with the process
        
        """
        json_array = []
        logs_text = self.conf_param['logsText']["geojson"]
        for path1, dirs, files in os.walk(self.root):
            if len(dirs) == 0:
                for file in files: 
                    self.file = file
                    if file.lower().endswith('.json'):
                         #if the file is a json execute the code below
                        npath =os.path.join(self.root, file)
                        print (file + " has geojson")
                        with open(npath, mode='r', encoding="utf-8") as f:
                            try:
                                schema_data = f.read()
                                geoson_data = json.loads(schema_data)
                                self.checkstructure(geoson_data)
                            except KeyError as error:
                                geojson = logs_text["extension"]["keyError"]
                                geojson.insert(1,file)
                                geojson.insert(3,str(error.args[0]))
                                self.logFile.writelogs(geojson,self.conf_param["root_path"])
                                geojson.pop(3)
                                geojson.pop(1)
                                continue
                            except Exception as error:
                                geojson = logs_text["extension"]["Exception"]
                                geojson.insert(0,file)
                                geojson.insert(2,str(error))
                                self.logFile.writelogs(geojson,self.conf_param["root_path"])
                                geojson.pop(2)
                                geojson.pop(0)
                        json_array.append(file)