import ogr,os,subprocess, ogr2ogr
from logFile import logFile
import numpy as np
from CheckVectorFile  import CheckVectorFile 




class CheckShapeFile(CheckVectorFile):

    def __init__(self,root,layer,conf_param,activ_cod):
        CheckVectorFile.__init__(self,root,conf_param,activ_cod)
        self.driver = ogr.GetDriverByName("ESRI Shapefile")
        self.shape_array=[]
        self.layer= layer
        self.extension ="shp"
        self.type= "shapefile"
        self.file =os.path.join(self.root, self.layer) + '.shp' 
        self.logs_text = self.conf_param['logsText']["shapefile"]        
        
    def checkextension(self):        
        logs_text = self.logs_text
        try:
            if not "summarytable" in self.file and not "source" in self.file:
                extensions = self.conf_param["VectorFormats"][self.type]["types"]                
                if len(extensions) > 0:   
                    #check if all necessary files of shapefiles are present
                    numFiles=0
                    for ext in extensions:
                        file =os.path.join(self.root, self.layer) + "." + ext
                        if not os.path.isfile(file):
                            no_extension = self.conf_param["logsText"][self.type]['extension']['NoExist'].copy()
                            initial_err = self.activ_cod + "|" + self.split_root(self.root,self.activ_cod) + "|" + self.layer + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
                            no_extension.insert(0,initial_err)
                            no_extension.insert(2, ext)


                            self.logFile.writelogs(no_extension)
                        else:
                            numFiles = numFiles+1
                            self._checkextension()

                    #if numFiles >= len(extensions):
                    self.open()
                        
            
            return self.shape_array
        except Exception as ex:
            e = logs_text["e"]
            e.append(str(ex))
            self.logFile.writelogs(e)


    def check_dict(self, dict):
        """
        Description: check a dictionary that contain the different shapefile extensions
        ----------
           
        dict: dictionary
            contain the extension of each file as key and the file name as value

        """

        extension = self.conf_param["VectorFormats"]["shapefile"]["types"]
        for key in dict.keys():
            if "summarytable" in key or "source" in key:
                pass
            else:
                file_ext = []
                for val in dict[key]:
                    file_ext.append(val.split(".")[-1])
                #this line returns the shapefile is not inside the json array
                check_shp_json = np.setdiff1d(extension,file_ext)
                if len(check_shp_json) > 0:
                    for ex in check_shp_json:
                        no_extension = self.conf_param["logsText"]['shapefile']['extension'].copy()
                        initial_err = self.activ_cod + "|" + self.splitroot(self.root,self.activ_cod) + "|" + key + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
                        no_extension.insert(0,initial_err)
                        no_extension.insert(2,key)   
                        no_extension.insert(4,key + "." + ex)
                        self.logFile.writelogs(no_extension)
   
    """
    def calcualtearea(self,driver,path):
        driver_path = os.path.join(path , self.file)
        ds = driver.Open(driver_path, 0)
        feature = ds.GetLayer().GetNextFeature()
        total_area = 0.0  # we unknow the unity meters ha etc
        total_length = 0.0
        gt = ds.GetLayer().GetGeomType()

        while feature:
            if gt == 3:#polygon
                total_area += feature.GetGeometryRef().GetArea()
                feature=ds.GetLayer().GetNextFeature()  
            elif gt == 2:#line
                total_area += feature.GetGeometryRef().GetArea()
        print(total_area)

        
        
        ogr2ogr.main(["","sql", "KML", "out.kml", "data/san_andres_y_providencia_administrative.shp"])
        my_call = ['C:/OSGeo4W64/OSGeo4W.bat',
                'ogrinfo', '-sql', 'SELECT SUM(OGR_GEOM_AREA) AS TOTAL_AREA FROM'+ path,
                    path]
        subp = subprocess.getoutput(my_call)
    """   
    def _checkextension(self):
        pass