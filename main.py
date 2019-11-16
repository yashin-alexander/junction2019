#!/usr/bin/python3
# -*- coding: utf-8 -*-

### General imports ###
from __future__ import division
import altair as alt

from flask import Flask, render_template, session, request, redirect, flash, Response
from flask_sockets import Sockets

from library.speech_emotion_recognition import *
from library.video_emotion_recognition import *
from library.text_emotion_recognition import *
from library.text_preprocessor import *
from nltk import *
from tika import parser
from werkzeug.utils import secure_filename
import tempfile
import base64
import imageio
import gevent
import gevent.threading


VIDEO = []
TMP_FILE = "tmp.png"

class OurCv(object):
    class OurStream(object):
        def read(self):
            # blocking
            while True:
                gevent.sleep(1)
                return None, imageio.imread(TMP_FILE)

    def __init__(self):
        pass

    def VideoCapture(self, _):
        return self.OurStream()




# Flask config
app = Flask(__name__)
app.secret_key = b'(\xee\x00\xd4\xce"\xcf\xe8@\r\xde\xfc\xbdJ\x08W'
app.config['UPLOAD_FOLDER'] = '/Upload'
sockets = Sockets(app)

### YOUTUBE STREAM HANDLERS

import flask_cors

from collections import namedtuple


States = namedtuple('States', ('not_started', 'ended', 'playing', 'pause', 'buffering', 'cued'))

states = {
    -1: States.not_started,
    0: States.ended,
    1: States.playing,
    2: States.pause,
    3: States.buffering,
    5: States.cued
}


class Subject(object):
    def __init__(self):
        self._observers = []

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class VideoStreamState(object):
    NAME = 'Unknown'
    RUNNING_STATES = (States.playing, )
    IDLE_STATES = (States.not_started, States.ended, States.buffering, States.pause, States.cued)

    def __init__(self, handler):
        self.timestamp = None
        self.handler = handler
        self.old_state = None

    def __str__(self):
        return self.NAME

    def process(self, video_state):
        if video_state in self.IDLE_STATES:
            self.handler.state = self.handler.idle_state
        elif video_state in self.RUNNING_STATES:
            self.handler.state = self.handler.running_state

    def get(self):
        return {
            'state': self.NAME,
            'timestamp': self.timestamp,
        }


class VideoStreamStateIdle(VideoStreamState):
    NAME = 'Idle'

    def __init__(self, handler):
        super(VideoStreamStateIdle, self).__init__(handler)


class VideoStreamStateRunning(VideoStreamState):
    NAME = 'Running'

    def __init__(self, handler):
        super(VideoStreamStateRunning, self).__init__(handler)


class VideoStreamHandler(object):
    def __init__(self, duration):
        self.duration = duration
        self.video_name = None
        self.idle_state = VideoStreamStateIdle(self)
        self.running_state = VideoStreamStateRunning(self)
        self.state = self.idle_state

    def update(self, data):
        print("data", data)
        current_time = data.get('current_time')
        video_state = states.get(data.get('current_state'))
        self.video_name = data.get('video_name')
        self.state.process(video_state)
        self.state.timestamp = current_time

    def get_state(self):
        return {
            'video_name': self.video_name,
            'duration': self.duration,
            'state': self.state.get()
        }


class VideoControler(Subject):
    def __init__(self):
        super(VideoControler, self).__init__()
        self.stream_handler = None

    def create_new(self, duration=0):
        self.stream_handler = VideoStreamHandler(duration)
        print("INITIAL BLET", self.get_state())

    def update(self, data):
        self.stream_handler.update(data)
        self.notify()

    def get_state(self):
        return self.stream_handler.get_state()


class Ebosher(object):
    def update(self, subject):
        print("STATE BLET", subject.get_state())


video_controller = VideoControler()
ebosher = Ebosher()


# YOU JUST SHOULD DEFINE YOUR OBSERVER LIKE EBASHERIO

video_controller.register(ebosher)


@app.route('/api/video', methods=['POST'])
def create():
    video_controller.create_new(duration=request.json)
    return Response('', 200)


@app.route('/api/video_state', methods=['POST', 'GET'])
def video_handler():
    try:
        if request.method == 'POST':
            video_controller.update(request.json)
        return video_controller.get_state()
    except (AttributeError, TypeError):
        video_controller.create_new()
        return Response('Created new video', 200)


################################################################################
################################## INDEX #######################################
################################################################################

# Home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

################################################################################
################################## RULES #######################################
################################################################################

# Rules of the game
@app.route('/rules')
def rules():
    return render_template('rules.html')

################################################################################
############################### VIDEO INTERVIEW ################################
################################################################################

# Read the overall dataframe before the user starts to add his own data
df = pd.read_csv('static/js/db/histo.txt', sep=",")

# Video interview template
@app.route('/video', methods=['POST'])
def video() :
    # Display a warning message
    flash('You will have 45 seconds to discuss the topic mentioned above. Due to restrictions, we are not able to redirect you once the video is over. Please move your URL to /video_dash instead of /video_1 once over. You will be able to see your results then.')
    return render_template('video.html')


# Display the video flow (face, landmarks, emotion)
@app.route('/start_analyzer', methods=['GET'])
def video_1():
    try:
        print('startingg GEVENT thread')
        return Response(gen(OurCv(), 10),mimetype='multipart/x-mixed-replace; boundary=frame')
    except:
        return None


