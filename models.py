import json
import logging
import ast
import re
class models(object): 
    logging.basicConfig(filename="log.txt", level=logging.DEBUG) 
    def __init__(self, m):
        logging.debug("init called from models")
        preview=any
        temp={}
        if(isinstance(m,dict)):
            for count,line in enumerate(m):
                test=self.innerclass(m[count])
                temp[count]=test          
            self.__dict__ = temp
        else:
            preview= json.loads(m)
            self.__dict__ = preview
    def format(json_str={}):
        logging.debug("format function called from models")
        try:
            if(isinstance(json_str,list) and (json_str != [])):
                li={}
                for count,item in enumerate(json_str):
                    li[count]=str(item).replace("\'", "\"")
                return li
            return json.dumps(json_str,sort_keys=True,indent=4)
        except Exception as e:
            logging.debug(e.args)  
       

    class innerclass(object):
        def __init__(self, m):
             self.__dict__ = json.loads(m)