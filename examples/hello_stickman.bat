set LANGUAGE=english
set MESSAGE="Hello, I am stickman, a virtual robot. Press Q on your keyboard to end this demo"
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
CALL %CONDA% run -n sobotify --no-capture-output python "%~dp0\..\sobotify\tools\robotcontrol\robotcontrol.py" --robot_name stickman --language %LANGUAGE% --message %MESSAGE%
PAUSE