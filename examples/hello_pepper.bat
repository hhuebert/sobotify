set ROBOT_IP=192.168.0.141
set ROBOT_NAME=pepper
set LANGUAGE=english
set MESSAGE="Hello, I am Pepper, your robot"
@ECHO OFF
REM ======================================================================================
REM find and set CONDA executable path
if EXIST "%USERPROFILE%\miniforge3\condabin\conda.bat" (
    set CONDA="%USERPROFILE%\miniforge3\condabin\conda.bat" 
) else if EXIST "%USERPROFILE%\AppData\Local\miniforge3\condabin\conda.bat" (
    set CONDA="%USERPROFILE%\AppData\Local\miniforge3\condabin\conda.bat" 
) else (
    echo cannot find CONDA environment. Installation aborted!
    pause
    exit
)
REM ======================================================================================
@ECHO ON
CALL %CONDA% run -n sobotify_naoqi --no-capture-output python "%~dp0\..\sobotify\tools\robotcontrol\robotcontrol.py" --robot_name %ROBOT_NAME% --robot_ip %ROBOT_IP% --language %LANGUAGE% --message %MESSAGE%
PAUSE