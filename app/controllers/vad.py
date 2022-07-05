from flask import Blueprint, request,jsonify
import app.modules.vad as vadModule
from scipy.io.wavfile import read
import io

vadCtrl = Blueprint('vad',__name__)
  
"""
HTTP Method: POST
Content-type: application/json
傳送 base64 字串並取得經過 VAD 後的 ASR 結果
"""
@vadCtrl.route('/base64', methods=['POST'])
def getBase64Result():
    # 取得 base64 音檔字串
    insertValues = request.get_json()
    base64String=insertValues['base64']
    
    # 取得 16kHz waveform
    waveform_16k = vadModule.base64String2Wav(base64String)
    # 取得 VAD 分段資訊
    vadResult = vadModule.getVADResult(waveform_16k)
    result = vadModule.getASRResult(waveform_16k, vadResult)
    return result

"""
HTTP Method: POST
Content-type: multipart/form-data
傳送 .wav 音檔 File 並取得經過 VAD 後的 ASR 結果
"""
@vadCtrl.route('/file', methods=['POST'])
def getFileResult():
    # 取得二進制音檔
    binaryFile = request.files['audioFile'].read()
    
    # 取得 16kHz waveform
    waveform_16k = vadModule.byte2Wav(binaryFile)
    # 取得 VAD 分段資訊
    vadResult = vadModule.getVADResult(waveform_16k)
    result = vadModule.getASRResult(waveform_16k, vadResult)
    return result

@vadCtrl.route('/test', methods=['POST'])
def postTest():
    # 取得 base64 音檔字串
    insertValues = request.get_json()
    base64String=insertValues['text']
    print(base64String)
    return base64String