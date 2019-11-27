import os
import ogr 
from zipfile import ZipFile
from logFile import logFile
import numpy as np
from CommonFunctions import CommonFunctions
import shapely.wkt

class CheckGDB(CommonFunctions):
    def __init__(self,root,conf_param,activ_code):
        CommonFunctions.__init__(self,root,conf_param,activ_code)
        self.root = root
        self.logFile = logFile()
        self.conf_param = conf_param
        self.activ_code = activ_code
        self.ds =""

    def _getLayerGeometry(self):
        string_chain = self.layer.split("_")
        if len(string_chain) == 7:
            return string_chain[4][-1] 
        else:
            return false

    def extent_calculation(self,extent_layer):
        numDigitsForAoi = 6
        extent = extent_layer
        # Create a Polygon from the extent of the layer
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(round(extent[0],numDigitsForAoi),round(extent[2],numDigitsForAoi))
        ring.AddPoint(round(extent[1],numDigitsForAoi), round(extent[2],numDigitsForAoi))
        ring.AddPoint(round(extent[1],numDigitsForAoi), round(extent[3],numDigitsForAoi))
        ring.AddPoint(round(extent[0],numDigitsForAoi), round(extent[3],numDigitsForAoi))
        ring.AddPoint(round(extent[0],numDigitsForAoi),round(extent[2],numDigitsForAoi))
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        return poly
    
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

    def checkgeometry(self,layers):
        try:
            if self.ds==None:
                return layers
            """
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
            """


            #check if the layer is within the AOI 

            # Create a Polygon from the extent of the layer
            aoi_geometry = None
            for layer_object in layers['AOI']['LayerObject']:
                layer_object
                aoi_geometry = shapely.wkt.loads(layer_object.geometry().ExportToIsoWkt())
            ogr.UseExceptions()
            #aoi_extent = self.extent_calculation(aoi['AOI']['GeometryObject'].GetLayer().GetExtent())
            for key in layers:
                #layer_extent = self.extent_calculation(aoi[key]['GeometryObject']
                for layer_object in layers[key]['LayerObject']:
                    pass
                    if not layer_object.geometry().Within(aoi_geometry):
                        err = self.logs_text["geometryName"]["not_in_AOI"].copy()
                        initial_err = self.activ_code + "|" + self.splitroot(self.root,self.activ_code) + "|" + self.layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]['not_in_AOI']) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]['not_in_AOI']) + "|"
                        err.insert(0,initial_err)
                        self.logFile.writelogs(err) 
        except Exception as ex:
            print (ex)

        """
        else:
            err = self.logs_text["geometryName"]["wrong_name"].copy()
            err.insert(0,self.root + "\\" + self.file)
            self.logFile.writelogs(err)
        return aoi
        """
    def _split_name_layer(self,layer):
        string_chain = layer.split("_")
        if len(string_chain) > 5:
            return string_chain[4].lower()
        else: 
            return layer

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
                self.logFile.writelogs(error)

    def _checkattributes(self,layer,field_name_array):
        """
        Description: Check if the vector contains the same field that are demanded
        ----------
           
        String_chain: array 
            contains the file name split

        ds: Object
            ogr object that contains the shapefile information
        """

        files_check = self.conf_param['files_to_check'] 

        name_comp = self._split_name_layer(layer.GetName())
        config_fields = []
        #get the attributes defined in config
        try:
            if name_comp in files_check:
                for key in files_check[name_comp]["Attributes"]:
                    if key not in ["cat","issue"]:
                        config_fields.append(key)
                #get fields in the current layer
 
                missing_fields = np.setdiff1d(config_fields,field_name_array)
                extra_fields = np.setdiff1d(field_name_array,config_fields)

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
                            self.logFile.writelogs(datatype)


        except KeyError as key:
            fieldName = self.logs_text["attribute"]["fieldName"].copy()
            initial_err = self.root + "|" + self.file + "|" +  self.logFile.getCatValue( files_check[name_comp]["Attributes"]) + "|" + self.logFile.getIssueValue( files_check[name_comp]["Attributes"]) +"|"
            fieldName.insert(0,initial_err)
            fieldName.insert(2,field.name)
            fieldName.insert(4,name_comp)
            self.logFile.writelogs(fieldName)

        except Exception as ex:
            e = self.logs_text["e"]
            e.append(str(ex))
            self.logFile.writelogs(e)
            
    
    def checkextension(self,path):
        """
        Descrpition: check the gdb 
        """
        try:
            logs_text = self.conf_param['logsText']["GDB"]
            open_file_GDB = ogr.GetDriverByName("OpenFileGDB")
            self.ds = open_file_GDB.Open(path, 0)
            if self.ds != None:
                n = 0
                layer_dictionary = {}
                field_name_array = []
                while n < self.ds.GetLayerCount():
                    name = self.ds.GetLayer(n).GetName()
                    if not CommonFunctions.checkLayerNomenclature(self,self.activ_code,self.root,name):
                        _nameCorrect = False
                        err =  self.conf_param['logsText']['namingconvention']['incorrect'].copy()
                        initial_err = self.activ_code + "|" + CommonFunctions.split_root(self,self.root,self.activ_code) + "|" + name + "|" +  self.logFile.getCatValue(self.conf_param['logsText']['namingconvention']) + "|" +  self.logFile.getIssueValue(self.conf_param['logsText']['namingconvention']) + "|"
                        err.insert(0,initial_err)
                        self.logFile.writelogs(err) 
                    aoi = None           
                    layer_dictionary[name]={
                        'GeometryType':self.ds.GetLayer(n).GetGeomType(),
                        'LayerObject':self.ds.GetLayer(n),
                    }
                    layer = self.ds.GetLayer(n).GetLayerDefn()
                    for d in range(layer.GetFieldCount()):
                        field_name_array.append(layer.GetFieldDefn(d).GetName())
                    self._checkattributes(layer,field_name_array)
                    layer_dictionary[name]["Field"] = field_name_array
                    n += 1
                #print (layer_dictionary)
                #print ("a")
                #self.checkgeometry(layer_dictionary)
            else:
                inital_text_error = self.activ_code + "|" + CommonFunctions.split_root(self,self.root,self.activ_code) + "|" + name + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
                geojson = logs_text["extension"]["NoExist"]
                geojson.insert(0,inital_text_error)
                self.logFile.writelogs(geojson)
                geojson.pop(0)
        except Exception as ex:
            e=self.conf_param['logsText']["KML"]["extension"]["keyError"]
            inital_text_error = self.activ_code + "|" + CommonFunctions.split_root(self,self.root,self.activ_code) + "|" + name + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
            e.insert(0,inital_text_error)
            e.insert(1,str(ex))
            self.logFile.writelogs(e)
            e.pop(1)
            e.pop(1)



