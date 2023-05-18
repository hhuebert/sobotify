set LANGUAGE=english
set SOUND_DEVICE=0
set KEYWORD="apple tree"
set ROBOT_NAME=stickman
set ROBOT_IP=127.0.0.1
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify --no-capture-output python "%~dp0\..\scripts\debate_partner.py" --robot_name=%ROBOT_NAME% --robot_ip=%ROBOT_IP% --sound_device %SOUND_DEVICE% --language %LANGUAGE% --keyword %KEYWORD%  
PAUSE