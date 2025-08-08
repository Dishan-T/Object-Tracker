import cv2
import imutils
import time
import serial


#Red -
#Lower = (0, 100, 20)
#Upper = (10, 255, 255)

#Green -
#Lower = (29,86,6)
#Upper = (64,255,255)

#Blue
Lower = (100,150,0)
Upper = (140,255,255)

vid = cv2.VideoCapture(0)
#vid = cv2.VideoCapture("http://192.168.43.234:8080/video")
stm32 = serial.Serial(port='COM8', baudrate=115200, timeout=.1)

time.sleep(1.0)

last_sent_time = time.perf_counter()

while True:
	ret, frame = vid.read()
	if frame is None:
		break

	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)


	mask = cv2.inRange(hsv, Lower, Upper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	cv2.imshow("mask", mask)


	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None


	if len(cnts) > 0:
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		a=int(M["m10"] / M["m00"])
		b=int(M["m01"] / M["m00"])
		ans1=str(a)
		ans2=str(b)
		center = (a, b)
		height, width = frame.shape[:2]

		current_time = time.perf_counter()
		if current_time - last_sent_time >= 0.02:
			print('Center = ',center)
			stm32.write(('h' + ans1 + ',' + ans2 + '\n').encode('ascii'))
			last_sent_time = current_time

		if radius > 10:
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

vid.release()

cv2.destroyAllWindows()
