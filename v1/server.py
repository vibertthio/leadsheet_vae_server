import os
import time
from flask import Flask, request, Response
from flask_cors import CORS
import numpy as np
import json
import pypianoroll
from pypianoroll import Multitrack, Track
import torch
import torch.utils.data as Data
import vae_4bar as model

app = Flask(__name__)
app.config['ENV'] = 'development'
CORS(app)

'''
load model
'''
path = '/home/vibertthio/local_dir/vibertthio/leadsheetvae/server/presets/'
checkpt = [ m for m in os.listdir(path) if '.pt' in m ][0]
songfiles = [m for m in os.listdir(path) if '.midi' in m]
print(songfiles)
vae = model.VAE(hidden_m=256, hidden_c=48, bar=4).to(model.device)
vae.load_state_dict(torch.load(path + checkpt))

'''
load data
'''
### two songs for interpolation
UNIT_LEN = 4 # the length for encode and decode
INTERP_NUM = 6 # number of interpolated samples between
TOTAL_LEN = (INTERP_NUM+2)*4
RHYTHM_THRESHOLD = 0.6 # number: 0~1
# SONG1 = 'payphone'
# SONG2 = 'someonelikeyou'
# m, c = load_midi(SONG1, SONG2, UNIT_LEN)
# m_roll, c_roll = interp_sample(vae, SONG1, SONG2, m, c, INTERP_NUM)

'''
load preset
'''
# preset_file = './static/payphone2someonelikeyou.npy' # type bool (48*total_len, 128, 2)
# seed = np.load(preset_file)
# seed_m = seed[:, :, 0]
# seed_c = seed[:, :, 1]

'''
utils
'''
### numpytojson
def numpy2json(m, c, tempo):
    out_melody = m.tolist() # (n, 4, 48)
    out_chord = c.tolist() #(n, 4, 4)
    out_tempo = tempo.tolist() #(n)
    #print(type(out_melody))
    response = {
        'melody': out_melody,
        'chord': out_chord,
        'tempo': out_tempo,
    }
    response_pickled = json.dumps(response)
    return response_pickled

'''
api route
'''
@app.route('/static', methods=['GET'], endpoint='static_1')
def static():
    with torch.no_grad():
        global UNIT_LEN
        global INTERP_NUM
        global TOTAL_LEN
        global path
        global RHYTHM_THRESHOLD
        
        song1 = path + songfiles[1] # heyjude
        song2 = path + songfiles[2] # someonelikeyou
        print('song1:',song1)
        print('song2:',song2)
        m, c, tempo = model.load_midi(song1, song2, UNIT_LEN)
        m_seq, c_seq = model.interp_sample(vae, m, c, INTERP_NUM, RHYTHM_THRESHOLD)
    response_pickled = numpy2json(m_seq, c_seq, tempo)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/static/<s1>/<s2>', methods=['GET'], endpoint='static_twosong_1', defaults={'num': 7})
@app.route('/static/<s1>/<s2>/<num>', methods=['GET'], endpoint='static_twosong_1')
def static_twosong(s1, s2, num):
    with torch.no_grad():
        global UNIT_LEN
        global INTERP_NUM
        global TOTAL_LEN
        global path
        INTERP_NUM = num # number of interp group
        # TOTAL_LEN = (INTERP_NUM + 2)*4 # number of group * 4bar = total bars
        
        song1 = path + songfiles[int(s1)]
        song2 = path + songfiles[int(s2)]
        print('song1:',song1)
        print('song2:',song2)
        m, c, tempo = model.load_midi(song1, song2, UNIT_LEN)
        m_seq, c_seq = model.interp_sample(vae, m, c, INTERP_NUM, RHYTHM_THRESHOLD)
    response_pickled = numpy2json(m_seq, c_seq, tempo)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/api/content', methods=['POST'])
def content():
    r = request.json
    r_json = json.loads(r)
    m1 = r_json['m_seq_1']
    c1 = r_json['c_seq_1']
    m2 = r_json['m_seq_2']
    c2 = r_json['c_seq_2']
    t1 = r_json['tempo_1']
    t2 = r_json['tempo_2']
    theta_temp = r_json['theta']

    m_seq1 = np.asarray(m1).astype(int)
    c_seq1 = np.asarray(c1)
    m_seq2 = np.asarray(m2).astype(int)
    c_seq2 = np.asarray(c2)
    tempo_1 = np.asarray(t1)
    tempo_2 = np.asarray(t2)
    theta = np.float(theta_temp)

    tempo = np.array([tempo_1, tempo_2])

    with torch.no_grad():
        global RHYTHM_THRESHOLD
        RHYTHM_THRESHOLD = theta

        m, c = model.load_seq(m_seq1, c_seq1, m_seq2, c_seq2)
        m_seq, c_seq = model.interp_sample(vae, m, c, INTERP_NUM, RHYTHM_THRESHOLD)

    response_pickled = numpy2json(m_seq, c_seq, tempo)
    return Response(response=response_pickled, status=200, mimetype="application/json")
'''
start app
'''
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003)
