ECHO OFF
robocopy .\ ..\yojet-server-git\ /MIR /XD E:\dreamsavior\yojet-server\models /XD E:\dreamsavior\yojet-server\tests /XD E:\dreamsavior\yojet-server\releases /XD E:\dreamsavior\yojet-server\.git 
robocopy .\models\sp_model E:\dreamsavior\yojet-server-git\models\sp_model /MIR
mkdir E:\dreamsavior\yojet-server-git\models\sp_model
CD E:\dreamsavior\yojet-server-git\
del *.xml
cd .\Python
call.\uninstall.bat
rmdir /S /Q .\Lib\site-packages\ctranslate2
cd ..
del .\db\cache.db
pause
