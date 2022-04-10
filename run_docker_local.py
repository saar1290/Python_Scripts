import os 
from datetime import datetime
import subprocess
from docker import client
from py3nvml import *
from py3nvml.py3nvml import nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlDeviceGetName, nvmlInit, nvmlSystemGetDriverVersion
from colorama import Fore, Style


# Set var fo docker client env
cl = client.from_env()

def delete_none():
      cl.images.prune({'dangling': 'true'})
      dangling = subprocess.run(['docker','images','-qf','dangling=true'], capture_output=True, text=True).stdout.split()
      for d in dangling:
            subprocess.run([f'docker','rmi',d,'-f'])
            
def images(x):
      delete_none()
      list_images = str(cl.images.list(name=x))
      sorted_list=str(list_images).replace("<Image:","").replace(" ","").replace("[","").replace("]","").replace(">","").replace("'","").split(',')
      reverse_list = []
      
      # Reverse the soreted list from docker images
      for i in reversed(sorted_list):
            reverse_list.append(i)
      # Append index to each image from reverse list
      n = 0
      for i in range(len(reverse_list)):
            n += 1
            print(f"{n}) "+reverse_list[i] + '\n')
      # Ask the user for an index and if it empty or larger then length of reverse list it ask again until the user answer the currect index
      while True:
            quest_img = input(Fore.LIGHTCYAN_EX+ "Choose an image: "+Style.RESET_ALL)
            if quest_img == '' or int(quest_img) > len(reverse_list):
                  print(Fore.LIGHTRED_EX+"Bad index or selection... please choose correct number of image"+Style.RESET_ALL)
            else:
                  break
      # Converting the question to integer and subtracting at 1, for image in index of reverse list
      quest_img = int(quest_img)
      quest_img -= 1
      images.image = reverse_list[quest_img]
      print(Fore.LIGHTGREEN_EX+"Your image is:"+Style.RESET_ALL,images.image)

def conv_Bits_to_MB(input_bits):
        magabyte = 1024*1000
        convert_mb = input_bits / magabyte
        return convert_mb

# Set an empty array for GPU list avalible
av_list = []

# Init nvnml
nvmlInit()

# Get the total number of GPU devices on system
deviceCount= nvmlDeviceGetCount()

# Set array for selected GPU
selected_GPU = []

# Set array for full list of GPU
full_list = []

def handle_gpu(x):
      handle = nvmlDeviceGetHandleByIndex(x)
      mem = nvmlDeviceGetMemoryInfo(handle)
      handle_gpu.gpu_type = nvmlDeviceGetName(handle)
      handle_gpu.tmem=str(conv_Bits_to_MB(mem.total)).split('.')[0]
      handle_gpu.umem=str(conv_Bits_to_MB(mem.used)).split('.')[0]

def select_n_gpu():       
      print(Fore.LIGHTCYAN_EX + "Total GPU devices",":"+ Style.RESET_ALL ,deviceCount)
      for g in range(deviceCount):
            full_list.append(g)
    	            
      # Show the GPU driver version
      print()
      print(Fore.LIGHTCYAN_EX +"Driver Version",":"+Style.RESET_ALL,nvmlSystemGetDriverVersion())
      print()
      
      g = int(full_list[0])
      handle_gpu(g)

      # Check each interact if the gpu from full list is free to use, and add it to a avalible list
      umem = int(handle_gpu.umem)
      minm = 1000
      if umem >= minm:
            print(Fore.LIGHTRED_EX + "GPU",full_list, "is Out of memory" + Style.RESET_ALL)      
      
      # Print the avalible list of GPU on system
      print()
      print(Fore.LIGHTGREEN_EX+ "Avalible GPU for use:"+Style.RESET_ALL,Fore.LIGHTYELLOW_EX+f"(The maximum used memory, to use a gpu it {minm}MB)"+Style.RESET_ALL,g)
      print()
      print(Fore.LIGHTCYAN_EX+"Your GPU devices is ready to use:"+Style.RESET_ALL)
      
      # Print the results of user selected
      print()
      print(Fore.LIGHTBLUE_EX + "GPU",g,":" + Style.RESET_ALL,handle_gpu.gpu_type)
      print(Fore.LIGHTMAGENTA_EX + "Total Memory of GPU",g,":" + Style.RESET_ALL ,handle_gpu.tmem,"MiB")
      print(Fore.LIGHTGREEN_EX + "Total Used Memeoy of GPU",g,":" + Style.RESET_ALL, handle_gpu.umem,"MiB")
      selected_GPU.append(g)

def resource_question():
      # Ask the user for which resources he need
      while True:
            resource_question.runtime = input(Fore.LIGHTMAGENTA_EX+"Which resources do you need, gpu/cpu? "+Style.RESET_ALL)
            if resource_question.runtime not in ["gpu","cpu"]:
                  print(Fore.LIGHTRED_EX+"Please answer with gpu or cpu!"+Style.BRIGHT)
            else:
                  break
      if resource_question.runtime == "gpu":
            resource_question.rt = "nvidia"
            select_n_gpu()
            
      if resource_question.runtime == "cpu":
            resource_question.rt = ""
            
def cmdline():
      # Set environment for container
      USER = os.environ['USER']
      user = f"user={USER}"
      try:
            display = os.environ['DISPLAY']
            x = f"DISPLAY={display}"
      except KeyError as error:
            print(error)
            print(Fore.LIGHTRED_EX+"Please exit from the server and try to start a new ssh session with -X arg..."+Style.RESET_ALL)
            os._exit(1)
      xauthority = "XAUTHORITY=/app/.Xauthority"
      sel_gpu = str(selected_GPU).replace("[","").replace("]","")
      gpu = f"NVIDIA_VISIBLE_DEVICES={sel_gpu}"
      
      # Set share file and directory for container
      home = os.environ['HOME']
      # ld_conf = "/etc/ldap.conf:/etc/ldap.conf:ro"
      # ld_sec = "/etc/ldap.secret:/etc/ldap.secret:ro"
      # ld_crt_conf = "/etc/ldap/ldap.conf:/etc/ldap/ldap.conf:ro"
      # ld_crt = "/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro"
      # nss_conf = "/etc/nsswitch.conf:/etc/nsswitch.conf:ro"
      # pam_pass = "/etc/pam.d/common-password:/etc/pam.d/common-password:ro"
      # pam_sess = "/etc/pam.d/common-session:/etc/pam.d/common-session:ro"
      # data = "/data/Projects/:/data"
      # data2 = "/data2/Projects/:/data2"
      app = f"{home}:/app"
      # entry = "/data/entry.sh:/data/entry.sh"
            
      # Run command
      now = datetime.now()
      today = now.strftime("%d.%m.%Y_%H-%M-%S")
      name = f"LDAP-{USER}-{today}"
      rt = resource_question.rt   
      subprocess.call([f'docker','run','--runtime',rt,'--rm','-it','--shm-size','16G','--memory=64g','--net','host','-e',user,'-v',app,'-e',x,'-e',xauthority,'-e',gpu,'--name',name,images.image])

# Main script
images("")
resource_question()
cmdline()