#Michelle Morales
#Dissertation Work 2017

#This script can be used to perform AV (audiovisual) feature extraction using the OpenFace and COVAREP repos

### OpenFace ###
#Feature extraction with OpenFace
#ToDo
#function that takes video as input
#creates new csv for output
#runs feature extraction: OpenFace/bin/FeatureExtraction -f /path/to/mov -of /path/to/.csv

#Extract audio (wav) from video - ffmpeg -i Example.mov -vn -acodec pcm_s16le -ar 44100 -ac 2 Example.wav

### COVAREP ###
#Feature extraction with covarep
#ToDo
#figure out how to call matlab functions in python
#function that takes audio as input and creates csv and writes features to
#covarep/feature_extraction/COVAREP_feature_extraction.m
#/Applications/MATLAB_R2016a.app/bin/matlab -nodisplay -nosplash -nodesktop -r "COVAREP_feature_extraction('/Users/morales/Desktop/');exit"

### Dependencies ###
# OpenFace
# ffmpeg
# Matlab

import sys, os, subprocess,json, LingAnalysis, LingAnalysis_NonEnglish, pandas, scipy.stats, os.path, glob
import speech_recognition as sr
import numpy as np


def extract_visual(video, openface):
    #Extracts visual features using OpenFace, requires the OpenFace () repo to be installed
    pathOpenFace =''
    csv = video.replace('.mp4','_openface.csv')
    newF = open(csv,'w')
    print 'Launching OpenFace to extract visual features... \n\n\n\n\n'
    command = '%s -f %s -of %s'%(openface, video, csv)
    subprocess.call(command, shell=True)
    print 'DONE! Visual features saved to %s' %csv


def video2audio(video):
    # Converts video to audio using ffmpeg, requires ffmpeg to be installed
    wav = video.replace('.mp4', '.wav')
    command = 'ffmpeg -i %s -acodec pcm_s16le -ac 1 -ar 16000 %s'%(video, wav)
    subprocess.call(command, shell=True)
    print 'DONE! Video converted to audio file: %s' % wav


def extract_audio(audio_dir, matlab):
    # Covarep operates on directory of files
    # Extracts audio features using matlab app
    matlab = '/Applications/MATLAB/MATLAB_Runtime/v92/'
    # command = '/Applications/MATLAB_R2016a.app/bin/matlab -nodisplay -nosplash -nodesktop -r '+ '"COVAREP_feature_extraction(%s);exit"'%("'"+audio_dir+"'")
    command = "./covarep/run_COVAREP_feature_extraction.sh '%s' '%s'" % (matlab, audio_dir)
    print command
    subprocess.call(command, shell=True)
    print 'DONE! Audio features saved to .mat file in %s directory.' % audio_dir


def google_speech2text(audio_file,lang):
    GOOGLE_SPEECH_RECOGNITION_API_KEY = 'AIzaSyCQNG-Jeageo_myq7MJTBzoxAdSq8oqASc'
    json_name = audio_file.replace(".wav","_transcript.json")
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    #Recognize speech using Google Speech Recognition
    try:
        result = r.recognize_google(audio, key=GOOGLE_SPEECH_RECOGNITION_API_KEY, language=lang)
        new_f = open(json_name,"w") #create a file to write json object to
        json.dump(result, new_f)
        new_f.close()
        print("Audio file processed transcript saved json file!")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def speech2text(audio_file, lang, IBM_USERNAME, IBM_PASSWORD):
    # IBM_USERNAME = "28e8d133-29a7-477e-9544-d3ac977218ab"
    # IBM_PASSWORD = "JPyxiE3a4ADK"
    json_name = audio_file.replace(".wav", "_transcript.json")
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    # Recognize speech using IBM Speech to Text
    try:
        result = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD, language=lang,
                                 show_all=True, timestamps=True)
        # Create a file to write json object to
        new_f = open(json_name, "w")
        json.dump(result, new_f)
        new_f.close()
        print("Audio file processed transcript saved json file!")

    except sr.UnknownValueError:
        print("IBM Speech to Text could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from IBM Speech to Text service; {0}".format(e))

def combine_modes(file_name):
    print file_name
    visualF = file_name.replace('_transcript.json','_openface.csv')
    audioF = file_name.replace('_transcript.json','_covarep.csv')
    lingF = file_name.replace('_transcript.json','_ling.csv')
    mmF = file_name.replace('_transcript.json','_multimodal.csv')
    print visualF, audioF, lingF, '\n\n'
    files = [visualF,audioF,lingF]
    stats_names = ['max','min','mean','median','std','var','kurt','skew','percentile25','percentile50','percentile75']
    mm_feats = []
    mm_names = []
    for f in files:
        df = pandas.read_csv(f,header='infer')
        feature_names = df.columns.values
        for f in feature_names:
            vals = df[f].values #Feature vector
            #Run statistics
            maximum = np.nanmax(vals)
            minimum = np.nanmin(vals)
            mean = np.nanmean(vals)
            median = np.nanmedian(vals)
            std = np.nanstd(vals)
            var = np.nanvar(vals)
            kurt = scipy.stats.kurtosis(vals)
            skew = scipy.stats.skew(vals)
            percentile25 = np.nanpercentile(vals,25)
            percentile50 = np.nanpercentile(vals, 50)
            percentile75 =  np.nanpercentile(vals, 75)
            names = [f.strip()+"_"+stat for stat in stats_names]
            feats = [maximum, minimum, mean, median, std, var, kurt, skew, percentile25, percentile50, percentile75]
            for n in names:
                mm_names.append(n)
            for f in feats:
                mm_feats.append(f)
    newF = open(mmF,'w')
    newF.write(','.join(mm_names)+'\n')
    newF.write(','.join([str(mm) for mm in mm_feats]))
    newF.close()
    print 'Done combining modalities!'


