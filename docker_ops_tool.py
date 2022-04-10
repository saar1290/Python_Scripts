import os
import subprocess
import requests
import urllib3
import tarfile
from time import sleep
import docker
import platform
from tqdm import tqdm
from colorama import Fore, Style

# Ignore some warnings 
urllib3.disable_warnings()

# initial docker client
docker_api = docker.from_env()

class List:
    @classmethod
    def list(self):
        list_all = docker_api.images.list()
        sorted_list=str(list_all).replace("<Image:","").replace(" ","").replace("[","").replace("]","").replace(">","").replace("'","").split(',')
        self.reverse_list = []
        # Reverse the soreted list docker images
        for i in reversed(sorted_list):
            self.reverse_list.append(i)
        # Append index to each image from reverse list
        n = 0
        for i in range(len(self.reverse_list)):
            n += 1
            print(f"{n}) "+self.reverse_list[i] + '\n')
    
class Push:
    def __init__(self, multiple, in_a_range):
        self.multiple = multiple
        self.range = in_a_range
        while True:
            self.registry = input(Fore.LIGHTMAGENTA_EX+"Enter the registry host ---> "+Style.RESET_ALL)
            if self.registry:
                break
            else:
                print(Fore.LIGHTRED_EX+"Empty answers is not accepted!")
                continue

    def tagging(self):
        if self.range:
            while True:
                start = input(Fore.LIGHTYELLOW_EX+"Select the start of range number of images to push ---> "+Style.RESET_ALL)
                end = input(Fore.LIGHTYELLOW_EX+"Select the end of range number of images to push ---> "+Style.RESET_ALL)
                remove_src = input(Fore.LIGHTCYAN_EX+"Do you want to delete the source tag after is tagged with the registry name? (yes/no) "+Style.RESET_ALL)
                if start and end and remove_src:
                    self.start = int(start)
                    self.end = int(end)
                    self.to_push = []
                    for l in range(self.start, self.end+1):
                        self.image = str(List.reverse_list[self.start -1]).replace(':', ',').split(',')[0]
                        self.tag = str(List.reverse_list[self.start -1]).replace(':', ',').split(',')[1]
                        self.start += 1
                        self.to_push.append(self.registry+"/"+self.image+":"+self.tag)
                        print(Fore.LIGHTCYAN_EX+f"Tagging image {self.image+':'+self.tag} to {self.registry}..."+Style.RESET_ALL)
                        self.taged = docker_api.api.tag(self.image+":"+self.tag, self.registry+"/"+self.image, self.tag, force=True)
                        print(Fore.LIGHTGREEN_EX+f"Image {self.registry+'/'+self.image+':'+self.tag} taged, and ready to push!"+Style.RESET_ALL)
                        if remove_src == 'yes':
                            self.untaged = docker_api.images.remove(self.image+":"+self.tag)
                            print(Fore.LIGHTMAGENTA_EX+f"Untagged {self.image+':'+self.tag}")
                        elif remove_src == 'no':
                            print(Fore.LIGHTMAGENTA_EX+f"Source image tag --> {self.image+':'+self.tag} is now duplicated with the new image tag --> {self.registry+'/'+self.image+':'+self.tag}")
                    break
                else:
                    print(Fore.LIGHTRED_EX+"Empty answers is not accepted!")
                    continue
        elif self.multiple:
            while True:
                images_ask = input(Fore.LIGHTMAGENTA_EX+"Choose images by number, separated by a spaces ---> "+Style.RESET_ALL)
                remove_src = input(Fore.LIGHTCYAN_EX+"Do you want to delete the source tag after is tagged with the registry name? (yes/no) "+Style.RESET_ALL)
                if images_ask and remove_src:
                    self.images = []
                    selected_images=str(images_ask).replace(" ", ",").split(',')
                    print(selected_images)
                    for n in selected_images:
                        self.images.append(n)                    
                else:
                    print(Fore.LIGHTRED_EX+"Empty answers is not accepted!"+Style.RESET_ALL)    
                    continue
                if self.images:
                    self.to_push = []
                    for i in self.images:
                        self.image = str(List.reverse_list[int(i) -1]).replace(':', ',').split(',')[0]
                        self.tag = str(List.reverse_list[int(i) -1]).replace(':', ',').split(',')[1]
                        self.to_push.append(self.registry+"/"+self.image+":"+self.tag)
                        print(Fore.LIGHTCYAN_EX+f"Tagging image {self.image+':'+self.tag} to {self.registry}..."+Style.RESET_ALL)
                        self.taged = docker_api.api.tag(self.image+":"+self.tag, self.registry+"/"+self.image, self.tag, force=True)
                        print(Fore.LIGHTGREEN_EX+f"Image {self.registry+'/'+self.image+':'+self.tag} taged, and ready to push!"+Style.RESET_ALL)
                        if remove_src == 'yes':
                            self.untaged = docker_api.images.remove(self.image+":"+self.tag)
                            print(Fore.LIGHTMAGENTA_EX+f"Untagged {self.image+':'+self.tag}")
                        elif remove_src == 'no':
                            print(Fore.LIGHTMAGENTA_EX+f"Source image tag --> {self.image+':'+self.tag} is now duplicated with the new image tag --> {self.registry+'/'+self.image+':'+self.tag}")
                    break

    def pushing(self):
        while True:
            insecure = input(Fore.LIGHTBLUE_EX+"Is your registry with authentication method? (yes/no) "+Style.RESET_ALL)
            if insecure == 'yes':
                user = str(input(Fore.LIGHTCYAN_EX+"Enter the username registry ---> "+Style.RESET_ALL))
                password = str(input(Fore.LIGHTCYAN_EX+"Enter the password registry ---> "+Style.RESET_ALL))
                if user and password:
                    docker_api.login(username=f'{user}', password=f'{password}', registry=f"https://{self.registry}/v2")
                    for i in self.to_push:
                        print(Fore.LIGHTYELLOW_EX +f"Pushing image {i} to {self.registry}..."+Style.RESET_ALL)
                        sleep(3)
                        for line in docker_api.images.push(i, stream=True, decode=True):
                            print(line)
                    break
                else:
                    print(Fore.LIGHTRED_EX+"Empty authentication is not accepted on this method!"+Style.RESET_ALL)
                    continue
            elif insecure == 'no':
                for i in self.to_push:
                    print(Fore.LIGHTYELLOW_EX +f"Pushing image {i} to {self.registry}..."+Style.RESET_ALL)
                    sleep(3)
                    for line in docker_api.images.push(i, stream=True, decode=True):
                        print(line)
                break
            else:
                print(Fore.LIGHTRED_EX+"Please answer yes or no!"+Style.RESET_ALL)

