from flask import jsonify
import io
from scipy.io.wavfile import read, write
import torch
import base64
import librosa 
import speech_recognition as sr
import numpy as np

model, utils = torch.hub.load(repo_or_dir='silero-vad-master',
                              model='silero_vad',
                              source = 'local',
                              force_reload=False)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

def byte2Wav(binaryFile):
    # 讀取二進位檔並取得 waveform 與 sample rate
    samplerate, data = read(io.BytesIO(binaryFile))
    print(samplerate, data)
    # Resample data
    waveform_16k = librosa.resample(data.astype('float'), orig_sr=samplerate, target_sr=16000)
    return waveform_16k

def getASRResult(waveform_16k, vadResult):
    
    dataList=[]
    for i in range(len(vadResult)):
        start=vadResult[i]['start']
        end=vadResult[i]['end']
        sampling_rate = 16000
        byte_io = io.BytesIO(bytes())
        wav = waveform_16k[start:end]
        audio_array = np.int16(wav/np.max(np.abs(wav)) * 32767) # 方法1
        write(byte_io, sampling_rate, audio_array)
        result_bytes = byte_io.read()

        audio_data = sr.AudioData(result_bytes, sampling_rate, 2)
        r = sr.Recognizer()
        try:
            text = r.recognize_google(audio_data, language='cmn-Hant-TW')
            dataList.append({"start": start/sampling_rate, "end": end/sampling_rate, "text": text})
        except:
            print(f'no text detected on {i}')
            
    return jsonify({'results': dataList})

def getVADResult(waveform_16k):
    """
    取得語意分析結果
    Args:
        sentence(string): 辨識句子(限512字元)
    Return:
        回傳情意分析結果
    """
    
    speech_timestamps = get_speech_timestamps(waveform_16k, model, sampling_rate=16000)
    print(speech_timestamps)
    
    return speech_timestamps

def getAnalyzeResult(base64String):
    """
    取得語意分析結果
    Args:
        sentence(string): 辨識句子(限512字元)
    Return:
        回傳情意分析結果
    """
    decoded_data = base64.b64decode(base64String)
    print(type(decoded_data))
    samplerate, data = read(io.BytesIO(decoded_data))
    print(samplerate, data)
    # Resample data
    number_of_samples = round(len(data) * float(16000) / samplerate)
    wav = sps.resample(data, number_of_samples)
    print(wav)
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)
    print(speech_timestamps)
    
    return jsonify({'results': speech_timestamps})