@ECHO OFF
set ROBOT_NAME=stickman
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
ECHO IMPORTANT: To exit this demo
ECHO            1. press Q on your keyboard in the activated camera window
ECHO            2. then close this window
CALL %CONDA% run -n sobotify --no-capture-output python "%~dp0\..\sobotify\sobotify.py" -f --robot_name=%ROBOT_NAME%
PAUSE