import requests
from models import models
import json
import base64
import os 
import logging
import glob

default_file_name = "test"
settings="settings.txt"
status_empty=-1
logging.basicConfig(filename="log.txt", level=logging.DEBUG)

def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

def main():   #get auth token, connect, and pull initial repo
    try:
        files_in_local_repo=""
        
        with open(settings, "r") as settings_file:
            #get settings
            file_contents=settings_file.readlines()
        model =   models(models.format(json.loads(file_contents[0])))
        # file_structure = {}
        # for root,dir_names,files in os.walk(model.file_path):
        #         file_structure.update(roots=dir_names)
        #         print(f"dirs: {dir_names}")
        #         print(f"files in folder: {files}")
        #         print(file_structure) 
        ##TODO: Add recusively files/folders to file_structure
        #get all files in current directory
        files_in_local_repo = []
        for path in listdir_nohidden(model.file_path):
            #ignore file with personal data
            if(path.startswith(".") or os.path.basename(path) =="settings.txt"
                or os.path.basename(path) == "__pycache__" 
                or os.path.basename(path) == "log.txt"):
                pass
            else:
                print(os.path.basename(path))
                files_in_local_repo.append(os.path.basename(path))
    except Exception as e: 
        logging.debug(e.args)
    finally:
        update_file(files_in_local_repo,model)
    print(files_in_local_repo)
    
def put_(url,model,data):
    print("data for post: " , data)
    return requests.put(url = url, auth = ("{model.username}",model.token),json = data)
    
def get_(url,headers):
    return  requests.get(url, headers)

def post_(headers,model):
    payload = {
                "name":model.repo_name
                }
    return requests.post(url =" https://api.github.com/user/repos",
                                      headers=json.loads(headers), json= payload)

def get_repo(update_url,data=None,model=any):
    try:
        header_types = ["Accept","Authorization","X-GitHub-Api-Version"]
        header_data = ["application/vnd.github+json","Bearer {0}".format(model.token),"2022-11-28"]
        headers= json.dumps(dict(zip(header_types,header_data)))
        print(f"repo url: {update_url}")
        response = None
        if(data):
            response=put_(update_url,model,data)
        else:
            response=get_(update_url,headers)    
        print("status: " + str(response.status_code))
     
        #create repo if none exists
        if(response.status_code == 404  or 
           json.loads(response.text)["message"] == "This repository is empty."
           or json.loads(response.text)["message"] == "Not Found"):
           post_(headers,model)
           return status_empty
    except Exception as e:
        logging.debug(e.args)
    finally:
        model_list=[] #if response is a list there we have more than 1 file 
                    #and we need to create different models separately
        if(isinstance(response,list)):
            for file in response:
                model_list.append(models(models.format(file))) #converts to object
                #write_to_file(f"{file_name}.py",response_json)
            return model_list
        else:
            d=json.loads(response.text)
           # test=models(models.format(d))
            return models(models.format(d))
    

   
def write_to_file(filename=f"{default_file_name}.py",data=None):
    if(data):
        with open(filename, 'w') as file:
            file.write(json.dumps(data,sort_keys=True,indent=4))
            #file.write("def "+ "get_"+ a +":" + "\n" + "\t" +"return " +b  )
            file.close()



def convert_file_base64(filename=None,path=None):
    try:
        with open(filename,'rb') as file:
            converted_file_contents = base64.b64encode(file.read())
            file.close()
        return converted_file_contents.decode("utf-8") #have to decode to utf-8 because
                                        #the stupid b symbol in front of byte string
    except Exception as e:
        logging.debug(e.args)



# def isBase64(s):
#     try:
#         return base64.b64encode(base64.b64decode(s)) == s
#     except Exception:
#         return False


###branch_url = "https://api.github.com/repos/%s/%s/branches/main"
###branch_models = get_repo(branch_url % (f"{user_name}",f"{repo_name}"))
###sha = branch_models.commit["sha"]



def update_file(files_in_local_repo=[],model = any):
    try:
        #get all files sha's in repo
        repo_url= f"https://api.github.com/repos/{model.username}/{model.repo_name}/contents/"
        payload = {
                                "message" : "commit",
                                "branch" : "master",             
                                }
        
        if(len(files_in_local_repo) > 0):
            files_in_remote= get_repo(repo_url,model=model)
            if  files_in_remote != status_empty:  
                # we need to get all the remote file names beforehand
                remote_files=[]
                try:
                    for k,v in files_in_remote.__dict__.items():        
                        remote_files.append(v.name)
                except Exception as e:
                    logging.debug(e.args)
            
            for local_file in files_in_local_repo: 
                #remove this from production, only for testing
                #so we dont upload git token
                if(local_file == "settings.txt"):
                    pass
                else:
                    if(files_in_remote !=status_empty and local_file in remote_files):
                        for key,remote_file in files_in_remote.__dict__.items():      
                                #if file matches remote we update it
                                if local_file ==  remote_file.name :
                                    try:
                                        print(f"sha for file: {remote_file.name} {remote_file.sha}")
                                        path = f'''{model.file_path}\\{local_file}'''
                                        content =  convert_file_base64(path)
                                        #add sha for existing files
                                        payload.update({"sha" :  remote_file.sha,
                                        "content": content})
                                        repo_contents = get_repo(repo_url + local_file,payload,model=model)
                                    except Exception as e:
                                        print(e)
                    else:
                            #no sha for new files
                            print("new file to be added to remote: " + local_file)
                            path = f"{local_file}"
                            content =  convert_file_base64(path)
                            payload.update({"content": content})
                            repo_contents = get_repo(repo_url + local_file,payload,model=model)
    except Exception as e:
        print(repr(e.args))
                


#must be called at the beginning of the program
main()









