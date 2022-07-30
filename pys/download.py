import requests
from tqdm import tqdm
import getopt, sys, os, signal
from os.path import abspath


#===========================================================
# HANDLING ARGUMENTS
#===========================================================
# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

saveTo = abspath(argumentList[1])
print("Downloading:", argumentList[0])
print("To: ", saveTo)

def download(url: str, fname: str):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
            desc=fname,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

if __name__ == "__main__":
    download(argumentList[0], saveTo)