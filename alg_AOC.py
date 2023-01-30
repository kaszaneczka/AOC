import cv2
import numpy as np
import pandas as pd

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def polacz(x, y, shape):
    xx = shape[0] - 1
    yy = shape[1] - 1

    polaczone = list()

    for dx in range(3):
        for dy in range(3):
            pix_x = x + dx - 1
            pix_y = y + dy - 1
            if pix_x < 0 or pix_x > xx or \
                    pix_y < 0 or pix_y > yy or \
                    (pix_x == x and pix_y == y):
                pass
            else:
                polaczone.append((pix_x, pix_y))
    return polaczone


def rozrost(img, pkt_start):
    sprawdzenie = lambda x, y, img, wyjscie: img[x, y] != 0
    stan = np.full((img.shape[0], img.shape[1]), False)
    wyjscie = np.zeros_like(img)

    for pixel in pkt_start:
        stan[pixel[0], pixel[1]] = True
        wyjscie[pixel[0], pixel[1]] = img[pixel[0], pixel[1]]

    while (len(pkt_start) > 0):
        b = pkt_start[0]
        for wspl in polacz(b[0], b[1], img.shape):
            if not stan[wspl[0], wspl[1]]:
                if sprawdzenie(wspl[0], wspl[1], img, wyjscie):
                    wyjscie[wspl[0], wspl[1]] = wyjscie[b[0], b[1]]
                    if not stan[wspl[0], wspl[1]]:
                        pkt_start.append(wspl)
                    stan[wspl[0], wspl[1]] = True

        pkt_start.pop(0)
    return wyjscie


def detekcja(nazwa : str):
    param = [750, 119 + 900 + 63, 600, 80]
    kernel = np.ones((5, 5), np.uint8)
    kernel1 = np.ones((3, 3), np.uint8)

    img = cv2.imread(nazwa)
    img = img[int(param[1]):int(param[1] + param[3]), int(param[0]):int(param[0] + param[2])]
    image = cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
    lower = np.uint8([0, 150, 0])
    upper = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(image, lower, upper)

    mask = white_mask

    mask = cv2.dilate(mask,kernel,iterations = 1)

    return mask

def center(vektor):
    zmiany = []
    a = 0
    best = -np.inf
    while a < len(vektor):
        help = a + 1

        if vektor[a] == True:
            while vektor[help] == True:
                help += 1
            xx = pd.Interval(a, help)
            xxx = xx.length

            if xxx > best and xxx < 40:
                best = xxx
                best_mid = int(xx.mid)

        a = help
    if best < 6 :

        return None

    return [best_mid]

def detect_changes(first_frame:str, second_frame:str):
    pierwszy_czarne = detekcja(first_frame)[0]
    drugi_czarne = detekcja(second_frame)[0]
    tablica_przejsc = pierwszy_czarne < drugi_czarne


    return center(tablica_przejsc)

ppredkosc = []
def detect_low(first_frame:str, second_frame:str, last_frame:int):
    ale = detect_changes(first_frame,second_frame)

    seed1 = [(0,ale[0])]
    seed2 = [(0,ale[0])]

    mask1 = detekcja(second_frame)
    mask2 = detekcja('frame%d.jpg' % (last_frame+2)) # tu trzeba poprawic na second + 3

    out1 = rozrost(mask1, seed1)
    last = None
    for x in range(len(out1)):
        if 255 in out1[x]:
            last = x

    out2 = rozrost(mask2, seed2)
    last1 = None
    for x in range(len(out2)):
        if 255 in out2[x]:
            last1 = x

    wysokosc = abs(last1 - last)
    szerokosc = abs(center(out2[last1]>0)[0]- ale[0])
    if szerokosc < 40:
        przkatna = ((wysokosc**2 + szerokosc**2)**(0.5))
        wpslczynnik = 7.473 + (2- 2*szerokosc*(1/40))#5 #2.7559944880165363
        #print(wysokosc,'- wysokość ',szerokosc,'- szerkość',przkatna , '- przekatna')

        #print('predkosc',wysokosc*wpslczynnik,last_frame)
        ppredkosc.append( wysokosc*wpslczynnik)

    return ppredkosc


pred = 0
pred1 = 0
tab_30 = []
odczyt = []
for a in range(0,1800):

    try:
        pred = detect_low("frame%d.jpg"%a, "frame%d.jpg" %(a+1),(a+1) )[-1]
    except:
        pass
    tab_30.append(pred)
    if a%30 == 0:
        pred1 = max(tab_30)
        tab_30 = []
        odczyt.append(int(pred1))
    img = Image.open("frame%d.jpg"%a)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Aaargh.ttf", 100)


    draw.text((0, 0), str(int(pred1)) + " Km/h", (255, 255, 255), font=font)
    img.save('frame_speed/sample-out%d.jpg'%a)

# print(min(ppredkosc),max(ppredkosc),len(ppredkosc))
# print(odczyt)