class Save:
    def __init__(self, multiple, in_a_range):
        self.multiple = multiple
        self.range = in_a_range
    
    def save_image(self):
        # Check the type of platfrom, for query the current path directory
        if platform.system() == 'Windows':
            pwd = os.getenv('%cd%')
        elif platform.system() == 'Linux':
            pwd = os.environ['PWD']
        if self.range:
            start = input(Fore.LIGHTYELLOW_EX+"Select the start of range number of images to save ---> "+Style.RESET_ALL)
            end = input(Fore.LIGHTYELLOW_EX+"Select the end of range number of images to save ---> "+Style.RESET_ALL)
            self.start = int(start)
            self.end = int(end)
            for l in range(self.start, self.end+1):
                self.image = str(List.reverse_list[self.start -1])
                self.basename = str(List.reverse_list[self.start -1]).replace(':', '_').replace('/', '_').split(',')[0]
                self.start += 1
                image = docker_api.images.get(self.image)
                image_tar = self.basename+".tar"
                print(Fore.LIGHTCYAN_EX+f"Saving image {self.image} to {image_tar}..."+Style.RESET_ALL)
                f = open(image_tar, 'wb')
                image_chunks = []
                for chunk in tqdm(image.save()):
                    image_chunks.append(chunk)
                for p in tqdm(iterable=image_chunks, total=len(image_chunks), desc='Saving progress of {}'.format(self.basename)):
                    f.write(p)
                f.close()  
                # Archiveing images to an one gzip file, and remove each one after that
                images_dir = pwd
                ext = ('.tar') 
                a = tarfile.open('images.gzip', 'w')
                images_tars = []
                for file in os.listdir(images_dir):
                    images_tars.append(file)
            for i in tqdm(iterable=images_tars, total=len(images_tars), desc='Adding progress of {} to images.gzip'.format(self.basename)):
                if i.endswith(ext):
                    print(Fore.LIGHTGREEN_EX+" Adding {} to images.gzip...".format(i)+Style.RESET_ALL)
                    a.add(i)
                    os.remove(i)
            a.close()

        elif self.multiple:
            while True:
                self.images = []
                images_ask = input(Fore.LIGHTMAGENTA_EX+"Choose images by number, separated by a spaces --->"+Style.RESET_ALL)
                if images_ask:
                    selected_images=str(images_ask).replace(" ", ",").split(',')
                    print(selected_images)
                    for n in selected_images:
                        self.images.append(n)
                    break
                elif images_ask == "":
                    print(Fore.LIGHTRED_EX+"Empty list or alphameric is not accepted!"+Style.RESET_ALL)    
                    continue
            for i in self.images:
                self.image = str(List.reverse_list[int(i) -1])
                self.basename = str(List.reverse_list[int(i) -1]).replace(':', '_').replace('/', '_').split(',')[0]
                image = docker_api.images.get(self.image)
                image_tar = self.basename+".tar"
                print(Fore.LIGHTCYAN_EX+f"Saving image {self.image} to {image_tar}..."+Style.RESET_ALL)
                f = open(image_tar, 'wb')
                image_chunks = []
                for chunk in tqdm(image.save()):
                    image_chunks.append(chunk)
                for p in tqdm(iterable=image_chunks, total=len(image_chunks), desc='Saving progress of {}'.format(self.basename)):
                    f.write(p)
                f.close()  
                # Archiveing images to an one gzip file, and remove each one after that
                images_dir = pwd
                ext = ('.tar') 
                a = tarfile.open('images.gzip', 'w')
                images_tars = []
                for file in os.listdir(images_dir):
                    images_tars.append(file)
            for i in tqdm(iterable=images_tars, total=len(images_tars), desc='Adding progress of {} to images.gzip'.format(self.basename)):
                if i.endswith(ext):
                    print(Fore.LIGHTGREEN_EX+" Adding {} to images.gzip...".format(i)+Style.RESET_ALL)
                    a.add(i)
                    os.remove(i)

