import configparser
cfg = configparser.ConfigParser()
cfg.read('app.cfg')

import os, sys, cv2, time
from Packages import Kinect as kn, mainWindow, SSDFace as ssdf
from API import client
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QImage

try: 
	os.mkdir(cfg.get('log', 'log_dir'))
	os.mkdir(cfg.get('file', 'img_save_dir'))
except:
	pass

log_dir = cfg.get('log', 'log_dir')


with open(os.path.join(log_dir, cfg.get('log', 'log_sys')), 'a') as srw:
	srw.writelines(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+' '+'open')
	srw.write('\n')
srw.close()

class AppWindow(QMainWindow, mainWindow.Ui_MainWindow):
	def __init__(self):
		super(AppWindow, self).__init__()
		self.setupUi(self)

		self.current_timer = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		self.ssd = ssdf.cv2_ssd(
				prototxt=cfg.get('ssd', 'prototxt'),
				model=cfg.get('ssd', 'model'),
				threshold=float(cfg.get('ssd', 'threshold'))
			)
		self.face_cnt = 0
		self.img_save_dir = cfg.get('file', 'img_save_dir')

		self.kn_timer = QTimer()
		self.cFrame = kn.Color() #open kinect color frame
		self.slot_init()
		self.showFullScreen()
		self.show()
		self.frame_Start()

	def slot_init(self):
		self.btn_exit.clicked.connect(self.btn_exit_Click)
		self.kn_timer.timeout.connect(self.capture_)

	def kn_timer_ctrl(self):
		state = self.kn_timer.isActive()
		if not state:
			self.kn_timer.start(30)
			self.capture_()

	def frame_Start(self):
		#Open Kinect
		self.pic_ts = time.time()
		if self.kn_timer.isActive() == False:
			self.kn_timer_ctrl()
			print("camera open")

	def capture_(self):
		frame = self.cFrame.get()
		color = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
		height, width, channel = color.shape

		facefile = self.ssd.detect(color)
		if facefile is not None and len(facefile)>0:
			for faces in range(len(facefile)):
				x1, y1, x2, y2 = facefile[faces][0]

				if x1<0:x1=0
				if y1<0:y1=0

				self.predict_ans = client.useAPI(frame[y1:y2, x1:x2]).get_answer()

				if self.predict_ans == 'e':
					self.label_frame.setText(cfg.get('hint', 'api_error'))
					self.kn_timer.stop()
				else:
					
					self.pred_gender = self.predict_ans['Gender']
					self.pred_age = self.predict_ans['Age']
				texts = self.pred_gender+', '+str(int(self.pred_age)-4)+'~'+str(int(self.pred_age)+1)
				cv2.putText(color, texts, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)
				cv2.rectangle(color, (x1, y1), (x2, y2), (255,0,0), 3)
				with open(os.path.join(log_dir, cfg.get('log', 'log_recg')), 'a') as rrw:
					rrw.writelines(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+' '+self.pred_gender+', '+str(self.pred_age))
					rrw.write('\n')
				rrw.close()

			cv2.imwrite(
				os.path.join(
					self.img_save_dir,
					str(time.time())+str(self.face_cnt)+'.jpg'
				),
				cv2.resize(
					cv2.cvtColor(
						color, cv2.COLOR_BGR2RGB
					),
					(960, 540)
				)
			)

		qimg_c = QImage(color.data, width, height, width*3, QImage.Format_RGB888)
		self.label_frame.setPixmap(QPixmap.fromImage(qimg_c))

	def btn_exit_Click(self):
		self.kn_timer.stop()
		self.label_frame.clear()
		self.label_frame.setText("Camera Zone")
		cv2.destroyAllWindows()
		print('camera close')
		self.close()

		with open(os.path.join(log_dir, cfg.get('log', 'log_sys')), 'a') as srw:
			srw.writelines(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+' '+'system/close')
			srw.write('\n')
		srw.close()


app = QApplication(sys.argv)
main = AppWindow()
main.show()
sys.exit(app.exec_())