set ROBOT_IP=192.168.0.141
set ROBOT_NAME=pepper
set LANGUAGE=english
set MESSAGE="%~n1|Hello"
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
CALL %CONDA% run -n sobotify_naoqi --no-capture-output python "%~dp0\..\sobotify\robotcontrol\robotcontrol.py" --robot_name %ROBOT_NAME% --robot_ip %ROBOT_IP% --language %LANGUAGE% --message %MESSAGE%
PAUSE