import cv2
video = cv2.VideoCapture('jazda.mp4')
flag, img = video.read()
count = 0

param = [0,0,2592,1944]

print(img.shape)
while flag:
  print('Read a new frame: ', flag)
  cv2.imwrite("frame%d.jpg" % count,img[int(param[1]):int(param[1] + param[3]), int(param[0]):int(param[0] + param[2])])
  flag, img = video.read()
  count += 1


