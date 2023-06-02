set LANGUAGE=english
set SOUND_DEVICE=1
set ROBOT_NAME=stickman
set ROBOT_IP=192.168.0.141
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify --no-capture-output python "./quiz.py" --robot_name=%ROBOT_NAME% --robot_ip=%ROBOT_IP% --sound_device %SOUND_DEVICE% --language %LANGUAGE% --project_file "./quiz_english.xlsx"
PAUSE