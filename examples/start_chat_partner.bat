set LANGUAGE=english
set SOUND_DEVICE=0
set ROBOT_NAME=stickman
set ROBOT_IP=127.0.0.1
set MOSQUITTO_IP=127.0.0.1
set PROJECT_FILE="%USERPROFILE%\.sobotify\projects\chat_partner.xlsx" 
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
CALL %CONDA% run -n sobotify --no-capture-output python "%~dp0\..\sobotify\apps\chat_partner\chat_partner.py" --mosquitto_ip %MOSQUITTO_IP% --robot_name=%ROBOT_NAME% --robot_ip=%ROBOT_IP% --sound_device %SOUND_DEVICE% --language %LANGUAGE% --project_file %PROJECT_FILE%
PAUSE