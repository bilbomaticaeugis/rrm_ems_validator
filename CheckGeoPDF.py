import os,subprocess
import numpy as np
from logFile import logFile
from osgeo import gdal

class CheckGeoPDF:
    def __init__(self,root,conf_param,activ_cod):
        """
        Description: Init function
        ----------
        conf_param : Dictionary
            the config file
           
        root: string
            the folder path

        """
        self.root = root
        self.logFile = logFile()
        self.conf_param = conf_param
        self.activ_cod = activ_cod
        self.type ='pdf'
        self.extension = 'pdf'

    def checkextension(self,shp_list):
        """
        Description: check if the shapefile contained in the Vector folder are also in theGeopdf. 
        ----------
           
        Shp_list: Array
            contain the shapefile names to compare with geopdf

        """
        layers_name = map(lambda x: x, shp_list)
        layers_name = list(layers_name)
        logs_text=self.conf_param['logsText']["geopdf"]
        try:
            pdf= False
            for path1, dirs, files in os.walk(self.root):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        path = os.path.join(path1, file)
                        hDataset = gdal.Open(path, gdal.GA_ReadOnly)
                        if hDataset:
                            layers= hDataset.GetMetadata_List("LAYERS")
                            lyr_names_geopdf= map(lambda x: x.split('=')[1], layers)
                            lyr_names_geopdf = list(lyr_names_geopdf)
                            hDataset= None
                            pdf = True
                        else: 
                            print ("PDF None")
            if pdf:            
                a=1
                pdf_not_contain_layer_list = np.setdiff1d(lyr_names_geopdf,layers_name)
                layer_list_not_contain_pdf = np.setdiff1d(layers_name,lyr_names_geopdf)               
                if len(layer_list_not_contain_pdf) > 0:
                    for geo in layer_list_not_contain_pdf:
                        ac=self.root.split(self.activ_cod)
                        product = ""
                        product = [x for x in ac[1].split("\\")]
                        geopdf = logs_text["geojson"].copy()
                        initial_err = self.activ_cod + "|" + '_'.join(product) + "|" + file + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
                        geopdf.insert(0,initial_err)
                        geopdf.insert(2,geo)
                        self.logFile.writelogs(geopdf,self.conf_param["root_path"])
                if len(pdf_not_contain_layer_list) > 0:
                    for shp in pdf_not_contain_layer_list:
                        ac=self.root.split(self.activ_cod)
                        product = ""
                        product = [x for x in ac[1].split("\\")]
                        #check this line to see how write the output
                        shapefile = logs_text["shapefile"].copy()
                        initial_err = self.activ_cod + "|" + '_'.join(product) + "|" + file + "|" +  self.logFile.getCatValue(self.conf_param['VectorFormats'][self.type]) + "|" +  self.logFile.getIssueValue(self.conf_param['VectorFormats'][self.type]) + "|"
                        shapefile.insert(0,initial_err)
                        shapefile.insert(2,shp)
                        self.logFile.writelogs(shapefile,self.conf_param["root_path"])             
            else:
                #pdf not found
                no_image = self.conf_param['logsText']['geopdf']['notpdf'].copy()
                ac=self.root.split(self.activ_cod)
                product = ""
                product = [x + "_" for x in ac[1].split("\\")]
                if len(files) > 0:
                    if len(files) > 0:
                        initial_err =self.activ_cod + "|" + '_'.join(product) + "|" + file + "|" + self.logFile.getCatValue(self.conf_param['ImageFormats']['image']) + "|" + self.logFile.getIssueValue(self.conf_param['ImageFormats']['image']) + "|"
                    else:
                        initial_err =self.activ_cod + "|" + '_'.join(product) + "|" + self.logFile.getCatValue(self.conf_param['ImageFormats']['image']) + "|" + self.logFile.getIssueValue(self.conf_param['ImageFormats']['image']) + "|"             
                no_image.insert(0,initial_err)
                self.logFile.writelogs(no_image,self.conf_param["root_path"])

        except Exception as ex:
            e = logs_text["e"]
            e.append(str(ex))
            self.logFile.writelogs(e,self.conf_param["root_path"])