ECHO OFF
robocopy .\ ..\yojet-server-build\ /MIR /XD E:\dreamsavior\yojet-server\models /XD E:\dreamsavior\yojet-server\.git /XD E:\dreamsavior\yojet-server\tests /XD E:\dreamsavior\yojet-server\releases /XD E:\dreamsavior\yojet-server\res
robocopy .\models\sp_model E:\dreamsavior\yojet-server-build\models\sp_model /MIR
mkdir E:\dreamsavior\yojet-server-build\models\sp_model
CD E:\dreamsavior\yojet-server-build\
del *.xml
cd .\Python
call.\uninstall.bat
rmdir /S /Q .\Lib\site-packages\ctranslate2
cd ..
del .\db\cache.db
del .\build.bat
del .\server.bat
pause