@app.route('/video_youtube', methods=['GET'])
def video_youtube():
    print('startingg GEVENT thread')
    t = gevent.Greenlet(gen, OurCv(), 10)
    t.start()
    print('GEVENT thread started')
    return render_template('stream.html')
    # return Response(gen(OurCv()),mimetype='multipart/x-mixed-replace; boundary=frame')


# Dashboard
@app.route('/video_dash', methods=("POST", "GET"))
def video_dash():
    
    # Load personal history
    df_2 = pd.read_csv('static/js/db/histo_perso.txt')


    def emo_prop(df_2) :
        return [int(100*len(df_2[df_2.density==0])/len(df_2)),
                    int(100*len(df_2[df_2.density==1])/len(df_2)),
                    int(100*len(df_2[df_2.density==2])/len(df_2)),
                    int(100*len(df_2[df_2.density==3])/len(df_2)),
                    int(100*len(df_2[df_2.density==4])/len(df_2)),
                    int(100*len(df_2[df_2.density==5])/len(df_2)),
                    int(100*len(df_2[df_2.density==6])/len(df_2))]

    emotions = ["Angry", "Disgust", "Fear",  "Happy", "Sad", "Surprise", "Neutral"]
    emo_perso = {}
    emo_glob = {}

    for i in range(len(emotions)) :
        emo_perso[emotions[i]] = len(df_2[df_2.density==i])
        emo_glob[emotions[i]] = len(df[df.density==i])

    df_perso = pd.DataFrame.from_dict(emo_perso, orient='index')
    df_perso = df_perso.reset_index()
    df_perso.columns = ['EMOTION', 'VALUE']
    df_perso.to_csv('static/js/db/hist_vid_perso.txt', sep=",", index=False)

    df_glob = pd.DataFrame.from_dict(emo_glob, orient='index')
    df_glob = df_glob.reset_index()
    df_glob.columns = ['EMOTION', 'VALUE']
    df_glob.to_csv('static/js/db/hist_vid_glob.txt', sep=",", index=False)

    emotion = df_2.density.mode()[0]
    emotion_other = df.density.mode()[0]

    def emotion_label(emotion) :
        if emotion == 0 :
            return "Angry"
        elif emotion == 1 :
            return "Disgust"
        elif emotion == 2 :
            return "Fear"
        elif emotion == 3 :
            return "Happy"
        elif emotion == 4 :
            return "Sad"
        elif emotion == 5 :
            return "Surprise"
        else :
            return "Neutral"

    ### Altair Plot
    df_altair = pd.read_csv('static/js/db/prob.csv', header=None, index_col=None).reset_index()
    df_altair.columns = ['Time', 'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

    
    angry = alt.Chart(df_altair).mark_line(color='orange', strokeWidth=2).encode(
       x='Time:Q',
       y='Angry:Q',
       tooltip=["Angry"]
    )

    disgust = alt.Chart(df_altair).mark_line(color='red', strokeWidth=2).encode(
        x='Time:Q',
        y='Disgust:Q',
        tooltip=["Disgust"])


    fear = alt.Chart(df_altair).mark_line(color='green', strokeWidth=2).encode(
        x='Time:Q',
        y='Fear:Q',
        tooltip=["Fear"])


    happy = alt.Chart(df_altair).mark_line(color='blue', strokeWidth=2).encode(
        x='Time:Q',
        y='Happy:Q',
        tooltip=["Happy"])


    sad = alt.Chart(df_altair).mark_line(color='black', strokeWidth=2).encode(
        x='Time:Q',
        y='Sad:Q',
        tooltip=["Sad"])


    surprise = alt.Chart(df_altair).mark_line(color='pink', strokeWidth=2).encode(
        x='Time:Q',
        y='Surprise:Q',
        tooltip=["Surprise"])


    neutral = alt.Chart(df_altair).mark_line(color='brown', strokeWidth=2).encode(
        x='Time:Q',
        y='Neutral:Q',
        tooltip=["Neutral"])


    chart = (angry + disgust + fear + happy + sad + surprise + neutral).properties(
    width=1000, height=400, title='Probability of each emotion over time')

    chart.save('static/css/chart.html')
    print("EMOTIONAL TABLE = {} ".format(emotion))
    print("EMO  = {} ".format(df_2))
    
    return render_template('video_dash.html', emo=emotion_label(emotion), emo_other = emotion_label(emotion_other), prob = emo_prop(df_2), prob_other = emo_prop(df))


@sockets.route('/stream')
def stream(ws):
    while not ws.closed:
        message = ws.receive()
        if message is None:
            gevent.sleep(0.1)
            print('SLLEPING')
            continue
        # print(message[:100])
        prefix, msg = message.split(',')
        print(f"prefix: {prefix}")
        # print(f"msg: {msg[:50]}")

        if len(prefix) < 5:
            continue

        f = open(TMP_FILE, "wb")
        f.write(base64.b64decode(msg))
        f.close()
        gevent.sleep(1)

# длина видео


def main():
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    app.url_map.strict_slashes = False
    flask_cors.CORS(app, origins='*')
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
    #app.run(debug=True)


if __name__ == '__main__':
    main()

