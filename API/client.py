import requests, json, cv2

url1 = ''

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
			response1 = requests.post(url1, data=self.img_encoded.tostring(), headers=headers, timeout = 3)

			get_json1 = json.loads(response1.text)
			return get_json1
		except:
			return 'e'
			