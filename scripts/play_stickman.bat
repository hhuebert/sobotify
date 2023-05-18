set LANGUAGE=english
set MESSAGE="%~n1|Hello"
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify --no-capture-output python "%~dp0\..\sobotify\robotcontrol\robotcontrol.py" --robot_name stickman --language %LANGUAGE% --message %MESSAGE%
PAUSE