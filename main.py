import csv
import cv2
import mediapipe as mp
import mouse

# does not count as a library
import math
import numpy as np
import pyautogui
import time
import tensorflow as tf



# -----------------------------------------------------------------------------------------------------------------------------------
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
# -----------------------------------------------------------------------------------------------------------------------------------
wCam, hCam = 640, 480
frameR = 100  # reduce the fram so that you don't have to go right to the bottom of teh screen
# smoothening = 3
# prevLocX, prevLocY = 0, 0
# curLocX, curLoxY = 0, 0
# -----------------------------------------------------------------------------------------------------------------------------------

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# -----------------------------------------------------------------------------------------------------------------------------------
mp_hands = mp.solutions.hands
model = tf.keras.models.load_model("Model/model")
# -----------------------------------------------------------------------------------------------------------------------------------
screenwidth, screenheight = pyautogui.size()  # get resolution of the users screen
screencordy = 0
# -----------------------------------------------------------------------------------------------------------------------------------
mode = 0
pTime = 0  # need for frame rate
# -----------------------------------------------------------------------------------------------------------------------------------
fingersuplist = [0, 0, 0, 0, 0]  # [index, middle, 4th finger, pinky finger, thumb]
dragclick = False

def CalcLandmarkList(image, landmarks):
    img_width, img_height = image.shape[1], image.shape[0] # gets the width and height of the video screen
    landmark_point = []
    for i, landmark in enumerate(landmarks.landmark):
        landmark_x = int(landmark.x * img_width)
        landmark_y = int(landmark.y * img_height)
        # convert the relative coordinates of the landmarks provided by the Mediapipe library into
        # absolute pixel coordinates on the image

        landmark_point.append([landmark_x, landmark_y])  # we do not need z point as we do not want to change it / normalise it
    return landmark_point


def LoggingHandGestures(normalised_landmark_list): # logs the list into a csv file so the neural network can use it to compare
    if mode == 3:
        print("logging")
        gesturespath = 'Model/gestures.csv'
        openedfile = open(gesturespath, 'a', newline='') # opens the path of the gestures folder and makes it writeable
        # makes it so that no new line is created
        writer = csv.writer(openedfile) # opened using csv writer
        writer.writerow([4, *normalised_landmark_list]) # writes the row with a 3 at the beginning and then
        # screenshot of this not working on discord server
        # it still kept overwriting the data so this did not work
        # instead of writing it should be a which means appending
        #  The * symbol is used to unpack the array elements into individual values within the row.
        time.sleep(0.5)


# does something
def flattenlist(iterableList):  # better name for this
    for it in iterableList:
        for element in it:
            yield element  # what does this function do??? a copy of itertools.chains.from_iterable()
# The yield keyword is used to yield (produce) each element as the generator produces values.
# This effectively flattens the nested structure of the iterables into a single flat sequence of elements.

# returns an array of how many fingers will be up, ignores the thumb
def fingersUp(landmarkList, which_hand):
    if landmarkList[8][1] < landmarkList[6][1]:
        fingersuplist[0] = 1
    else:
        fingersuplist[0] = 0

    if landmarkList[12][1] < landmarkList[10][1]:
        fingersuplist[1] = 1
    else:
        fingersuplist[1] = 0

    if landmarkList[16][1] < landmarkList[14][1]:
        fingersuplist[2] = 1
    else:
        fingersuplist[2] = 0

    if landmarkList[20][1] < landmarkList[18][1]:
        fingersuplist[3] = 1
    else:
        fingersuplist[3] = 0

    if which_hand == "RIGHT" and landmarkList[4][0] < landmarkList[2][0]:  # Right Thumb # checks if the x coord of the tip of the thumb is
        # less than the index 2 landmark
        fingersuplist[4] = 1
    elif which_hand == "LEFT" and landmarkList[4][0] > landmarkList[2][0]:  # Left Thumb # checks if the x coord of the tip of the thumb is
        # greater than the index 2 landmark
        fingersuplist[4] = 1
    else:
        fingersuplist[4] = 0

    return fingersuplist


def whichHand(landmarklist):
    if (landmarklist[20][0] - landmarklist[16][0]) < 0:
        # checks if tip of the pinky finger - 4th finger is negative which means it will be left hand
        return "LEFT"
    else:
        return "RIGHT"


def normaliseLandmarkList(landmarkList):
    # converting to relative coordinates so i can use it in a neural network
    b_x, b_y = 0, 0  # base values, wrist coordinates (x, y)
    for i, lmk_point in enumerate(landmarkList):
        # i is the index of the current element (lmk_point) in the landmarkList.
        # lmk_point is the actual value of the current element in the landmarkList.
        if i == 0:  # if it is at index (wrist) which is 0 then
            b_x = lmk_point[0] # represents the base coordinates of the wrists x and y position
            b_y = lmk_point[1]

        landmarkList[i][0] = landmarkList[i][0] - b_x  # gets each x value and subtracts it from the base value of the wrist
        # this essentially makes all the points relative to the list
        landmarkList[i][1] = landmarkList[i][1] - b_y  # gets each y value

        # mediapipe will provide 3d coordinates for the landmarks so we will need to flatten them into a 1d vector (2d arrray)
        landmarkList = list(flattenlist(landmarkList))
        max_value = max(list(map(abs, landmarkList))) # for each element in the landmark list it will do absolute on it

        def normalise_(n): # local function so can only be used in this function
            return n / max_value

        landmarkList = list(map(normalise_, landmarkList))  # applying the normalise function to all of them
        # maps makes all elements do the normalise function
        return landmarkList


