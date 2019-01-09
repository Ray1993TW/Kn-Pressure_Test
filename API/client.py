import configparser
cfg = configparser.ConfigParser()
try:
	cfg.read('API-client.cfg')
except:
	return 'Config file not exist.'

import requests, json, cv2

content_type = 'image/jpeg'
headers = {'content-type': content_type}

class useAPI:
	def __init__(self, frame):
		h,w,c = frame.shape
		if(h<=0):
			h=w
		elif(w<=0):
			w=h
		else:
			self._state_, self.img_encoded = cv2.imencode('.jpg', frame)

	def get_answer(self):
		try:
			response1 = requests.post(cfg.get('net', url1), data=self.img_encoded.tostring(), headers=headers, timeout = 3)
			response2 = requests.post(cfg.get('net', url2), data=self.img_encoded.tostring(), headers=headers, timeout = 3)

			get_json1 = json.loads(response1.text)
			get_json2 = json.loads(response2.text)
			return (get_json1,get_json2)
		except:
			return 'e'
			