def one_csv(dir):
    # mm_files = [pandas.read_csv(os.path.join(dir,f)) for f in os.listdir(dir) if 'multimodal' in f]
    mm_files = glob.glob(dir + "/*_multimodal.csv")
    frame = pandas.DataFrame()
    dfs = []
    for filename in mm_files:
        dfs.append(pandas.read_csv(filename))
    frame = pandas.concat(dfs)
    frame.to_csv(os.path.join(dir,"ALL_MULTIMODAL.csv"))


def json2txt(json_file):
    file = open(json_file,'r')
    data = json.load(file)
    transcription = []
    for utterance in data["results"]:
        if "alternatives" not in utterance: raise UnknownValueError()
        for hypothesis in utterance["alternatives"]:
            if "transcript" in hypothesis:
                transcription.append(hypothesis["transcript"])
    newF = open(json_file.replace('.json','.txt'),'w')
    for line in transcription:
        newF.write(line.encode('ascii','ignore'))
    newF.close()
    print "Done converting json to txt - %s!"%json

if __name__ == '__main__':
    my_dir = sys.argv[1]
    lang = sys.argv[2]

    # Get parameters from config file
    config = sys.argv[3]
    json_file = open(config, "r").read()
    pars = json.loads(json_file)

    # Get video files from directory
    files = os.listdir(my_dir)

    # Extract visual features
    # First, check that the video is the right .mp4 format
    # video_files = [f for f in files if f.endswith('.mp4')]
    # openface = pars["OPENFACE"]
    # for f in video_files:
    #     extract_visual(os.path.join(my_dir, f), openface)
    #     video2audio(os.path.join(my_dir, f))

    # Extract audio features using covarep
    # Point to matlab runtime application
    # matlab = pars["MATLAB_RUNTIME"]
    # extract_audio(my_dir, matlab)

    # Use speech-to-text APIs
    audio_files = [f for f in os.listdir(my_dir) if f.endswith('.wav')]
    google_key = str(pars['GOOGLE_API_KEY'])
    ibm_pass = str(pars["IBM_PASSWORD"])
    ibm_un = str(pars["IBM_USERNAME"])
    print ibm_un, ibm_pass
    for f in audio_files:
        if lang == 'english':
            speech2text(os.path.join(my_dir, f), 'en-US', ibm_un, ibm_pass)
        elif lang == 'spanish':
            speech2text(os.path.join(my_dir, f), 'es-ES', ibm_un, ibm_pass)
        # If language in german use Google's API
        elif lang == 'german':
            google_speech2text(os.path.join(my_dir, f), 'de-DE', google_key)


    # Extract ling features
    # audio_files = [f for f in os.listdir(dir) if f.endswith('.wav')]
    # for f in audio_files:
    #     if lang =='english':
    #         transcript_files = [f for f in os.listdir(dir) if f.endswith('_transcript.json')]
    #         bag = LingAnalysis_NonEnglish.bag_of_words(dir,'english')
    #         for f in transcript_files:
    #             LingAnalysis_NonEnglish.get_feats(os.path.join(dir,f),bag,'english')
    #
    #     elif lang =='german':
    #         transcript_files = [f for f in os.listdir(dir) if f.endswith('_transcript.json')]
    #         bag = LingAnalysis_NonEnglish.bag_of_words(dir,'german')
    #         for f in transcript_files:
    #             LingAnalysis_NonEnglish.get_feats(os.path.join(dir,f),bag,'german')
    #
    #     elif lang =='spanish':
    #         bag = LingAnalysis_NonEnglish.bag_of_words(dir,'spanish')
    #         for f in transcript_files:
    #             LingAnalysis_NonEnglish.get_feats(os.path.join(dir,f),bag,'spanish')

    # Combine features from all three modalities
    # transcript_files = [f for f in os.listdir(dir) if f.endswith('_transcript.json')]
    # for f in transcript_files:
    #     combine_modes(os.path.join(dir,f))

    # Combine all multimodal csvs into one csv
    # one_csv(dir)

    # Convert json to txt files
    # transcript_files = [f for f in os.listdir(dir) if f.endswith('_transcript.json')]
    # for f in transcript_files:
    #     json2txt(os.path.join(dir,f))
