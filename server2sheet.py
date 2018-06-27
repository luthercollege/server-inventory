#!/usr/bin/python3

import os
import subprocess
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def getRowIdxByName(wks, name):
    rows = wks.get_all_values()

    colIdx = 0
    for i, col in enumerate(rows[0]):
        if col == 'serverName': colIdx = i + 1
    
    for idx, row in enumerate(rows):
        if row[colIdx - 1] == name:
            return idx + 1
    
    return len(rows) + 1

def getCell(colName, rowIdx, command, firstRow):
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    val = output.stdout.strip()
    
    colIdx = 0

    for i, col in enumerate(firstRow):
        if col == colName: colIdx = i + 1

    print(colName, val)
    
    return gspread.models.Cell(rowIdx, colIdx, val)
    


def main():
    serverName = subprocess.run('hostname -s', shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
    distro = subprocess.run('lsb_release -is', shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
    
    commands = [
        ('name', 'hostname -s'),
        ('uptime', 'uptime | cut -d, -f1'),
        ('kernelVer', 'uname -r'),
        ('arch', 'uname -m'),
        ('distro', 'lsb_release -is'),
        ('distroVer', 'lsb_release -rs'),
        ('openSSLVer', 'openssl version'),
        ('IP', 'hostname -i'),
        ('manufacturer', 'sudo dmidecode -s system-manufacturer'),
        ('BIOSVendor', 'sudo dmidecode -s bios-vendor'),
        ('BIOSVer', 'sudo dmidecode -s bios-version'),
        ('BIOSReleaseDate', 'sudo dmidecode -s bios-release-date'),
        ('serialNum', 'sudo dmidecode -s system-serial-number'),
        ('updateTime', 'date')
    ]

    if distro == 'Ubuntu':
        commands.append(('pendingRegularUpdates', "/usr/lib/update-notifier/apt-check 2>&1 | cut -d ';' -f 1"))
        commands.append(('pendingSecurityUpdates', "/usr/lib/update-notifier/apt-check 2>&1 | cut -d ';' -f 2"))
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.dirname(os.path.abspath(__file__)) + '/gspread-638cf9da7c8d.json', scope)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key("1XnS1Oz7eRfb38H30Ow1M3NHtXvjSmjpTv0ELbv9MXxA").sheet1
            
    rowIdx = getRowIdxByName(wks, serverName)

    print('Updating on Google Sheets...')

    firstRow = wks.row_values(1)
    cells = []
    for command in commands:
        c = getCell(command[0], rowIdx, command[1], firstRow)
        cells.append(c)
    
    wks.update_cells(cells)


if __name__ == "__main__":
    main()