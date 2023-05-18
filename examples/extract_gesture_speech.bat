set ROBOT_NAME=pepper
set LANGUAGE=english
CALL "%USERPROFILE%\miniconda3\condabin\conda.bat" run -n sobotify --no-capture-output python "%~dp0\..\sobotify\sobotify.py" -e --robot_name %ROBOT_NAME% --language %LANGUAGE% --video_file %1
PAUSE