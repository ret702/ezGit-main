import json
import os
from models import models
import logging 

class user_input:

    logging.basicConfig(filename="log.txt", level=logging.DEBUG)
 
    def open_file(self, key="",data=""):
        assert key != ""
        assert key in ["username","token","repo_name","file_path"]
        if(key == "file_path"):
            assert os.path.exists(key)
        settings_file="settings.txt"
        is_empty=False
        try:
            if((os.path.exists(settings_file) == False) or (os.stat(settings_file).st_size == 0)):
                logging.debug("no settings files, printing new one...")
                is_empty=True
            
            with open(settings_file, "a+") as file:
                file.seek(0)
                lines_of_file = file.readlines()  
                if(is_empty):
                    file.write(json.dumps({key: data.strip()}))
                else: 
                        settings = models(models.format(lines_of_file))
                        if(data == "" and data in settings.__dict__):
                            print(settings.__dict__[key])
                        else:    
                            settings.__dict__.update({key: data})
                            file.seek(0)
                            file.truncate(0)
                            file.write(json.dumps(settings.__dict__))                 
        except Exception as e:
            logging.debug(e.args) 
        finally:
            file.close()
            user_input()


    def __init__(self):                                                      
        try:
            print("Please select...")
            print("1) add username")
            print("2) add repo name")
            print("3) add token")
            print("4) add repo file path")
            print("5) print username")
            print("6) print repo name")
            print("7) print token")
            user_choice =  int(input(">>> "))
            assert isinstance(user_choice,int)
            match user_choice:
                case 1:   
                    username= input("please input new username >>> ")
                    self.open_file(key="username",data=username)
                case 2:
                    repo_name= input("please input your repo name >>> ")
                    self.open_file( key="repo_name", data=repo_name)
                case 3:
                    token= input("please input your git auth token >>> ").strip()
                    self.open_file(key="token",data=token)
                case 4:
                    file_path= r'%s'% input("please input your repo file path >>> ")
                    self.open_file(key="file_path",data=file_path)
                case 5:
                    self.open_file(key="username")
                case 6:
                    self.open_file(key="repo_name")
                case 7:
                    self.open_file( key="token")         
        except Exception as e:
            logging.debug(e.args)    

user_input()