class Pull:
    def __init__(self, images):
        self.images = str(images).replace(" ", ",").split(',')

    def pull_images(self):
        to_pull = []
        for i in self.images:
            to_pull.append(i)
        print(to_pull)
        for p in to_pull:
            self.image = docker_api.images.pull(f'{p}')
            print(Fore.LIGHTGREEN_EX+f"Image {p} pulled successfully"+Style.RESET_ALL)
            print(self.image.id)

class Remove:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def get_images(self):
        catalog = requests.get(f"{self.url}/_catalog", verify=False, headers=self.headers).json(object_hook=dict) # Query the full repository catalog
        images_list = []
        for index, image in enumerate(catalog['repositories']):
            images_list.append(image)
            index += 1
            print(Fore.LIGHTYELLOW_EX+f"{index}) "+Style.RESET_ALL+ image)
        while True:
            try:
                print("--------------------------------")
                i = int(input(Fore.LIGHTBLUE_EX+"Please choose a repository: "+Style.RESET_ALL)) - 1 
                self.image = images_list[i]
                print("----------------")
                print (Fore.LIGHTGREEN_EX+"Image :"+Style.RESET_ALL,self.image)
                break
            except ValueError:
                print(Fore.LIGHTRED_EX+"Wrong choise, please select only index number!"+Style.RESET_ALL)
            except IndexError:
                print(Fore.LIGHTRED_EX+"Index out of range, please try again"+Style.RESET_ALL)

    def delete_tags(self):
        r = requests.get(f"{self.url}/{self.image}/tags/list", verify=False, headers=self.headers).json() # List tags of image input
        try:
            tags_list = []
            print("----------------")
            print(Fore.LIGHTMAGENTA_EX+f"{self.image} tags:"+Style.RESET_ALL)
            print("----------------")
            for index, t in enumerate(r['tags']):
                tags_list.append(t)
                index += 1
                print(Fore.LIGHTYELLOW_EX+f"{index}) Tag:"+Style.RESET_ALL,t)
                print("----------------")
            i = int(input(Fore.LIGHTBLUE_EX+"Choose a tag to delete: "+Style.RESET_ALL)) - 1
            tag = tags_list[i]
            manifast = requests.head(f"{self.url}/{self.image}/manifests/{tag}", verify=False, headers=self.headers).headers['Docker-Content-Digest'] # Query the manifest digest
            requests.delete(f"{self.url}/{self.image}/manifests/{manifast}", verify=False, headers=self.headers) # Delete the image tag manifest
            print(Fore.LIGHTGREEN_EX+f"Deleting manifest: {manifast} from image tag: {self.image}:{tag}"+Style.RESET_ALL)
            test = requests.get(f"{self.url}/{self.image}/manifests/{tag}", verify=False, headers=self.headers)
            response = test.status_code
            if response == 404:
                print(Fore.LIGHTMAGENTA_EX+f"Image {self.image}:{tag} removed"+Style.RESET_ALL)
        except Exception:
            if 'NoneType':
                print(Fore.LIGHTRED_EX+f"Image tag {self.image} not exist ---->"+Style.RESET_ALL)

