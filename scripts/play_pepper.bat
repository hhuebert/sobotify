set ROBOT_IP=192.168.0.141
set LANGUAGE=english
set MESSAGE="%~n1|Hello"
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify_naoqi python "%~dp0\..\sobotify\robotcontrol\robotcontrol.py" --robot_name pepper --robot_ip %ROBOT_IP% --language %LANGUAGE% --message %MESSAGE%