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
SONG1 = '1'
SONG2 = '3'
test_url = addr + '/static'
# test_url = addr + '/static' + '/'+SONG1+'/'+SONG2
content_type = 'application/json'
headers = {'content-type': content_type}

response = requests.get(
    test_url,
    headers=headers)

print(response)

r_json = json.loads(response.text)
chord_seq = r_json['chord']
melody_seq = r_json['melody']
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
