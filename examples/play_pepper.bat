set ROBOT_IP=192.168.0.141
set ROBOT_NAME=pepper
set LANGUAGE=english
set MESSAGE="%~n1|Hello"
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify_naoqi --no-capture-output python "%~dp0\..\sobotify\robotcontrol\robotcontrol.py" --robot_name %ROBOT_NAME% --robot_ip %ROBOT_IP% --language %LANGUAGE% --message %MESSAGE%
PAUSE