# Class for initializing operations classes
class Ops:
    def __init__(self, save_range, save_multiple, push_range, push_multiple, pull, remove):
        self.save_range = save_range
        self.save_multiple = save_multiple
        self.push_range = push_range
        self.push_multiple = push_multiple
        self.pull = pull
        self.remove = remove

        if self.save_range:
            List.list()
            in_a_range = True
            multiple = False
            save_in_range = Save(multiple, in_a_range)
            save_in_range.save_image()

        if self.save_multiple:
            List.list()                
            multiple = True
            in_a_range = False
            save_in_multiple = Save(multiple, in_a_range)
            save_in_multiple.save_image()
        
        if self.push_range:
            List.list()
            in_a_range = True
            multiple = False
            push_in_range = Push(multiple, in_a_range)
            push_in_range.tagging()
            push_in_range.pushing()

        if self.push_multiple:
            List.list()
            in_a_range = False
            multiple = True
            push_in_multiple = Push(multiple, in_a_range)
            push_in_multiple.tagging()
            push_in_multiple.pushing()
        
        if self.pull:
            while True:
                images = input(Fore.LIGHTYELLOW_EX+"Enter the images to pull as image:tag by spaces ---> "+Style.RESET_ALL)
                if images:
                    pull_images = Pull(images)
                    pull_images.pull_images()
                    break
                else:
                    print(Fore.LIGHTRED_EX+"Empty list is not accepted!"+Style.RESET_ALL)

        if self.remove:
            while True:
                url = input(Fore.LIGHTMAGENTA_EX+"Enter the URL of your private registry with the API version trailing (/v2) ---> "+Style.RESET_ALL)
                headers = {"Authorization" : "Basic %s" % "", "Accept" : "application/vnd.docker.distribution.manifest.v2+json"}
                if url and headers:
                    remove_from_reg = Remove(url, headers)
                    remove_from_reg.get_images()
                    remove_from_reg.delete_tags()
                    break
                else:
                    print(Fore.LIGHTRED_EX+"Empty URL is not accepted!"+Style.RESET_ALL)
                    continue

