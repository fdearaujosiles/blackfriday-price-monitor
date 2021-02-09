import pandas as pd
import numpy as np
import requests
from datetime import datetime
from time import sleep
import os
import re

url = "https://b2lq2jmc06.execute-api.us-east-1.amazonaws.com/PROD/ofertas?campanha=cybermonday&app=1&limite=999999&pagina=1"
cols = ['produto', 'quantidade', 'vlr_normal', 'data_ini', 'desconto', 'data_fim', 'vlr_oferta', 'codigo']
setores = { #&sec=
    "fonte": "fontes",
    "ram": "memoria-ram",
    "ssd": "ssd-2-5",
    "processador": "processadores",
    "vga": 'placa-de-video-vga',
    "monitor": "monitores"
}
marcas = { #&marcas=
    "amd": "5",
    "intel": "6",
    'xpg': '2430',
    "sandisk": '82',
    'kingston': '50',
    'adata': '171',
    'corsair': '36',
    'hyperx': '1135',
    'crucial': '1128',
    'aorus': '2350'
}

mbps = re.compile('([0-9])+([M|m][B|b]\/s)')
armz = re.compile('([0-9])+([G|g|T|t][B|b])')
mhz = re.compile('([0-9])+([M|m][H|h][Z|z])')
hz = re.compile('([0-9])+([H|h][Z|z])')

def toDate(d):
    return datetime.fromtimestamp(d).strftime('%d/%m/%Y %H:%M:%S')
def getMbps(d):
    r = mbps.search(d)
    return int(r.group(0)[:-4]) if r else 0
def getMhz(d):
    r = mhz.search(d)
    return int(r.group(0)[:-3]) if r else 0
def getArmz(d):
    r = armz.search(d)
    return int(r.group(0)[:-2]) if r else 0
def getHz(d):
    r = hz.search(d)
    return int(r.group(0)[:-2]) if r else 0

def getHead():
    req = requests.get(url + "&valor_min=50&valor_max=9999999").json()['produtos']
    df = pd.DataFrame(list(req))
    df = df[df['produto'].apply(lambda x: not any(a in x for a in ["Razer", "Kingston"]))]
    return df.sort_values('desconto', ascending=False).head(20)[cols]

def getProducts(setor="", marca=[], minDesc=0, findInName=[], minMbs=0, minArmz=0, minMhz=0, minHz=0, dep="hardware"):
    address = f'{url}&dep={dep}'
    address += f'&sec={setores[setor]}' if setor else ""
    address += f'&marcas={",".join(list(map(lambda x: marcas[x], marca)))}' if setor else ""
    
    req = requests.get(address).json()['produtos']
    df = pd.DataFrame(list(req))
    df["data_ini"] = df["data_ini"].apply(toDate)
    df["data_fim"] = df["data_fim"].apply(toDate)
    if len(findInName):
        df = df[df['produto'].apply(lambda x: any(a in x for a in findInName) )]
    if minMbs > 0:
        df = df[df['produto'].apply(lambda x: getMbps(x) >= minMbs) ]
    if minArmz > 0:
        df = df[df['produto'].apply(lambda x: getArmz(x) >= minArmz) ]
    if minMhz > 0:
        df = df[df['produto'].apply(lambda x: getMhz(x) >= minMhz) ]
    if minHz > 0:
        df = df[df['produto'].apply(lambda x: getHz(x) >= minHz) ]
    return df.loc[df["desconto"] >= minDesc ,cols].sort_values('desconto', ascending=False)

while True:
    rams = getProducts("ram", findInName=["D80"])
    ssds = getProducts("ssd", minDesc=15, minMbs=3000, minArmz=256)
    vgas = getProducts("vga", findInName=['GTX 1',"RX 580"])
    head = getHead()
    monitores = getProducts("monitor", dep="computadores", minHz=144)
    os.system('cls')
    print("\n########                 SSD                      ##########")
    print(ssds)
    print("\n########                 RAM                      ##########")
    print(rams)
    print("\n########                 MONITORES                ##########")
    print(monitores)
    print("\n########                 VGA                      ##########")
    print(vgas)
    print("\n########                 OUTROS                   ##########")
    print(head)