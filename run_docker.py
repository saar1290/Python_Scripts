import os 
from datetime import datetime
import subprocess
from docker import client
from py3nvml import *
from py3nvml.py3nvml import nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlDeviceGetName, nvmlInit, nvmlSystemGetDriverVersion
from colorama import Fore, Style


# Set var fo docker client env
cl = client.from_env()
client.APIClient.tag

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
      quest_img = int(quest_img) - 1
      images.image = reverse_list[quest_img]
      print(Fore.LIGHTGREEN_EX+"Your image is:"+Style.RESET_ALL,images.image)

def conv_Bits_to_MB(input_bits):
        magabyte = 1024*1000
        convert_mb = input_bits / magabyte
        return convert_mb

# Set an empty array for GPU list available
av_list = []

# Init nvnml
nvmlInit()

# Get the total number of GPU devices on system
deviceCount= nvmlDeviceGetCount()

# Set array for selected GPU
selected_GPU = []

# Set array for full list of GPU
full_list = []

def user_question():
      try:
      # Ask the user for number of GPUs he's needed
            user_question.num_gpu = int(input(Fore.LIGHTYELLOW_EX + "How much GPU do you need? "+ Style.RESET_ALL))
      except ValueError as error:
            if error:
                  print(Fore.LIGHTRED_EX+"Please choose a number of quantity GPU to use, empty or letter option is not accept"+Style.BRIGHT)
                  user_question()
      # Set an attribute for function
      user_question.selected_dv = int(user_question.num_gpu)
      # Checking if the selected GPU devices number from input is not greater than the system GPU devices 
      if user_question.selected_dv > deviceCount:
            raise ValueError(Fore.LIGHTRED_EX + 'GPU selection number is out of range on system devices'+ Style.RESET_ALL)

def handle_gpu(x):
      handle = nvmlDeviceGetHandleByIndex(x)
      mem = nvmlDeviceGetMemoryInfo(handle)
      handle_gpu.gpu_type = nvmlDeviceGetName(handle)
      handle_gpu.tmem=str(conv_Bits_to_MB(mem.total)).split('.')[0]
      handle_gpu.umem=str(conv_Bits_to_MB(mem.used)).split('.')[0]

