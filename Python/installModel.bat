ECHO OFF
CLS
.\python.exe -m pip install --upgrade requests
.\python.exe -m pip install --upgrade py7zr
.\python.exe ..\pys\download.py https://github.com/dreamsavior/yojet-server/releases/download/sugoi-fairseq-3.3-model/sugoi-fairseq-3.3.7z ..\models\model.7z
ECHO Unpacking model... please wait...
CD ..\models\
..\Python\python.exe -m py7zr x model.7z
del model.7z /F /Q
ECHO model is ready
