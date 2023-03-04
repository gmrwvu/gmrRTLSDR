REM This command file configures Travis Painter's dump1090.exe software
REM See https://github.com/tpainter/dump1090_win for downloading a copy of dump1090.exe
REM Installing the program will also install 
REM rtlsdr.dll
REM winposixclock.dll
REM pthreadVC2.dll
REM additionally you will need to have purchased and installed an rtlsdr dongle on your PC

dump1090.exe --interactive --oversample --net --phase-enhance  --net-ro-port 30002 --net-beast --device-index 1 --aggressive --fix   --debug D
pause
