#!/usr/bin/env python3

# code mainly taken from: https://github.com/alphacep/vosk-api/blob/master/python/example/test_srt.py

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import subprocess
import srt
import json
import datetime
import argparse



def replace_umlaute(text) :
    text = text.replace("ä","ae")
    text = text.replace("ö","oe")
    text = text.replace("ü","ue")
    text = text.replace("Ä","Ae")
    text = text.replace("Ö","oe")
    text = text.replace("Ü","ue")
    text = text.replace("ß","ss")
    return text


def transcribe(rec,process,WORDS_PER_LINE):
    results = []
    subs = []
    while True:
       data = process.stdout.read(4000)
       if len(data) == 0:
           break
       if rec.AcceptWaveform(data):
           results.append(rec.Result())
           print("processed one package ...")
    results.append(rec.FinalResult())
    print(rec.FinalResult())

    for i, res in enumerate(results):
       jres = json.loads(res)
       if not 'result' in jres:
           continue
       words = jres['result']
       for j in range(0, len(words), WORDS_PER_LINE):
           line = words[j : j + WORDS_PER_LINE] 
           text1 =" ".join([l['word'] for l in line])
           text2 = replace_umlaute(text1)
           s = srt.Subtitle(index=len(subs), 
                   content=text2,
                   start=datetime.timedelta(seconds=line[0]['start']), 
                   end=datetime.timedelta(seconds=line[-1]['end']))
           subs.append(s)
    return subs


def audio2srt(video_file,data_path,ffmpeg_path, model_path,language) :

    ffmpeg_full_path=os.path.join(ffmpeg_path,"ffmpeg")
    
    SetLogLevel(-1)

    # load vosk model
    full_model_path=os.path.join(model_path,language)
    if not os.path.exists(full_model_path):
        print ("cannot find model at "+full_model_path);
        print ("Please download the model from https://alphacephei.com/vosk/models, unpack it, rename it to \""+language+"\" and copy it to folder "+model_path)
        exit (1)
    print('loading vosk model: ',full_model_path)
    print("please be patient ...")
    SetLogLevel(-1)
    try:
        model = Model(full_model_path)
    except Exception:
        print ("error loading the model: ",Exception)
        print ("maybe memory limit reached ==> choose a smaller vosk model")
        exit(1)

    print("input  file   : " + video_file)
    fileName, ext = os.path.splitext(os.path.basename(video_file))

    srt_full_path= os.path.join(data_path,fileName+'.srt')
    print("output file   : " + srt_full_path)
    srtFile= open(srt_full_path, "w");

    sample_rate=16000

    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    process = subprocess.Popen([ffmpeg_full_path, '-i',video_file,
                                '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                stdout=subprocess.PIPE)


    WORDS_PER_LINE = 10

    srtString = srt.compose(transcribe(rec,process,WORDS_PER_LINE))

    print(srtString)
    srtFile.write(srtString)
    srtFile.close()

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='extract text from audio in a audio/video file and store it as srt file')
    parser.add_argument('--video_file',default='video.mp4',help='path to the video input file')
    parser.add_argument('--vosk_model_path',default=os.path.join(os.path.expanduser("~"),".sobotify","vosk","models"),help='path to vosk_model')
    parser.add_argument('--language',default="english",help='choose language (english,german)')
    parser.add_argument('--ffmpeg_path',default=os.path.join(os.path.expanduser("~"),".sobotify","ffmpeg","bin"),help='directory path to ffmpeg tools (bin directory)')
    parser.add_argument('--data_path',default=os.path.expanduser("~")+"/.sobotify/data",help='path to movement/speech data')
    args=parser.parse_args()
    audio2srt(args.video_file,args.data_path,args.ffmpeg_path,args.vosk_model_path,args.language)