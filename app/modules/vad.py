from flask import jsonify
import io
from scipy.io.wavfile import read, write
import torch
import base64
import librosa 
import speech_recognition as sr
import numpy as np

# download to .cache folder
# model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
#                               model='silero_vad',
#                               force_reload=True)
# run local by path to a local directory
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

def base64String2Wav(base64String):
    # 將 base64 字串轉成 byte 格式
    decoded_data = base64.b64decode(base64String)
    # 讀取二進位檔並取得 waveform 與 sample rate
    samplerate, data = read(io.BytesIO(decoded_data))
    print(samplerate, data)
    # Resample data
    waveform_16k = librosa.resample(data.astype('float'), orig_sr=samplerate, target_sr=16000)
    return waveform_16k
    

def getASRResult(waveform_16k, vadResult):
    """
    取得ASR語音辨識結果
    Args:
        waveform_16k(ndarray): 單聲道音訊 waveform 矩陣
        vadResult(ndarray): VAD 結果
    Return:
        回傳每段聲音ASR辨識結果: {"result": [{"start": 0.0, "end": 22.398, "text": "XXXXX"},...]}
    """
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
    取得VAD分析結果
    Args:
        waveform_16k(ndarray): 單聲道音訊 waveform 矩陣
    Return:
        回傳VAD分析結果: [{'start': 0, 'end': 425952},...]
    """
    
    speech_timestamps = get_speech_timestamps(waveform_16k, model, sampling_rate=16000)
    print(speech_timestamps)
    
    return speech_timestamps