def select_n_gpu():       
      # Ask the user if he need to use just Tesla GPU, other then he get the full list of gpu
      while True: 
            answer = input(Fore.LIGHTYELLOW_EX + "Do you need just Tesla GPU? " + Style.RESET_ALL) 
            tesla = answer.lower()
            if answer == '' or not tesla in ['yes','no']: 
                  print(Fore.LIGHTRED_EX+'Please answer with yes or no!'+Style.BRIGHT)
            else:
                  break
      while True: 
            answer = input(Fore.LIGHTYELLOW_EX + "Do you need just A5000 GPU? " + Style.RESET_ALL) 
            a5000 = answer.lower()
            if answer == '' or not a5000 in ['yes','no']: 
                  print(Fore.LIGHTRED_EX+'Please answer with yes or no!'+Style.BRIGHT)
            else:
                  break

      for g in range(deviceCount):
            full_list.append(g)      

      if tesla == 'yes' and a5000 == 'yes':
            a50001 = full_list[-5]
            a50002 = full_list[-4]
            a50003 = full_list[-3]
            tesla1 = full_list[-2]
            tesla2 = full_list[-1]
            full_list.clear()
            full_list.extend([tesla1,tesla2,a50001,a50002,a50003])
            full_list.sort()
            print(Fore.LIGHTCYAN_EX + "Total Tesla and A5000 GPU devices",":"+ Style.RESET_ALL ,full_list)
            user_question()
      
      elif tesla == 'yes':   
            tesla1 = full_list[-2]
            tesla2 = full_list[-1]
            full_list.clear()
            full_list.extend([tesla1,tesla2])
            print(Fore.LIGHTCYAN_EX + "Total Tesla GPU devices",":"+ Style.RESET_ALL ,full_list)
            user_question()
      
      elif a5000 == 'yes':   
            a50001 = full_list[-5]
            a50002 = full_list[-4]
            a50003 = full_list[-3]
            full_list.clear()
            full_list.extend([a50001,a50002,a50003])
            print(Fore.LIGHTCYAN_EX + "Total A5000 GPU devices",":"+ Style.RESET_ALL ,full_list)
            user_question()

      elif tesla == 'no' and a5000 == 'no': 
            print(Fore.LIGHTCYAN_EX + "Total GPU devices",":"+ Style.RESET_ALL ,deviceCount)
            user_question()
            
      # Show the GPU driver version 
      print()
      print(Fore.LIGHTCYAN_EX +"Driver Version",":"+Style.RESET_ALL,nvmlSystemGetDriverVersion())
      print()

      # Check each interact if the gpu from full list is free to use, and add it to a available list
      for i in full_list:
            handle_gpu(i)    
            umem = int(handle_gpu.umem)
            minm = 256
            if umem >= minm:
                  print(Fore.LIGHTRED_EX + "GPU",i, "is out of memory" + Style.RESET_ALL)
            else:
                  av_list.append(i)
      
      # Print the available list of GPU on system
      print()
      print(Fore.LIGHTGREEN_EX+ "Available GPU list for use:"+Style.RESET_ALL,Fore.LIGHTYELLOW_EX+f"(The maximum used memory, to use a gpu it {minm}MiB)"+Style.RESET_ALL,av_list)
      print()
      print(Fore.LIGHTCYAN_EX+"Your GPU devices is ready to use:"+Style.RESET_ALL)
      # A loop each quantity times (based on the value in the user question), and add it to the gpu selection list
      quest = user_question.selected_dv
      for a in range(quest):
            # Check if user selection is greater then number of available GPU on system, and take the all available GPU for him
            if quest > len(av_list):
                  try: 
                        for i in av_list:
                              # Remove brackets to append list to list, then handle the info on GPU by index i
                              i = int(str(i).replace("[","").replace("]",""))
                              handle_gpu(i)     
                              print()
                              print(Fore.LIGHTBLUE_EX + "GPU",i,":" + Style.RESET_ALL,handle_gpu.gpu_type)
                              print(Fore.LIGHTMAGENTA_EX + "Total Memory of GPU",i,":" + Style.RESET_ALL ,handle_gpu.tmem,"MiB")
                              print(Fore.LIGHTGREEN_EX + "Total Used Memeoy of GPU",i,":" + Style.RESET_ALL, handle_gpu.umem,"MiB")      
                              selected_GPU.append(i)
                  except IndexError as msg:
                        print(msg)
                        print(Fore.LIGHTRED_EX+"No GPU devices is left to use"+Style.RESET_ALL)      
                  break
            # Set var a each interact to the number of index from the av_list array with brackets remove, and convert it to integer 
            a = int(str([av_list[a]]).replace("[","").replace("]",""))
            # handle the info on gpu by index a
            handle_gpu(a)
            # Print the results of user selected
            print()
            print(Fore.LIGHTBLUE_EX + "GPU",a,":" + Style.RESET_ALL,handle_gpu.gpu_type)
            print(Fore.LIGHTMAGENTA_EX + "Total Memory of GPU",a,":" + Style.RESET_ALL ,handle_gpu.tmem,"MiB")
            print(Fore.LIGHTGREEN_EX + "Total Used Memeoy of GPU",a,":" + Style.RESET_ALL, handle_gpu.umem,"MiB")
            selected_GPU.append(a)
      print()
      print(Fore.LIGHTMAGENTA_EX + "Full list of gpu:" + Style.RESET_ALL,full_list)

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
      # Set environments for the container
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
      
      # Set share file and directory for the container
      home = os.environ['HOME']
      ld_conf = "/etc/ldap.conf:/etc/ldap.conf:ro"
      ld_sec = "/etc/ldap.secret:/etc/ldap.secret:ro"
      ld_crt_conf = "/etc/ldap/ldap.conf:/etc/ldap/ldap.conf:ro"
      ld_crt = "/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro"
      nss_conf = "/etc/nsswitch.conf:/etc/nsswitch.conf:ro"
      pam_pass = "/etc/pam.d/common-password:/etc/pam.d/common-password:ro"
      pam_sess = "/etc/pam.d/common-session:/etc/pam.d/common-session:ro"
      data = "/data/Projects/:/data"
      data2 = "/data2/Projects/:/data2"
      app = f"{home}:/app"
      entry = "/data/entry.sh:/data/entry.sh"
            
      # Runing the container
      now = datetime.now()
      today = now.strftime("%d.%m.%Y_%H-%M-%S")
      name = f"LDAP-{USER}-{today}"
      rt = resource_question.rt
      subprocess.call([f'docker','run','--runtime',rt,'--rm','-it','--shm-size','16G','--memory=64g','--net','host','-e',user,'-v',ld_conf,'-v',ld_sec,'-v',ld_crt_conf,'-v',ld_crt,'-v',nss_conf,'-v',pam_pass,'-v',pam_sess,'-v',app,'-v',data,'-v',data2,'-v',entry,'-e',x,'-e',xauthority,'-e',gpu,'--name',name,images.image])

# Main script
images("")
resource_question()
cmdline()