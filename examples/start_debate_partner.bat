set LANGUAGE=english
set SOUND_DEVICE=0
set KEYWORD="apple tree"
set ROBOT_NAME=stickman
set ROBOT_IP=127.0.0.1
set MOSQUITTO_IP=127.0.0.1
@ECHO OFF
REM ======================================================================================
REM find and set CONDA executable path
if EXIST "%USERPROFILE%\miniconda3\condabin\conda.bat" (
    set CONDA="%USERPROFILE%\miniconda3\condabin\conda.bat" 
) else if EXIST "%USERPROFILE%\AppData\Local\miniconda3\condabin\conda.bat" (
    set CONDA="%USERPROFILE%\AppData\Local\miniconda3\condabin\conda.bat" 
) else (
    echo cannot find CONDA environment. Installation aborted!
    pause
    exit
)
REM ======================================================================================
@ECHO ON
CALL %CONDA% run -n sobotify --no-capture-output python "%~dp0\..\examples\debate_partner.py" --mosquitto_ip %MOSQUITTO_IP% --robot_name=%ROBOT_NAME% --robot_ip=%ROBOT_IP% --sound_device %SOUND_DEVICE% --language %LANGUAGE% --keyword %KEYWORD%  
PAUSE