ECHO OFF
CLS
set arg=%1
if [%1] equ [] (
	set arg=https://github.com/dreamsavior/yojet-server/releases/download/sugoi-fairseq-3.3-model/sugoi-fairseq-levi.7z
) 


.\python.exe ..\pys\download.py %arg% ..\models\model.7z
ECHO Unpacking model... please wait...
CD ..\models\
..\Python\python.exe -m py7zr x model.7z
del model.7z /F /Q
ECHO model is ready

:end
ECHO model installation completed

pause
