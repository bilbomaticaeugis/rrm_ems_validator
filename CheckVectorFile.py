import ogr,os,json
import numpy as np
import re
from logFile import logFile

class CheckVectorFile():
    def __init__(self,root,conf_param,activ_cod):
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
        self.driver = ''
        self.ds= None
        self.logFile = logFile()
        self.conf_param = conf_param
        self.activ_cod = activ_cod
        self.nameConvention = True

    def setCorrectName(self,valid):
        self.nameConvention= valid
    
    def open(self):
        try:
            ogr.UseExceptions()
            if self.ds== None:
                self.ds = self.driver.Open(self.file, 0)

        except Exception as ex:
            no_extension = self.conf_param["logsText"]['cannot_open_file'].copy()
            initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|" + ex.args[0] + ' '
            no_extension.insert(0,initial_err)
            self.logFile.writelogs(no_extension,self.conf_param["root_path"])

        finally:    
            return self.ds != None
    
    def close(self):
        if self.ds != None:
            self.ds.Destroy()

    def _getLayerGeometry(self):
        string_chain = self.layer.split("_")
        if len(string_chain) == 7:
            return string_chain[4][-1] 
        else:
            return false

    def _checkLayerNomenclature(self):        
        #check the nomenclature of the layer
                        
        #name in folder structure
        path_in_system= self.root[self.root.index(self.activ_cod):].split("\\")
        #name of layer file
        splited_layer = self.layer.split("_")

        if not (splited_layer[0] == path_in_system[0] and splited_layer[1] == path_in_system[1] and splited_layer[2] == path_in_system[2] and
            splited_layer[3] == path_in_system[3] and splited_layer[6] == path_in_system[4]):
            return False

        x = re.search("r\d", splited_layer[5])
        if (x):
            return True

        return False

    def checkextension(self):        
        logs_text = self.logs_text
        try:
            if not "summarytable" in self.file and not "source" in self.file:
                extensions = self.conf_param["VectorFormats"][self.type]["types"]
                if len(extensions) > 0:
                    for ext in extensions:
                        file =os.path.join(self.root, self.layer) + "." + ext
                        if not os.path.isfile(file):
                            no_extension = self.conf_param["logsText"][self.type]['extension']['NoExist'].copy()
                            initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
                            no_extension.insert(0,initial_err)
                            self.logFile.writelogs(no_extension,self.conf_param["root_path"])
                        else:
                            self.open()
                            self._checkextension()
            
            return self.shape_array
        except Exception as ex:
            e = logs_text["e"]
            e.append(str(ex))
            self.logFile.writelogs(e,path)


    def checkgeometry(self,aoi):
        if self.ds==None:
            return aoi
        layerGeometry = self._getLayerGeometry()
        gt = self.ds.GetLayer().GetGeomType()
        if layerGeometry:
            if not (
              (layerGeometry== "P" and gt ==1)
              or
              (layerGeometry== "L" and gt ==2)
              or
              (layerGeometry== "A" and gt ==3)):
                #check fature by feature 
                self.__checkGeometryByFeature(layerGeometry)

            #check if the layer is within the AOI 
            numDigitsForAoi = 6
            extent = self.ds.GetLayer().GetExtent()
            # Create a Polygon from the extent of the layer
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(round(extent[0],numDigitsForAoi),round(extent[2],numDigitsForAoi))
            ring.AddPoint(round(extent[1],numDigitsForAoi), round(extent[2],numDigitsForAoi))
            ring.AddPoint(round(extent[1],numDigitsForAoi), round(extent[3],numDigitsForAoi))
            ring.AddPoint(round(extent[0],numDigitsForAoi), round(extent[3],numDigitsForAoi))
            ring.AddPoint(round(extent[0],numDigitsForAoi),round(extent[2],numDigitsForAoi))
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            if 'areaofinterest' in self.layer.lower():
               #get the geometry of the area of interest if none has been defined
               if aoi == None:
                   return poly
               else:
                   #compare if all AOIs are the same
                   if not poly.Equal(aoi):
                       
                       err = self.logs_text["geometryName"]["not_equal_AOI"].copy()
                       initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]['not_equal_AOI']) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]['not_equal_AOI']) + "|"
                       err.insert(0,initial_err)
                       self.logFile.writelogs(err,self.conf_param["root_path"])


            else:
				#check if the current layer´s extent in within AOI of the product
                if aoi!=None:
                    if not poly.Within(aoi):
                        err = self.logs_text["geometryName"]["not_in_AOI"].copy()
                        initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]['not_in_AOI']) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]['not_in_AOI']) + "|"
                        err.insert(0,initial_err)
                        self.logFile.writelogs(err,self.conf_param["root_path"])

        else:
            err = self.logs_text["geometryName"]["wrong_name"].copy()
            err.insert(0,self.root + "\\" + self.file)
            self.logFile.writelogs(err,self.conf_param["root_path"])
        return aoi

    def __checkGeometryByFeature(self,layerGeometry):
        layer = self.ds.GetLayer(0)
        numfeatures= layer.GetFeatureCount()
        n= self._firstFeature()        
        while not self._isLastFeature(n,numfeatures):
            feature= layer.GetFeature(n)
            if not self.checkFeatureGeometry(feature,layerGeometry):
                return False
            n=n+1
        return True

    def checkFeatureGeometry(self,feature,layerGeometry):
        if (feature!=None):
            try:
                gt=feature.GetGeometryRef().GetGeometryName()
                if not (
                    (layerGeometry== "P" and 'POINT' in gt  )
                    or
                    (layerGeometry== "L" and ('LINE' in gt or 'STRING' in gt))
                    or
                    (layerGeometry== "A" and 'POLYGON' in gt )):
                    #return False        
                    wrong_geom = self.logs_text["geometryName"]["wrong_geom"].copy()
                    initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
                    wrong_geom.insert(0,initial_err)
                    wrong_geom.insert(2,self.layer)
                    self.logFile.writelogs(wrong_geom,self.conf_param["root_path"])
                    return False
            except Exception as ex:
                aa=1
            finally:
                feature.Destroy()
        return True
    def split_name_layer(self):
        string_chain = self.layer.split("_")
        return string_chain[4].lower()

    def checkattributes(self):
        """
        Description: Check if the vector contains the same field that are demanded
        ----------
           
        String_chain: array 
            contains the file name split

        ds: Object
            ogr object that contains the shapefile information
        """
        if self.ds==None:
            return 0

        files_check = self.conf_param['files_to_check'] 

        layer = self.ds.GetLayer().GetLayerDefn()
        name_comp = self.split_name_layer()
        config_fields = []
        layer_fields = []

        #get the attributes defined in config
        try:
            if name_comp in files_check:
                for key in files_check[name_comp]["Attributes"]:
                    if key not in ["cat","issue"]:
                        config_fields.append(key)
                #get fields in the current layer
                for n in range(layer.GetFieldCount()):
                    field = layer.GetFieldDefn(n)
                    layer_fields.append(field.name)

                missing_fields = np.setdiff1d(config_fields,layer_fields)
                extra_fields = np.setdiff1d(layer_fields,config_fields)

                if len(missing_fields) > 0:
                    self._writeFieldError("missingAttribute",missing_fields,files_check[name_comp]["Attributes"])

                if len(extra_fields) > 0:
                    self._writeFieldError("extraAttribute",extra_fields,files_check[name_comp]["Attributes"])

                #check the datatypes in attributes match with the ones in config
                #get fields in the current layer
                for n in range(layer.GetFieldCount()):
                    field = layer.GetFieldDefn(n)
                    field_Type_Emer = field.GetFieldTypeName(field.GetType()) #the actual  datatype in the layer                    
                    if field.name in files_check[name_comp]["Attributes"]:
                        #the attribute is defined in config
                        field_Type_Conf =files_check[name_comp]["Attributes"][field.name]["DataType"]  #the datatype definedin config
                        if  not (field_Type_Emer in field_Type_Conf or field_Type_Conf in field_Type_Emer) :
                            #the type in the layer is not the defined one
                            datatype = self.logs_text["attribute"]["DataType"].copy()
                            initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue( files_check[name_comp]["Attributes"]) + "|" + self.logFile.getIssueValue( files_check[name_comp]["Attributes"]) +"|"
                            datatype.insert(0,initial_err)
                            datatype.insert(2,field.name.lower())
                            datatype.insert(4,field_Type_Emer)
                            datatype.insert(6,field_Type_Conf)
                            self.logFile.writelogs(datatype,self.conf_param["root_path"])
                self.shape_array.append(self.layer)

        except KeyError as key:
            fieldName = self.logs_text["attribute"]["fieldName"].copy()
            initial_err = self.root + "|" + self.file + "|" +  self.logFile.getCatValue( files_check[name_comp]["Attributes"]) + "|" + self.logFile.getIssueValue( files_check[name_comp]["Attributes"]) +"|"
            fieldName.insert(0,initial_err)
            fieldName.insert(2,field.name)
            fieldName.insert(4,name_comp)
            self.logFile.writelogs(fieldName,self.conf_param["root_path"])

        except Exception as ex:
            e = self.logs_text["e"]
            e.append(str(ex))
            self.logFile.writelogs(e,self.conf_param["root_path"])
            

    def splitroot(self,root,act):
        ac=root.split(act)
        product = ""
        for na in ac[1].split("\\"):
            product += na + "_"
        return product

    def _getProductName(self):
        ac=self.root.split(self.activ_cod)
        product = ""
        for na in ac[1].split("\\"):
            product += na + "_"
        return product

    def _getKey(self):
        ac=self.file.split("\\")



    def _writeFieldError(self,match, check_array, error_config_attr):
        err = self.logs_text[match]
        for conf in check_array:
            checkField= True
            if 'ignorefields' in self.conf_param['VectorFormats'][self.type]:
                if conf in self.conf_param['VectorFormats'][self.type]['ignorefields']:
                    checkField = False

            if checkField:    
                initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue(error_config_attr) + "|" +  self.logFile.getIssueValue(error_config_attr) + "|"
                error = []
                error.insert(0,initial_err)
                error.insert(1 ,err[0])
                error.insert(2 ,  "'" + conf + "' ")
                error.insert(3 , err[1])
                self.logFile.writelogs(error,self.conf_param["root_path"])					



    def __CleanLayerName(self):
        string_chain = self.file.split("_")
        return  string_chain[5]

