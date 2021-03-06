#!/bin/bash

sudo apt-get install -y git
sudo apt-get install -y python3-pip

pip3 install --upgrade oauth2client
pip3 install PyOpenSSL
pip3 install gspread

python3 ~/server-inventory/server2sheet.py