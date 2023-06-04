# sobotify
## sobotify: turn your robot into a SOcial roBOT

sobotify is a framework for turning a robot into a social robot. 
Currently it supports controlling the Pepper robot and a virtual "robot" (stickman). It is planned to support further robots (NAO, Cozmo, MyKeepon, ...).
 
It has been tested with Python 3.8 on Windows. Future versions should also support Linux.

# Known Issues/Restrictions
* NAO support not fully tested yet
* Issues with NAO and Pepper simulators (very slow execution)
* Chatbot (LLM - Large Language Model) code is only a dummy
* Currently usage of Miniconda3 is required (usage is hard coded within sobotify)
* Usage of non-ASCII characters (such as German umlauts) in diretory or file names will (likely) cause issues 

# Quick Start

## Easy Install

* Download the current version of sobotify here : https://github.com/hhuebert/sobotify/archive/refs/heads/main.zip

* Unzip the sobotify-main.zip file 
* Copy the unpacked sobotify-main folder to a permanent location (i.e. where it can stay, as this will be the installation folder), for example copy it to your home directory, such as C:\Users\MyName\sobotify-main
* go into the sobotify top folder (sobotify-main\sobotify)
* double click the file 

      install.bat

   to automatically download and install all required tools and packages. It downloads several other project and tools (Miniconda, Mosquitto, VOSK, FFMPEG, pybullet, qibullet, Python SDK for Pepper/NAO (pynaoqi),...).   
   Please check their licenses before installation and usage. You can find the corresponding download URLs in [install.bat](install.bat) and Python package (PyPi) names in [requirements.txt](requirements.txt). pybullet is downloaded from the conda package repository (conda-forge)
* Keep the default settings within Miniconda and Mosquitto installation

## One-Click-Testing

Double-click the batch file 
start_app.bat to start an app.

* For starting a predefined app (e.g. the quiz app) **double-clicking** the following file to start the GUI:      

      start_app.bat

* For extracting gestures and speech from a video file **double-clicking** the following file to start the GUI: 
  (Important: you always need a speech with the gesture, otherwise the gestures will not be replayed)

      examples\start_gesture.bat

* Start the example app "debate partner" by **double-clicking** the following batch file :
(You might want to adjust the robot name, robot IP address, the keyword, language or sound device in the batch file beforehand. IMPORTANT: after usage, CLOSE all command windows, that have been opened by the script.)

      start_debate_partner.bat  

## Manual Installation

Instead of using the install.bat script for installation as described above, you can perform a manual installation.

### Sobotify-Settings-Folder
Create a directory .sobotify\data\ in your home directory, e.g. C:\Users\MyName\.sobotify\data 
In this folder sobotify will store all motion and speech data by default.

### Vosk
For speech recognition sobotify uses Vosk. Depending on the language you want to use, you have to download the apporiate language model. 
* Create at first a directory in your %USERPROFILE%\.sobotify\vosk\models to store the models 
* Download models from https://alphacephei.com/vosk/models, 
* unpack them, rename the folder to e.g. "english or "german"
* copy them to folders to the directory %USERPROFILE%\.sobotify\vosk\models
(e.g. the README file of the english model can then be found at %USERPROFILE%\.sobotify\vosk\models\english\README)
If you copy them to a different location, then provide the path to sobotify with the option vosk_model_path (e.g. --vosk_model_path %userprofile%\Downloads\vosks\models)

### Mosquitto
The different tools within sobotify communicate via mqtt, a messaging protocol. For this you need a broker, which distributes the messages to all tools. Mosquitto can be used for this purpose. 
* Download mosquitto from here and install https://mosquitto.org/download/

