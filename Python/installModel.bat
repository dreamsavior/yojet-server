ECHO OFF
CLS
.\python.exe -m pip install --upgrade requests
.\python.exe -m pip install --upgrade py7zr
.\python.exe ..\pys\download.py http://127.0.0.1/models/sugoi-fairseq-3.3.7z ..\models\model.7z
ECHO Unpacking model... please wait...
CD ..\models\
..\Python\python.exe -m py7zr x model.7z
del model.7z /F /Q
ECHO model is ready
