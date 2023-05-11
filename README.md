# sobotify
## sobotify: a framework for turning a robot into a SOcial roBOT

sobotify is a projects, that aims to become a framework for turning a robot into a social robot. 
Currently it supports controlling the Pepper robot and a virtual "robot" (stickman). It is planned to support further robots (NAO, Cozmo, MyKeepon, ...).
 
It has been tested with Python 3.8 on Windows. Future versions should also support Linux.

# Known Issues
* NAO support not fully tested yet
* Issues with NAO and Pepper simulators (very slow execution)
* LLM (Large Language Model) code only dummy

# Installation

## "One-Click"-Installer
You can use the 

[install.bat](scripts/install.bat) 

file in the script folder to automatically download and install all required tools and packages. It downloads several other project and tools (VOSK, FFMPEG, Mosquitto, miniconda, qibullet, Python SDK for Pepper/NAO (pynaoqi),...). 

Please check their licenses before installation and usage. You can find the corresponding download URLs in [install.bat](scripts/install.bat) and package names in [requirements.txt](requirements.txt) 

## Manuall Installation

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

    `conda create -y -n sobotify python=3.8` 

    `conda activate sobotify`

    `conda config --add channels conda-forge`

    `conda install pybullet`

    `cd to sobotify folder (where README.md is)` 

    `pip install -e . -r requirements.txt`

#### Python 2.7 environment (Pepper and Nao)
Create a Python 2.7 envirnoment including the Python SDK (pynaoqi) and a if you want to use Pepper and Nao robots:

* download the Pepper Python SDK under "Old: Pepper SDK": https://www.aldebaran.com/en/support (pynaoqi 2.5.x for Python 2.7)
* unpack the ZIP file, e.g. to %HOME%\.sobotify\pynaoqi (or different location, then adjust also path in conda env below)
  (e.g. the naoqi.py can then be found at %USERPROFILE%\.sobotify\pynaoqi\lib\naoqi.py)

* open anaconda prompt and type the following commands: 

    `conda create -y -n sobotify_naoqi python=2.7`

    `conda activate sobotify_naoqi`
    
    `cd to sobotify folder (where README.md is)`
    
    `pip install -e . -r requirements.txt`
    
    `conda env config vars set PYTHONPATH=%USERPROFILE%\.sobotify\pynaoqi`
    
# Testing

## One-Click-Testing

The batch files in the [scripts](scripts/) folder can be used to test the tools easily.

Drop a video file on [analyze_video.bat](scripts/analyze_video.bat) to create the robot control files

Drop a video file on [play_pepper.bat](scripts/play_pepper.bat) to play the previously analyzed robot control files (wiht the same name) on Pepper

Drop a video file on [play_stickman.bat](scripts/play_pepper.bat) to play the previously analyzed robot control files (wiht the same name) on the stickman

click on [start_debate_partner.bat](scripts/start_debate_partner.bat) to start the debate partner scenario.


## Commandline Testing
### Converting a video
  For converting a video to robot control file (movement and speech) use  

    conda activate sobotify
    python sobotify\sobotify.py -a --video_file MyTest1.mp4 --language english --robot_name pepper

  or

    conda activate sobotify
    python sobotify\tools\analyze\analyze.py --video_file MyTest1.mp4 --language english --robot_name pepper 

This will create the robot control files in the  in the data base (by default: %USERPROFILE%\.sobotify\data\):
* MyTest1.srt ==> spoken words with timing information (for robot speech)
* MyTest1_lmarks.csv ==> landmarks for controlling the stickman
* MyTest1_pepper.csv ==> joint angles for controlling peppers joints (movement) 
* MyTest1_wlmarks.csv ==> world landmarks (internal data) 
* MyTest1.tsp ==> time stamps (internal data)

### Control the "stickman"
For running  "Hello world" with the stickman use : 

    conda activate sobotify
    python sobotify\sobotify.py -r --robot_name stickman --language english --message "MyTest1|Hello" 

or     

    conda activate sobotify
    python sobotify\robotcontrol\robotcontrol.py --robot_name stickman --language english --message "MyTest1|Hello"

For testing "Hello world" with the stickman use : 

    conda activate sobotify
    python sobotify\sobotify.py -r

For testing the debate partner with stickman:

    conda activate sobotify
    python sobotify\sobotify.py -mrvl


### Control the pepper robot
For testing the debate partner with pepper (when llm processor is runnung on a different PC):

on your PC (for example with IP address 192.168.0.101) run:

    conda activate sobotify
    python ./sobotify/sobotify.py -mrv --robot_name pepper --mosquitto_ip 192.168.0.101

on llm-processor PC run:

either 

    conda activate sobotify
    python ./sobotify/sobotify.py -ml --mosquitto_ip 192.168.0.101

or 

     conda activate sobotify
     python ./sobotify/tools/llm_processor.py --mosquitto_ip 192.168.0.101

For testing Hello World with pepper:

    conda activate sobotify_naoqi
    python .\sobotify\robotcontrol\robotcontrol.py --robot_name pepper --robot_ip 192.168.0.141

For testing the debate partner with pepper:
    
    conda activate sobotify
    python ./sobotify/sobotify.py -mrlv --robot_name pepper --robot_ip 192.168.0.141

## License:
Sobotify itself is licensed under MIT license. However, some part of the code are taken from other project which are under other licenses (e.g. Apache License). The license is then stated in the code. 
Additionally, sobotify uses several packages (see [requirements.txt](requirements.txt)), please check there license and terms of use before using sobotify.

## Credits: 
Part of sobotify include and are based on others code, especially from Fraporta (https://github.com/FraPorta/pepper_openpose_teleoperation) and also elggem (https://github.com/elggem/naoqi-pose-retargeting), which also uses code from Kazuhito00 (https://github.com/Kazuhito00/mediapipe-python-sample). 

Additionally several members of the Science Of Intelligence research project contributed to this project, whom I would like to thank. And special thanks go to Haeseon Yun for her inspiring inputs and and discussions in creating and applying these tools (https://www.scienceofintelligence.de/research/researchprojects/project_06/) 
