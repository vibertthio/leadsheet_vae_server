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
print(checkpt)
print(songfiles)
# encoder = Encoder().to(device)
# decoder = Decoder().to(device)
vae = model.VAE(hidden_m=256, hidden_c=48, bar=4).to(model.device)
vae.load_state_dict(torch.load(path + checkpt))

'''
load data
'''
### two songs for interpolation
UNIT_LEN = 4 # the length for encode and decode
INTERP_NUM = 6 # number of interpolated samples between
TOTAL_LEN = (INTERP_NUM + 2) * 4
# SONG1 = 'payphone'
# SONG2 = 'someonelikeyou'
# m, c = load_midi(SONG1, SONG2, UNIT_LEN)
# m_roll, c_roll = interp_sample(vae, SONG1, SONG2, m, c, INTERP_NUM)

'''
load preset
'''
preset_file = './static/payphone2someonelikeyou.npy' # type bool (48*total_len, 128, 2)
seed = np.load(preset_file)
seed_m = seed[:, :, 0]
seed_c = seed[:, :, 1]

'''
utils
'''
### numpytojson
def numpy2json(m, c, total_bars):
	out_melody = np.zeros((total_bars, 48, 128))
	out_chord = np.zeros((total_bars, 48, 128))
	for i in range(total_bars):
		out_melody[i] = np.where(m[48*i:48*(i+1),:], 1, 0)
		out_chord[i] = np.where(c[48*i:48*(i+1),:], 1, 0)
	out_melody = out_melody.tolist()
	out_chord = out_chord.tolist()
	response = {
        'melody': out_melody,
		'chord': out_chord,
    }
	response_pickled = json.dumps(response)
	return response_pickled
'''
api route
'''
@app.route('/static', methods=['GET'], endpoint='static_1')
def static():
    with torch.no_grad():
        global seed_m, seed_c
        global TOTAL_LEN

    response_pickled = numpy2json(seed_m, seed_c, TOTAL_LEN)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/static/<s1>/<s2>', methods=['GET'], endpoint='static_twosong_1', defaults={'num': '4'})
@app.route('/static/<s1>/<s2>/<num>', methods=['GET'], endpoint='static_twosong_1')
def static_twosong(s1, s2, num):
    with torch.no_grad():
        global UNIT_LEN
        global INTERP_NUM
        global TOTAL_LEN
        global path
        INTERP_NUM = int(num)
        TOTAL_LEN = (INTERP_NUM + 2) * 4
        
        song1 = path + songfiles[int(s1)]
        song2 = path + songfiles[int(s2)]
        print('song1:',song1)
        print('song2:',song2)
        m, c = model.load_midi(song1, song2, UNIT_LEN)
        m_roll, c_roll = model.interp_sample(vae, s1, s2, m, c, INTERP_NUM)
 
    response_pickled = numpy2json(m_roll, c_roll, TOTAL_LEN)
    return Response(response=response_pickled, status=200, mimetype="application/json")
'''
start app
'''
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003)