By default sobotify expects mosquitto to be installed at C:\Program Files\mosquitto\mosquitto.exe. If you install to a different location, you can provide the path to the mosquitto directory with the option --mosquitto_path  (e.g. --mosquitto_path "C:\Program Files\mosquitto\")

### FFMPEG
sobotify uses ffmpeg tools to extract information (e.g. time stamps and audio data) from the video files.
* Download ffmpeg tools ("essentials" are sufficient) from here https://ffmpeg.org/download.html
* unpack the directory
* rename it to ffmpeg
* copy it %USERPROFILE%\.sobotify (ffmpeg.exe can then be found at %USERPROFILE%\.sobotify\ffmpeg\bin\ffmpeg.exe).

If you copy it to a different location, then provide the path to "bin" sub directory to sobotify with the option --ffmpeg_path (e.g. --ffmpeg_path %userprofile%\Downloads\ffmpeg-essentials_build\bin)

### Set of Python environment 

The following instruction are based on using Conda to set up the two different Python versions required for the Sobotify main part (Python 3.8) and for the Pepper robot (Python 2.7)
* Get and install for example miniconda https://docs.conda.io/en/latest/miniconda.html
However, you can also use regular Python installation instead of Conda, as sobotify is not dependent on any other Conda packages (everything requried can be installe with pip) 

#### Python 3.8 environment
Create a Python 3.8 environment for most of the sobotify tools:
* open anaconda prompt and type the following commands: 

      conda create -y -n sobotify python=3.8
      conda activate sobotify
      conda config --add channels conda-forge
      conda install pybullet
      cd to sobotify folder (where README.md is)
      pip install -e . -r requirements.txt

#### Python 2.7 environment (Pepper and Nao)
Create a Python 2.7 envirnoment including the Python SDK (pynaoqi) and a if you want to use Pepper and Nao robots:

* download the Pepper Python SDK under "Old: Pepper SDK": https://www.aldebaran.com/en/support (pynaoqi 2.5.x for Python 2.7)
* unpack the ZIP file, e.g. to %HOME%\.sobotify\pynaoqi (or different location, then adjust also path in conda env below)
  (e.g. the naoqi.py can then be found at %USERPROFILE%\.sobotify\pynaoqi\lib\naoqi.py)

* open anaconda prompt and type the following commands: 

       conda create -y -n sobotify_naoqi python=2.7
       conda activate sobotify_naoqi
       cd to sobotify folder (where README.md is)
       pip install -e . -r requirements.txt
       conda env config vars set PYTHONPATH=%USERPROFILE%\.sobotify\pynaoqi
    
## Commandline Testing

For commandline testing you need to open a miniconda prompt. Then you can use the following commands. Before using the actual sobotify commands, you need to activate the sobotify enviroment (as can be seen below)

### "Hello World" on robots

For testing "Hello world" with the stickman use : 

    conda activate sobotify
    python sobotify\sobotify.py -r

For testing Hello World with pepper:

    conda activate sobotify_naoqi
    python .\sobotify\robotcontrol\robotcontrol.py --robot_name pepper --robot_ip 192.168.0.141

### Running the debate partner app
  For starting the debate parnter app with default settings (english with keyword "apple tree" and the "stickman" robot) use  

    conda activate sobotify
    python examples\debate_partner.py

or for running on the Pepper robot at 192.168.0.141 in german language with the keyword "Banane" 

    conda activate sobotify
    python examples\debate_partner.py --language="german" --keyword="Banane" --robot_name pepper --robot_ip 192.168.0.141

### Extracting gesture and speech from a video file
  For converting a video to robot control file (movement and speech) use  

    conda activate sobotify
    python sobotify\sobotify.py -e --video_file MyTest1.mp4 --language english --robot_name pepper 

  or

    conda activate sobotify
    python sobotify\tools\extract\extract.py --video_file MyTest1.mp4 --language english --robot_name pepper 

This will create the robot control files in the  in the data base (by default: %USERPROFILE%\.sobotify\data\):
* MyTest1.srt ==> spoken words with timing information (for robot speech)
* MyTest1_lmarks.csv ==> landmarks for controlling the stickman
* MyTest1_pepper.csv ==> joint angles for controlling peppers joints (movement) 
* MyTest1_wlmarks.csv ==> world landmarks (internal data) 
* MyTest1.tsp ==> time stamps (internal data)

### Running the extracted gesture/speech on the robot
For running  the previously extracted gesture/speech from the video MyTest1 with the stickman use : 

    conda activate sobotify
    python sobotify\sobotify.py -r --robot_name stickman --language english --message "MyTest1|Hello" 

or     

    conda activate sobotify
    python sobotify\robotcontrol\robotcontrol.py --robot_name stickman --language english --message "MyTest1|Hello"

## License:
Sobotify itself is licensed under MIT license. However, some part of the code are taken from other project which are under other licenses (e.g. Apache License). The license is then stated in the code. 
Additionally, sobotify uses several packages (see [requirements.txt](requirements.txt)), please check there license and terms of use before using sobotify.

## Credits: 
Part of sobotify include and are based on others code, especially from Fraporta (https://github.com/FraPorta/pepper_openpose_teleoperation) and also elggem (https://github.com/elggem/naoqi-pose-retargeting), which also uses code from Kazuhito00 (https://github.com/Kazuhito00/mediapipe-python-sample). 

Additionally several members of the Science Of Intelligence research project contributed to this project, whom I would like to thank. 

And special thanks go to Haeseon Yun for her inspiring inputs and fruitful discussions in creating and applying these tools (https://www.scienceofintelligence.de/research/researchprojects/project_06/) 
