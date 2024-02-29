REM ======================================================================================
REM                             sobotify installation script
REM Script for installing and setting up all required tools, models, SDKs and environments
REM ======================================================================================

REM ======================================================================================
REM download and install miniconda and mosquitto
set MINICONDA=Miniconda3-latest-Windows-x86_64.exe
set MOSQUITTO=mosquitto-2.0.15-install-windows-x64.exe 
CALL curl -O https://repo.anaconda.com/miniconda/%MINICONDA%
CALL curl -O https://mosquitto.org/files/binary/win64/%MOSQUITTO%
REM Instruction for silent installation of Miniconda https://docs.anaconda.com/free/anaconda/install/silent-mode/
CALL .\%MINICONDA% 
DEL  .\%MINICONDA% 
CALL .\%MOSQUITTO% 
DEL  .\%MOSQUITTO%
REM ======================================================================================

REM ======================================================================================
REM Download vosk models
set VOSK_EN=vosk-model-small-en-us-0.15
set VOSK_DE=vosk-model-small-de-0.15
  REM for larger models, use the following:
  REM set VOSK_EN=vosk-model-en-us-0.22
  REM set VOSK_DE=vosk-model-de-0.21
set VOSK_URL=https://alphacephei.com/vosk/models
set VOSK_PATH=%USERPROFILE%\.sobotify\vosk\models
mkdir "%VOSK_PATH%"
CALL :download %VOSK_URL% %VOSK_EN% "%VOSK_PATH%" english
CALL :download %VOSK_URL% %VOSK_DE% "%VOSK_PATH%" german
REM ======================================================================================


REM ======================================================================================
REM Download language tool
set LANGUAGE_TOOL=LanguageTool-6.3
set LANGUAGE_TOOL_URL=https://languagetool.org/download/
SET LANGUAGE_TOOL_PATH=%USERPROFILE%\.sobotify\
CALL :download %LANGUAGE_TOOL_URL% %LANGUAGE_TOOL% "%LANGUAGE_TOOL_PATH%" languagetool
REM ======================================================================================


REM ======================================================================================
REM Download FFMPEG
set FFMPEG=ffmpeg-master-latest-win64-lgpl-shared
set FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest
set FFMPEG_PATH=%USERPROFILE%\.sobotify\
CALL :download %FFMPEG_URL% %FFMPEG% "%FFMPEG_PATH%" ffmpeg
REM ======================================================================================

REM ======================================================================================
REM find and set CONDA executable path
if EXIST "%USERPROFILE%\miniconda3\condabin\conda.bat" (
    set CONDA_BASE=%USERPROFILE%\miniconda3
) else if EXIST "%USERPROFILE%\AppData\Local\miniconda3\condabin\conda.bat" (
    set CONDA_BASE=%USERPROFILE%\AppData\Local\miniconda3
) else (
    echo cannot find CONDA environment. Installation aborted!
    pause
    exit
)
set CONDA="%CONDA_BASE%\condabin\conda.bat"
REM ======================================================================================

REM ======================================================================================
REM Create python environment for sobotify
set CONDA_ENV=sobotify
CALL %CONDA% create -y -n %CONDA_ENV% python=3.8 
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% conda install -c conda-forge --yes pybullet
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% pip install -r "%~dp0\requirements.txt"
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% pip install -e "%~dp0."
REM ======================================================================================


REM ======================================================================================
REM Download NAOQI
set NAOQI=pynaoqi-python2.7-2.8.6.23-win64-vs2015-20191127_152649
set NAOQI_URL=https://community-static.aldebaran.com/resources/2.8.6
set NAOQI_PATH=%USERPROFILE%\.sobotify\
CALL :download %NAOQI_URL% %NAOQI% "%NAOQI_PATH%" pynaoqi
REM ======================================================================================


REM ======================================================================================
REM Create python environment for naoqi
set CONDA_ENV_NAOQI=sobotify_naoqi
CALL %CONDA% create -y -n %CONDA_ENV_NAOQI% python=2.7 
CALL %CONDA% run --no-capture-output -n %CONDA_ENV_NAOQI% pip install -r "%~dp0\requirements.txt"
CALL %CONDA% run --no-capture-output -n %CONDA_ENV_NAOQI% pip install -e "%~dp0."
CALL %CONDA% run --no-capture-output -n %CONDA_ENV_NAOQI% conda env config vars set PYTHONPATH="%NAOQI_PATH%\pynaoqi\lib"
REM ======================================================================================


REM ======================================================================================
REM Get animations for cozmo robot
set CONDA_ENV=sobotify
CALL %CONDA% run --no-capture-output -n %CONDA_ENV% python "%CONDA_BASE%\envs\%CONDA_ENV%\Scripts\pycozmo_resources.py" download
REM ======================================================================================


REM ======================================================================================
REM Create directories and copy default project data
set SOBOTIFY_DATA_PATH=%USERPROFILE%\.sobotify\data
mkdir "%SOBOTIFY_DATA_PATH%"
mkdir "%SOBOTIFY_DATA_PATH%\trash"
set SOBOTIFY_PROJECT_PATH=%USERPROFILE%\.sobotify\projects
mkdir "%SOBOTIFY_PROJECT_PATH%"
mkdir "%SOBOTIFY_PROJECT_PATH%\trash"
copy "%~dp0\sobotify\apps\quiz\quiz_english.xlsx" "%SOBOTIFY_PROJECT_PATH%"
copy "%~dp0\sobotify\apps\quiz\quiz_german.xlsx" "%SOBOTIFY_PROJECT_PATH%"
copy "%~dp0\sobotify\apps\chat_partner\chat_partner.xlsx" "%SOBOTIFY_PROJECT_PATH%"
copy "%~dp0\sobotify\apps\dialog_training\dialog_training.xlsx" "%SOBOTIFY_PROJECT_PATH%"
set SOBOTIFY_FACE_DB_PATH=%USERPROFILE%\.sobotify\face_db
mkdir "%SOBOTIFY_FACE_DB_PATH%"

REM ======================================================================================

pause

exit

REM ======================================================================================
REM function to download, extract and copy to sobotify config directory (HOME/.sobotify) 
:download
CALL curl -L -O  %~1/%~2.zip
TIMEOUT /T 3 /NOBREAK
powershell Expand-Archive -Path %~2.zip -DestinationPath '%~3'
move  "%~3\%~2" "%~3\%~4"
DEL %~2.zip
EXIT /B
REM ======================================================================================


