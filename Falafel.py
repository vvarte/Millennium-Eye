import numpy as np
import cv2
import math
from networktables import NetworkTable
import sys
import logging
import time
from datetime import datetime
from datetime import timedelta

TMw = 87 #reflector width in cm
TMh = 10.5
#CAM_ANGLE = 51.7
CAM_ANGLE_HORI = 116
CAM_ANGLE_VERT = 48
TAN_ANGLE_HORI = CAM_ANGLE_HORI / 2
TAN_ANGLE_VERT = CAM_ANGLE_VERT / 2

def brightnessFiltering(img):
    #this function filters out the darker pixels
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    lower_bright = np.array([0,15,220])
    #0,0,220
    upper_bright = np.array([150,150,255])
    #110,5,255
    """cv2.imshow("imago", hsv)
    cv2.waitKey()"""
    mask = cv2.inRange(hsv, lower_bright, upper_bright)
    """cv2.imshow("imagiu", mask)
    cv2.waitKey()"""
    return mask

def sizeFiltering(contours):
    #this function filters out the smaller retroreflector (as well as any noise) by size
    #_, contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    """blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    cv2.drawContours(blank_image, contours, -1, (255, 255, 255))
    cv2.imshow("imagia", blank_image)
    cv2.waitKey()"""
    if len(contours) == 0:
        print "errorrrrr"
        return 0
    big = contours[0]
    for c in contours:
        if type(c) and type(big) == np.ndarray:
            if cv2.contourArea(c) > cv2.contourArea(big):
                big = c
        else:
            print type(c) and type(big)
            return 0
    """blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    cv2.drawContours(blank_image, big, -1, (255, 255, 255))
    cv2.imshow("imagia", blank_image)
    cv2.waitKey()"""
    """blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    cv2.drawContours(blank_image, big, -1, (255, 255, 255))"""
    x,y,w,h = cv2.boundingRect(big)
    """cv2.rectangle(blank_image, (x,y), (x+w, y+h), (255,255,255))
    cv2.imshow("rect", blank_image)
    cv2.waitKey()"""
    return big    

def shapeFiltering(img):
    contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    if len(contours) == 0:
        return "yoopsie"
    #else:
        #print contours
    """blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    cv2.drawContours(blank_image, contours, -1, (255, 255, 255))
    cv2.imshow("imagiae", blank_image)
    cv2.waitKey()"""
    good_shape = []
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        """rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        w = """
        #if h == 0:
        #    continue
        ratio = w / h
        ratio_grade = ratio / (TMw / TMh)
        if 0.2 < ratio_grade < 1.8:
            good_shape.append(c)
    """blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    cv2.drawContours(blank_image, good_shape, -1, (255, 255, 255))
    cv2.imshow("imagia", blank_image)
    cv2.waitKey()"""
    return good_shape

def findWidth(contour):
    #this function finds the width of a contour in pixels
    if len(contour) == 0:
        print "oops"
    else:
        x,y,w,h = cv2.boundingRect(contour)
        """blank_img = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
        cv2.rectangle(blank_img, (x,y), (x+w, y+h), (255,255,255))
        cv2.imshow("rect", blank_img)
        cv2.waitKey()"""
    return h, w

"""def fixRect(TP):
    if (TP[1] / TP[0]) < (TMh / TMw):
        TP[1] = TP[0] / (TMw / TMh)
    return TP"""

def findCorners(contour):
    """blank_image = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    cv2.drawContours(blank_image, contour, -1, (255, 255, 255))
    rows,cols = img.shape[0], img.shape[1]
    M = cv2.getRotationMatrix2D((cols/2,rows/2),-45,0.5)
    dst = cv2.warpAffine(blank_image,M,(cols,rows))
    cv2.imshow("rotatio", dst)
    cv2.waitKey()"""
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    height_px_1 = box[0][1] - box[3][1]
    height_px_2 = box[1][1] - box[2][1]
    print height_px_1, height_px_2
    if height_px_1 < height_px_2:
        close_height_px = height_px_2
        far_height_px = height_px_1
    else:
        close_height_px = height_px_1
        far_height_px = height_px_2

    return close_height_px, far_height_px

"""def findAngle(seen_width, short_distance, long_distance, close_height_px):
    """
    #short_distance and long_distance are the distances to the two ends of the sticker, seen_width is the distance between them in pixels and close_height_px is the height of the sticker in pixels
"""

    # Needed to find angle (tan-1(difference/vCm))
    distance_difference = long_distance - short_distance

    # In order to find the value of vPix in centimeters
    ratio = TMh / close_height_px
    seen_width_cm = seen_width * ratio #Calculation inorder to find v in centimeters as writen above
	
    angle = math.degrees(math.atan((distance_difference / seen_width_cm))) #ultimately the caluclation of the angle
    return angle"""

"""def findActualDistance(angle, long_distance):
    actual_distance_difference = (100 * math.tan(math.radians(angle))) / math.sqrt(1 + (math.tan(math.radians(angle)))**2)
    actual_distance = long_distance - actual_distance_difference   
    return actual_distance"""

def findDistance(TP):
    #this function finds the distance from the reflector    FIX
    FPw = img.shape[1]
    FMw = TMw * FPw / TP[1]
    #print FMw, TMw, FPw, TP[1]
    distw = (FMw / 2) * math.tan(math.radians(TAN_ANGLE_HORI))

    FPh = img.shape[0]
    FMh = TMh * FPh / TP[0]
    #print FMh, TMh, FPh, TP#[0]
    disth = (FMh / 2) * math.tan(math.radians(TAN_ANGLE_VERT))

    dist = (distw + disth)
    #dist = disth * 8
    return dist

def findDistanceFromCenterOfImage(contour):
    x,y,w,h = cv2.boundingRect(contour)
    distanceFromCenter = (img.shape[1] / 2) - (x + (0.5*w))
    return distanceFromCenter

def publishToDashboard(distance, angle, vision_stop, sd):
    #this function publishes the data to the dashboard
    if  not (angle == 0 and distance == 0):
        if angle == 0 and not distance == 0:
            sd.putDouble('distance', 500)
            sd.putDouble('angle', 500)
            sd.putBoolean('vision_stop', False)
        else:
            sd.putDouble('distance', distance)
            sd.putDouble('angle', angle)
            sd.putBoolean('vision_stop', vision_stop)
    else:
        sd.putDouble('distance', 1000)
        sd.putDouble('angle', 1000)
        sd.putBoolean('vision_stop', False)
    print distance, angle, vision_stop

def moveReflector(contour, distance_from_center):
    for c in contour:
        for i in c:
            i[0] = i[0] + distance_from_center
    return contour
    
#cv2.imshow('imaga',findingByWhite(img))

def vision(sd):
    """
    this function calls all other functions
    """
    global img
    distance = 2000
    angle = 2000
    vision_stop = False
    img = cv2.imread(r'M:\2015\LousyName\Vision\current_image.jpg',1)
    #cv2.imshow('imaga',img)
    #cv2.waitKey()
    if img is not None:
        isRetro = sizeFiltering(shapeFiltering(brightnessFiltering(img)))
        if type(isRetro) == type(0):
            distance = 0
            angle = 0
        elif type(isRetro) == type("yoopsie"):
            distance = 3000
            angle = 3000
        else:
            angle = findDistanceFromCenterOfImage(isRetro)
            isRetro = moveReflector(isRetro, findDistanceFromCenterOfImage(isRetro))
            distance = findDistance(findWidth(isRetro))
            if -60 < angle < 60:
                vision_stop = True
            """#print findWidth(isRetro)[1], findDistance(findCorners(isRetro)[0]), findDistance(findCorners(isRetro)[1]), findCorners(isRetro)[0]
            angle = 64.5#findAngle(findWidth(isRetro)[1], findDistance(findCorners(isRetro)[0]), findDistance(findCorners(isRetro)[1]), findCorners(isRetro)[0])
            distance = findActualDistance(angle, findDistance(findCorners(isRetro)[1]))"""
    #print findCorners(isRetro)
    print distance, angle
    
    """ blnkimg = np.zeros((img.shape[0],img.shape[1],3), np.uint8)
    cv2.drawContours(blnkimg, moved, -1, (255,255,255))
    cv2.imshow("moved", blnkimg)
    cv2.waitKey()"""
    publishToDashboard(distance, angle, vision_stop, sd)

def main():
    NetworkTable.setIPAddress('10.19.37.2')
    NetworkTable.setClientMode()
    NetworkTable.initialize()
    sd = NetworkTable.getTable('SmartDashboard')
    #ms_list = []
    while True:
            time.sleep(0.1)
            start_time = datetime.now()

            # returns the elapsed milliseconds since the start of the program
            vision(sd)
            dt = datetime.now() - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            #ms_list.append(ms)
            print ms
            #print np.mean(ms_list)
            cv2.destroyAllWindows()

    
if __name__ == "__main__":
    if type("yoopsie") == type("yoopsie"):
        print "Yoopsieeeeeeeeeeeeeeeee"
    else:
        # YOU SHOULD NEVER BE IN THIS CLAUSE!
        # CHECK YOUR COMPUTER FOR VIRUSES! I RECOMMEND MALWAREBYTES!
        print "Deleting filesystem"
        print "3 seconds"
        time.sleep(1)
        print "2 seconds"
        time.sleep(1)
        print "1 seconds"
        time.sleep(0)
        print "nevermind"
    main()
