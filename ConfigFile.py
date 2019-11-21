import json

class ConfigFile:
    def __init__(self,file_path):
        self.file_path = file_path
    
    def readJson(self):
        with open(self.file_path, 'r') as f:
            schema_data = f.read()
            geoson_data = json.loads(schema_data)
        return geoson_data