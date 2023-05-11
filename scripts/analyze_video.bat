set ROBOT_NAME=pepper
set LANGUAGE=english
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify python "%~dp0\..\sobotify\sobotify.py" -a --robot_name %ROBOT_NAME% --language %LANGUAGE% --video_file %1
PAUSE