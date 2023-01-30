import cv2

img_array = []
g=0

for a in range(1800):
    img = cv2.imread("frame_speed/sample-out%d.jpg"%a)
    height, width, layers = img.shape
    size = (width, height)
    img_array.append(img)
    if g == 0:
        out = cv2.VideoWriter('j2.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    if g == 900:
        for i in range(len(img_array)):
            out.write(img_array[i])
        img_array = []
    g+=1

    print(g)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()