def delete_none():
      docker_api.images.prune({'dangling': 'true'})
    #   dangling = subprocess.run(['docker','images','-qf','dangling=true'], capture_output=True, text=True).stdout.split()
    #   for d in dangling:
    #         subprocess.run([f'docker','rmi',d,'-f'])

# Main manu
def main():
    while True:
        print("----------------------")
        print(Fore.GREEN+"Docker Operations Tool"+Style.RESET_ALL)
        print("----------------------")
        print(Fore.MAGENTA+"Author: Saar Buskila"+Style.RESET_ALL)
        print("--------------------")
        print()
        print(Fore.LIGHTYELLOW_EX+"Type save --> for saving images in range/multiple"+Style.RESET_ALL)
        print(Fore.LIGHTCYAN_EX+"Type push --> for pushing images in range/multiple"+Style.RESET_ALL)
        print(Fore.LIGHTMAGENTA_EX+"Type pull --> for pulling images"+Style.RESET_ALL)
        print(Fore.LIGHTWHITE_EX+"Type prune --> for pruning a dangling images"+Style.RESET_ALL)
        print(Fore.LIGHTRED_EX+"Type remove --> for removing tag/repository in a private docker registry"+Style.RESET_ALL)
        print("*********************")
        ask = input(Fore.LIGHTGREEN_EX+"Choose an operation: "+Style.RESET_ALL)

        if ask == 'save':
            while True:
                mode = input(Fore.YELLOW+"Would you like to save images in a range or in multiple? options(range/multiple)--->"+Style.RESET_ALL)
                if mode == 'range':
                    save_range = True
                    save_multiple = False
                    push_range = False
                    push_multiple = False
                    pull = False
                    remove = False
                    r = Ops(save_range, save_multiple, push_range, push_multiple, pull, remove)
                    r.save_range
                    break
                elif mode == 'multiple':
                    save_range = False
                    save_multiple = True
                    push_range = False
                    push_multiple = False
                    pull = False
                    remove = False
                    m = Ops(save_range, save_multiple, push_range, push_multiple, pull, remove)
                    m.save_multiple
                    break
                else: 
                    print(Fore.LIGHTRED_EX+"Wrong selection, please answer range/multiple"+Style.RESET_ALL)
                    continue
            break     
        elif ask == 'push':
            while True:
                mode = input(Fore.YELLOW+"Would you like to push images in a range or in multiple? options(range/multiple)--->"+Style.RESET_ALL)
                if mode == 'range':
                    save_range = False
                    save_multiple = False
                    push_range = True
                    push_multiple = False
                    pull = False
                    remove= False
                    r = Ops(save_range, save_multiple, push_range, push_multiple, pull, remove)
                    r.push_range
                    break
                elif mode == 'multiple':
                    save_range = False
                    save_multiple = False
                    push_range = False
                    push_multiple = True
                    pull = False
                    remove = False
                    m = Ops(save_range, save_multiple, push_range, push_multiple, pull, remove)
                    m.push_multiple
                    break
                else: 
                    print(Fore.LIGHTRED_EX+"Wrong selection, please answer range/multiple"+Style.RESET_ALL)
                    continue
            break
        elif ask == 'pull':
            save_range = False
            save_multiple = False
            push_range = False
            push_multiple = False
            pull = True
            remove = False
            p = Ops(save_range, save_multiple, push_range, push_multiple, pull, remove)
            p.pull
            break
        elif ask == 'prune':
            delete_none()
            break
        elif ask == 'remove':
            save_range = False
            save_multiple = False
            push_range = False
            push_multiple = False
            pull = False
            remove = True
            r = Ops(save_range, save_multiple, push_range, push_multiple, pull, remove)
            r.remove
            break
        else: 
            continue
main()