set LANGUAGE=english
set SOUND_DEVICE=1
set ROBOT_NAME=stickman
set ROBOT_IP=192.168.0.141
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
CALL %CONDA% run -n sobotify --no-capture-output python "./simple_mqtt.py" --robot_name=%ROBOT_NAME% --robot_ip=%ROBOT_IP% --sound_device %SOUND_DEVICE% 
PAUSE