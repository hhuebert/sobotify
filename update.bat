REM ======================================================================================
REM                             sobotify update script
REM       Script for updating the environments of an existing installation
REM ======================================================================================


REM ======================================================================================
REM find and set CONDA executable path
if EXIST "%USERPROFILE%\miniforge3\condabin\conda.bat" (
    set CONDA_BASE=%USERPROFILE%\miniforge3
) else if EXIST "%USERPROFILE%\AppData\Local\miniforge3\condabin\conda.bat" (
    set CONDA_BASE=%USERPROFILE%\AppData\Local\miniforge3
) else (
    echo cannot find CONDA environment. Installation aborted!
    pause
    exit
)
set CONDA="%CONDA_BASE%\condabin\conda.bat"
REM ======================================================================================


REM ======================================================================================
REM Update python environment for sobotify
set CONDA_ENV=sobotify
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% pip install -r "%~dp0\requirements.txt"
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% pip install -e "%~dp0."
REM ======================================================================================


REM ======================================================================================
REM Update python environment for naoqi
set CONDA_ENV_NAOQI=sobotify_naoqi
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% pip install -r "%~dp0\requirements.txt"
CALL %CONDA% run --no-capture-output -n %CONDA_ENV_NAOQI% pip install -e "%~dp0."
REM ======================================================================================


REM ======================================================================================
REM Get animations for cozmo robot
set CONDA_ENV=sobotify
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% python "%CONDA_BASE%\envs\%CONDA_ENV%\Scripts\pycozmo_resources.py" download
REM ======================================================================================

pause