def DetectHands(image, handsmodel):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # changes colour
    image.flags.writeable = False  # makes it not writeable
    result = handsmodel.process(image)
    image.flags.writeable = True  # makes it writeable
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, result

with open('Model/GestureLabels.csv', encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels]
    # may not need this code


with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1) as hands:
    while cap.isOpened():
        # break by pressing esc
        key = cv2.waitKey(10)
        if key == 27:
            break

        if key == 107: # k
            mode = 3
        elif key == 110: # n
            mode = 0

        success, img = cap.read()  # reads the video captured and returns two values
        if not success:  # if there is no image then break out of the loop
            break
        img = cv2.flip(img, 1)  # flips the image
        # detection by mediapipe
        img, results = DetectHands(img, hands)

        # draw hand landmarks
        if results.multi_hand_landmarks:
            for handLandmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(img, handLandmarks, mp_hands.HAND_CONNECTIONS)
                landmark_list = CalcLandmarkList(img, handLandmarks)
                normalisedLandmarkList = normaliseLandmarkList(landmark_list)  # coordinates are in relation to the

                # wrist where the starting of the wrist is the base point
                # in total there are 21 hand landmarks so the normalised list gives\
                # you 42 for each x and y value
                # this list will be used for the neural network2
                # get tip of index and middle finger
                LoggingHandGestures(normalisedLandmarkList)
                xindex, yindex = landmark_list[8][0], landmark_list[8][1]
                xmiddle, ymiddle = landmark_list[12][0], landmark_list[12][1]

                whichhand = whichHand(landmark_list)  # checks which hand is showing
                fingersuplist = fingersUp(landmark_list, whichhand)

                # draw on show
                cv2.rectangle(img, (100, 100), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
                # MOUSE FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------
                if fingersuplist[0] == 1 and fingersuplist[1] == 0:
                    xlowerindex, ylowerindex = landmark_list[6][0], landmark_list[6][1]
                    xthumbtip, ythumbtip = landmark_list[4][0], landmark_list[4][1]
                    # coordinates to move mouse
                    cv2.circle(img, center=(xindex, yindex), radius=10, color=(0, 255, 0))
                    xpos = np.interp(xindex, (frameR, wCam - frameR), (0, screenwidth))  # what does np.interp do
                    ypos = np.interp(yindex, (frameR, hCam - frameR), (0, screenheight))

                    # finds distance between the thumb and the index finger so to check if drag click should be enabled or not
                    distanceofthumbandindex = int(math.sqrt(((xlowerindex - xthumbtip) ** 2) + ((ylowerindex - ythumbtip) ** 2)))
                    # drag click
                    if distanceofthumbandindex < 30: # if distance is less than a certain numebr
                        # coordinates to move mouse. if thumb, index and middle finger are all up and 4th finger is down
                        dragclick = True # makes it so that it wont always do the mouse.release function
                        # changed the libraryand it is much smoother now
                        mouse.press(button='left') # holds the mouse down
                    else:
                        if dragclick:  # so that it does not realease the mouse if the part above never even eran
                            mouse.release(button='left')
                            dragclick = False


                    # move the mouse
                    mouse.move(xpos, ypos, duration=0.001) # with pyautogui it made fps low so changed to mouse library
                    # changed the libraryand it is much smoother now
                elif fingersuplist[0] == 1 and fingersuplist[1] == 1 and fingersuplist[2] == 0 and fingersuplist[4] == 1:
                    distance = int(math.sqrt(((xmiddle - xindex) ** 2) + ((ymiddle - yindex) ** 2)))
                    # distance between two coord formula - normal maths
                    if distance < 23:
                        mouse.click()
                        time.sleep(0.5)

                # right click
                # if index finger is up and middle two fingers are down
                elif fingersuplist[0] == 1 and fingersuplist[1] == 0 and fingersuplist[2] == 0 and fingersuplist[3] == 1:
                    mouse.right_click()
                    time.sleep(0.5)

                # MOUSE FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------
                # gestures like scrolling only available in mouse and keyboard mode
                # to make sure they didn't accidentally do a gesture then put the recursive function code in on disc
                else:
                    # print(np.array(normalisedLandmarkList).shape)
                    # print(np.array(normalisedLandmarkList).dtype) # neural network giving an error so debugging
                    normalisedLandmarkList = np.array(normalisedLandmarkList, dtype=np.float32) # the normalised data at first was of type float64, however the
                    # model will only take in data of type float 32, so had to convert it
                    normalisedLandmarkList = normalisedLandmarkList.reshape(1, -1) # -1  is used when you dont know or want
                    # to explicitly tell the dimension of that axis
                    prediction = model.predict(normalisedLandmarkList)
                    print("prediction: ")
                    whichhandgesture = np.argmax(np.squeeze(prediction))
                    print(np.argmax(np.squeeze(prediction)))
                    if whichhandgesture == 0:
                        mouse.wheel(delta=1)
                    elif whichhandgesture == 1:
                        mouse.wheel(delta=-1)

        # frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime) # float so make into an int
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        # show image
        cv2.imshow("Gesture Recog", img)

cap.release()
cv2.destroyAllWindows()
