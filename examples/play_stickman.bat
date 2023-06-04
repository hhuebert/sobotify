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
CALL %CONDA% run -n sobotify --no-capture-output python "%~dp0\..\sobotify\robotcontrol\robotcontrol.py" --robot_name stickman --language %LANGUAGE% --message %MESSAGE%
PAUSE