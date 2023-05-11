set LANGUAGE=english
set MOSQUITTO_IP=192.168.0.101
set SOUND_DEVICE=0
set VOSK_KEYWORD="apple tree"
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify python "%~dp0\..\sobotify\sobotify.py" -ml --mosquitto_ip %MOSQUITTO_IP% --sound_device %SOUND_DEVICE% --language %LANGUAGE% --vosk_keyword %VOSK_KEYWORD%  
PAUSE