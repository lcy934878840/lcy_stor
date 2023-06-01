import base64
import json
import time
from flask import Flask, render_template, request
from moviepy.video.io.VideoFileClip import VideoFileClip
from datetime import datetime
from detect import predict
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized
import sys
sys.path.append('./ChatBot')
from ChatBot.chatbot import Chat, EnglishNameSearchFor
from SqlClass.SqlOperate import SqlClass



app = Flask(__name__, template_folder='C:\\Users\934878840\WebstormProjects\\mushroomIdentificaton\\template',
            static_folder='C:\\Users\934878840\WebstormProjects\mushroomIdentificaton\\node_modules')

DB = SqlClass()

PredictConfident={}

def toBase64(filename):
    if filename.endswith('.mp4'):
        with open(filename, 'rb') as video_file:
            video_data = video_file.read()
            base64_data = base64.b64encode(video_data).decode('utf-8')
            video_file.close()
        return base64_data
    else:
        pic = open(filename, "rb")
        pic_base64 = base64.b64encode(pic.read())
        pic.close()
        return pic_base64.decode()

def runsReCode(videoPath):
        if videoPath.endswith('.mp4'):
            videoName = videoPath.split('//')
            # 视频重编码，加载预测推理后的视频文件
            video = VideoFileClip(f"runs//{videoName[1]}")
            # 对视频进行重新编码并保存为新的视频文件
            video.write_videofile(f"./video//{videoName[1]}", codec="libx264", audio_codec="aac")
            return True
        

# 渲染登陆界面
@app.route('/', methods=['GET', 'POST'])
def loginHome():
    return render_template('logins.html')

# 获取注册信息
@app.route('/register', methods=['GET', 'POST'])
def register():
    name = json.loads(request.get_data())['UserName']
    phone = json.loads(request.get_data())['UserPhone']
    password = json.loads(request.get_data())['UserPassword']
    reply = DB.Register(name,phone,password)
    return json.dumps({"reply": reply})

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():

    phone = json.loads(request.get_data())['inputPhone']
    password = json.loads(request.get_data())['inputPwd']

    msg=DB.Login(phone,password)

    return json.dumps({"reply": msg})

# 首页
@app.route('/indexHome', methods=['GET', 'POST'])
def indexHome():
    return render_template('indexs.html')

#数据渲染
@app.route('/readData', methods=['GET', 'POST'])
def readData():
    phone = json.loads(request.get_data())['uname']
    print(phone)
    data = DB.FetchPredictedData(phone)
    if json.loads(request.get_data())['loginState']:
        return json.dumps({"data": data})


# 聊天功能
@app.route('/questionsSubmit', methods=['GET', 'POST'])
def Chatbot():
    questions = json.loads(request.get_data())['questions']
    print(questions)
    answer = Chat(questions)
    print(f"answer:{answer}")
    return json.dumps({"answer": answer, "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S")})

# 数据接收
@app.route('/Rev', methods=['GET', 'POST'])
def RevData():
    global mushroomMeg, confidence
    phone = json.loads(request.get_data())['uname']
    #接收时间
    preData = json.loads(request.get_data())['preData']
    RcvDataTime = json.loads(request.get_data())['time']
    #格式化时间
    dt = str(datetime.strptime(RcvDataTime,'%Y/%m/%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'))
    datatime = dt.replace('-', '').replace(':', '').replace(' ', '')
    dataType = preData.split(';')[0]

    # 获取64编码下载图片
    dataBase64 = preData.split(',')[1]
    filePath = phone + datatime + '.' + dataType.split('/')[1] #133247747982023528162318.png
    print(filePath)
    with open(f"Rcv//{filePath}", 'wb') as f:
        f.write(base64.b64decode(dataBase64.encode()))
    f.close()
    #开始预测返回字典
    PredictConfident = predict(f"Rcv//{filePath}")
    #视频重编码
    print('Begin recoding...')
    runsReCode(f"Rcv//{filePath}")
    # 把预测的图片或者视频转为base64返回
    dataBase64 = toBase64(f"runs//{filePath}") if 'image' in dataType else toBase64(f"./video//{filePath}")
    #添加前缀
    dataContent = preData.split(',')[0] + ',' + dataBase64
    #存储
    if PredictConfident or 'image' in dataType:
        mushroomName, confidence = list(PredictConfident.items())[0]
        print(mushroomName,confidence)
        # 获取相关信息
        mushroomMeg = EnglishNameSearchFor(mushroomName)
        print(mushroomMeg)
        # 添加菌子信息到mysql
        DB.AddMushroomMsg(mushroomMeg)
        DB.AddPredictedData(phone+datatime,dataType.split(':')[1],dataContent,RcvDataTime,mushroomMeg['name'],confidence)
        return json.dumps({"reData": dataContent,"mushroomMeg": mushroomMeg,"confidence": confidence})
    else:
        DB.AddPredictedData(phone + datatime, dataType.split(':')[1],dataBase64, RcvDataTime)
        return json.dumps({"reData": dataBase64})

    

#数据删除
@app.route('/deleteData', methods=['GET', 'POST'])
def deleteData():
    deleteDateList = json.loads(request.get_data())['deleteDateList']
    print(deleteDateList)
    reply = DB.DeleteData(deleteDateList)
    return json.dumps({"reply": reply})

if __name__ == '__main__':
    app.run()
