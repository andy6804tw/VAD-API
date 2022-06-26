from flask import Blueprint, request,jsonify
import app.modules.vad as vadModule
from scipy.io.wavfile import read
import io

vadCtrl = Blueprint('vad',__name__)
  

@vadCtrl.route('', methods=['GET','POST'])
def getResult():
    # 取得 base64 音檔字串
    insertValues = request.get_json()
    base64String=insertValues['base64']
    
    # 取得 16kHz waveform
#     waveform_16k = vadModule.getAnalyzeResult(base64String)
    # 取得 VAD 分段資訊
    result = vadModule.getAnalyzeResult(base64String)
    return result

@vadCtrl.route('/test', methods=['POST'])
def imagePost():
    # 取得二進制音檔
    binaryFile = request.files['audioFile'].read()
    
    # 取得 16kHz waveform
    waveform_16k = vadModule.byte2Wav(binaryFile)
    # 取得 VAD 分段資訊
    vadResult = vadModule.getVADResult(waveform_16k)
    result = vadModule.getASRResult(waveform_16k, vadResult)
    return result