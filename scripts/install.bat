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
REM Download FFMPEG
set FFMPEG=ffmpeg-master-latest-win64-lgpl-shared
set FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest
set FFMPEG_PATH=%USERPROFILE%\.sobotify\
CALL :download %FFMPEG_URL% %FFMPEG% "%FFMPEG_PATH%" ffmpeg
REM ======================================================================================


REM ======================================================================================
REM Create python environment for sobotify
set CONDA="%USERPROFILE%\miniconda3\condabin\conda.bat" 
set CONDA_ENV=sobotify
CALL %CONDA% create -y -n %CONDA_ENV% python=3.8 
CALL %CONDA% config --add channels conda-forge
CALL %CONDA% run -n %CONDA_ENV% conda install pybullet
CALL %CONDA% run -n %CONDA_ENV% pip install -e "%~dp0\.." -r "%~dp0\..\requirements.txt"
CALL %CONDA% run -n %CONDA_ENV% pip install protobuf==3.20.1 --force-reinstall
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
set CONDA="%USERPROFILE%\miniconda3\condabin\conda.bat" 
set CONDA_ENV_NAOQI=sobotify_naoqi
CALL %CONDA% create -y -n %CONDA_ENV_NAOQI% python=2.7 
CALL %CONDA% run -n %CONDA_ENV_NAOQI% pip install -e "%~dp0\.." -r "%~dp0\..\requirements.txt"
CALL %CONDA% run -n %CONDA_ENV_NAOQI% conda env config vars set PYTHONPATH="%NAOQI_PATH%\pynaoqi\lib"
REM ======================================================================================


REM ======================================================================================
REM Create data directory
set SOBOTIFY_DATA_PATH=%USERPROFILE%\.sobotify\data
mkdir "%SOBOTIFY_DATA_PATH%"
REM ======================================================================================

pause


REM ======================================================================================
REM function to download, extract and copy to sobotify config directory (HOME/.sobotify) 
:download
CALL curl -L -O  %~1/%~2.zip
powershell Expand-Archive -Path %~2.zip -DestinationPath '%~3'
move  "%~3\%~2" "%~3\%~4"
DEL %~2.zip
EXIT /B
REM ======================================================================================


