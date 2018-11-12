import requests
import numpy as np
import json

'''
show leadsheet sequence in console
'''
def printchord_seq(seq):
    trans = np.flip(seq, 0)
    for r_i, r in enumerate(trans):
        print('[{}]'.format(r_i), end='')
        print() 
        print('[{}]'.format(r), end='') 
        print()
        # print('[{}]'.format(r_i), end='') 
        # for i, w in enumerate(r):
        #     if i > 0 and i % 12 == 0:
        #         print('|', end='')
        #     if w == 0:
        #         print('_', end='')
        #     else:
        #         print('[{}]'.format(w), end='')
        # print()

def printmelody_seq(seq):
    trans = np.flip(seq, 0)
    for r_i, r in enumerate(trans):
        print('[{}]'.format(r_i), end='')
        print() 
        print('[{}]'.format(r), end='') 
        print() 

addr = 'http://localhost:5003'
SONG1 = '0'
SONG2 = '3'
test_url = addr + '/static'
test_url = addr + '/static' + '/'+SONG1+'/'+SONG2
content_type = 'application/json'
headers = {'content-type': content_type}

### GET

response = requests.get(
    test_url,
    headers=headers)

print(response)

r_json = json.loads(response.text)
chord_seq = r_json['chord']
melody_seq = r_json['melody']
tempo_seq = r_json['tempo']
for i, d in enumerate(chord_seq):
    x = i
    y = 0
    print('({}, {})'.format(x, y))
    printchord_seq(d)

for i, d in enumerate(melody_seq):
    x = i
    y = 0
    print('({}, {})'.format(x, y))
    printmelody_seq(d)

for i in enumerate(tempo_seq):
    print('({})'.format(i))

# ### POST
test_url = addr + '/api/content'
# temp = np.zeros((5, 4)) + 0.1
# temp = temp.tolist()
m1 = melody_seq[0]
c1 = chord_seq[0]
m2 = melody_seq[-1]
c2 = chord_seq[-1]
t1 = tempo_seq[0]
t2 = tempo_seq[-1]
theta = 0.8

data = {'m_seq_1': m1,
        'c_seq_1': c1,
        'm_seq_2': m2,
        'c_seq_2': c2,
        'tempo_1': t1,
        'tempo_2': t2,
        'theta': theta,
        }
response = requests.post(
    test_url,
    json=json.dumps(data),
    headers=headers)
# print(response.text)

r_json = json.loads(response.text)
chord_seq = r_json['chord']
melody_seq = r_json['melody']
tempo_seq = r_json['tempo']
for i, d in enumerate(chord_seq):
    x = i
    y = 0
    print('({}, {})'.format(x, y))
    printchord_seq(d)

for i, d in enumerate(melody_seq):
    x = i
    y = 0
    print('({}, {})'.format(x, y))
    printmelody_seq(d)

for i in enumerate(tempo_seq):
    print('({})'.format(i))
