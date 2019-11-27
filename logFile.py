import os
import datetime
import socket

class logFile():
 
    def writelogsfirst(self,value,root):
        root1 = os.path.join(root, 'log.txt')
        with open(root1,'w') as file:
            file.write(str(value)+"\n")

    def getCatValue(self,config):
        if config.get('cat')!=None:
            return config['cat'];
        return '';
    def getIssueValue(self,config):
        if config.get('issue')!=None:
            return config['issue'];
        return '';


    def writelogs(self,value):
        d=datetime.datetime.now()
        date= d.strftime("%b") + " " + d.strftime("%d")+" "+d.strftime("%H")+":"+d.strftime("%M")+":"+d.strftime("%S")
        pc_name=socket.gethostname()
        standar="dcct_rrm"
        concatenate = date + " " + pc_name + " " + standar + ": "  
        for val in value:
            concatenate += val.upper()
        
            
        print (concatenate.splitlines()[0])
        
        #root1 = os.path.join(root, 'log.txt')
        #with open(root1,'a+') as file:
        #    file.write(concatenate)