import cv2
import mediapipe as mp
import mouse

# does not count as a library
import math
import numpy as np
import pyautogui
import time
import tensorflow as tf
import csv
# gui libraries -------------------------------------------------------
from tkinter import *
from PIL import Image, ImageTk
import threading

# -----------------------------------------------------------------------------------------------------------------------------------
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
# -----------------------------------------------------------------------------------------------------------------------------------
wCam, hCam = 640, 480
frameR = 150  # reduce the fram so that you don't have to go right to the bottom of teh screen
smoothening = 7  # slider for this

# -----------------------------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------------------------
mp_hands = mp.solutions.hands
model = tf.keras.models.load_model("Model/model")
# -----------------------------------------------------------------------------------------------------------------------------------
screenwidth, screenheight = pyautogui.size()  # get resolution of the users screen
screencordy = 0
# -----------------------------------------------------------------------------------------------------------------------------------
mode = 0
isStopped = False
# -----------------------------------------------------------------------------------------------------------------------------------
fingersuplist = [0, 0, 0, 0, 0]  # [index, middle, 4th finger, pinky finger, thumb]
# --------------- gui -----------------------
# threading
backgroundcolor = "#B4B4B4"
textcolor = "#FFFFFF"
buttoncolor = "#636363"
gesturelist = [
    "pointer",
    "drag click",
    "right click",
    "scroll up",
    "scroll down"
]


def CalcLandmarkList(image, landmarks):  # algorithm
    img_width, img_height = image.shape[1], image.shape[0]  # gets the width and height of the video screen
    landmark_point = []
    for i, landmark in enumerate(landmarks.landmark):
        landmark_x = int(landmark.x * img_width)
        landmark_y = int(landmark.y * img_height)
        # convert the relative coordinates of the landmarks provided by the Mediapipe library into
        # absolute pixel coordinates on the image

        landmark_point.append(
            [landmark_x, landmark_y])  # we do not need z point as we do not want to change it / normalise it
    return landmark_point


def LoggingHandGestures(
        normalised_landmark_list):  # logs the list into a csv file so the neural network can use it to compare, ALGORITHM
    if mode == 3:
        print("logging")
        gesturespath = 'Model/gestures.csv'
        openedfile = open(gesturespath, 'a', newline='')  # opens the path of the gestures folder and makes it writeable
        # makes it so that no new line is created
        writer = csv.writer(openedfile)  # opened using csv writer
        writer.writerow([4, *normalised_landmark_list])  # writes the row with a 3 at the beginning and then
        # screenshot of this not working on discord server
        # it still kept overwriting the data so this did not work
        # instead of writing it should be a which means appending
        #  The * symbol is used to unpack the array elements into individual values within the row.
        time.sleep(0.5)


def flattenlist(iterableList):  # ALGORITHM
    for it in iterableList:
        for element in it:
            yield element


# The yield keyword is used to yield (produce) each element as the generator produces values.
# This effectively flattens the nested structure of the iterables into a single flat sequence of elements.

# returns an array of how many fingers will be up, ignores the thumb
def fingersUp(landmarkList, which_hand):  # algorithm
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

    if which_hand == "RIGHT" and landmarkList[4][0] < landmarkList[2][
        0]:  # Right Thumb # checks if the x coord of the tip of the thumb is
        # less than the index 2 landmark
        fingersuplist[4] = 1
    elif which_hand == "LEFT" and landmarkList[4][0] > landmarkList[2][
        0]:  # Left Thumb # checks if the x coord of the tip of the thumb is
        # greater than the index 2 landmark
        fingersuplist[4] = 1
    else:
        fingersuplist[4] = 0

    return fingersuplist


def whichHand(landmarklist):  # algorithm
    if (landmarklist[20][0] - landmarklist[16][0]) < 0:
        # checks if tip of the pinky finger - 4th finger is negative which means it will be left hand
        return "LEFT"
    else:
        return "RIGHT"


def normaliseLandmarkList(landmarkList):  # algorithm
    # converting to relative coordinates so i can use it in a neural network
    b_x, b_y = 0, 0  # base values, wrist coordinates (x, y)
    for i, lmk_point in enumerate(landmarkList):
        # i is the index of the current element (lmk_point) in the landmarkList.
        # lmk_point is the actual value of the current element in the landmarkList.
        if i == 0:  # if it is at index (wrist) which is 0 then
            b_x = lmk_point[0]  # represents the base coordinates of the wrists x and y position
            b_y = lmk_point[1]

        landmarkList[i][0] = landmarkList[i][
                                 0] - b_x  # gets each x value and subtracts it from the base value of the wrist
        # this essentially makes all the points relative to the list
        landmarkList[i][1] = landmarkList[i][1] - b_y  # gets each y value

        # mediapipe will provide 3d coordinates for the landmarks so we will need to flatten them into a 1d vector (2d arrray)
        landmarkList = list(flattenlist(landmarkList))
        max_value = max(list(map(abs, landmarkList)))  # for each element in the landmark list it will do absolute on it

        def normalise_(n):  # local function so can only be used in this function
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


def WhichGesture(gesturenumber):
    if gesturenumber == 0:
        mouse.wheel(delta=1)
    elif gesturenumber == 1:
        mouse.wheel(delta=-1)  # when doing key algorithm for this include the rest of the psuedocode that will be there


def MainFunction(mousesens, mousesmooth, scrollspeed):
    dragclick = False
    normalclick = False
    rightclick = False

    global mode
    global fingersuplist
    global isStopped

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    prevLocX, prevLocY = 0, 0
    curLocX, curLoxY = 0, 0
    pTime = 0  # need for frame rate

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1) as hands:
        while cap.isOpened() and not isStopped:
            # break by pressing esc
            key = cv2.waitKey(10)
            if key == 27:  # esc key
                break

            if key == 107:  # k
                mode = 3
            elif key == 110:  # n
                mode = 0

            success, img = cap.read()  # reads the video captured and returns two values
            if not success:  # if there is no image then break out of the loop
                break
            img = cv2.flip(img, 1)  # flips the image
            # detection by mediapipe
            img, results = DetectHands(img, hands)
            # cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

            # MainWindow.UpdateVideoLabel(cv2image)

            # draw hand landmarks
            if results.multi_hand_landmarks:
                for handLandmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(img, handLandmarks, mp_hands.HAND_CONNECTIONS)
                    # show image here

                    landmark_list = CalcLandmarkList(img, handLandmarks)
                    normalisedLandmarkList = normaliseLandmarkList(landmark_list)  # coordinates are in relation to the

                    # wrist where the starting of the wrist is the base point
                    # in total there are 21 hand landmarks so the normalised list gives\
                    # you 42 for each x and y value
                    # this list will be used for the neural network
                    # get tip of index and middle finger
                    LoggingHandGestures(normalisedLandmarkList)
                    xindex, yindex = landmark_list[8][0], landmark_list[8][1]
                    xmiddle, ymiddle = landmark_list[12][0], landmark_list[12][1]

                    whichhand = whichHand(landmark_list)  # checks which hand is showing
                    fingersuplist = fingersUp(landmark_list, whichhand)
                    print(fingersuplist)

                    # draw on show
                    cv2.rectangle(img, (100, 100), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
                    # MOUSE FUNCTIONS -------------------------------------------------------------------------------------
                    if fingersuplist[0] == 1 and fingersuplist[1] == 0 and fingersuplist[
                        4] == 1:  # now will change the mouse
                        rightclick = False
                        xlowerindex, ylowerindex = landmark_list[6][0], landmark_list[6][1]
                        xthumbtip, ythumbtip = landmark_list[4][0], landmark_list[4][1]
                        distanceofthumbandindex = int(
                            math.sqrt(((xlowerindex - xthumbtip) ** 2) + ((ylowerindex - ythumbtip) ** 2)))
                        # coordinates to move mouse
                        # could be a classed as an algorithm

                        cv2.circle(img, center=(xindex, yindex), radius=10, color=(0, 255, 0))
                        xpos = np.interp(xindex, (frameR, wCam - frameR), (0, screenwidth))
                        ypos = np.interp(yindex, (frameR, hCam - frameR), (0, screenheight))

                        curLocX = prevLocX + (xpos - prevLocX) / mousesmooth
                        curLocY = prevLocY + (ypos - prevLocY) / mousesmooth

                        # move the mouse
                        mouse.move(curLocX, curLocY)
                        # with pyautogui it made fps low so changed to mouse library, , duration=0.001
                        prevLocX, prevLocY = curLocX, curLocY
                        # this smoothening worked out much better than the library one
                        # finds distance between the thumb and the index finger so to check if drag click should be enabled or not
                        print(distanceofthumbandindex)
                        # LEFT CLICK ----------------------------------------------------------------------------------------------------------------
                        if distanceofthumbandindex < 65 and not normalclick:  # if distance is less than a certain number
                            # coordinates to move mouse. if thumb, index and middle finger are all up and 4th finger is down
                            normalclick = True
                            mouse.click()
                            print("click")
                            time.sleep(0.5)
                        else:
                            normalclick = False
                        # changed the library and it is much smoother now

                    # DRAG CLICK ----------------------------------------------------------------------------------------------------------------
                    elif fingersuplist[0] == 1 and fingersuplist[1] == 1 and fingersuplist[2] == 0 and fingersuplist[
                        4] == 1:
                        # coordinates to move mouse. if thumb, index and middle finger are all up and 4th finger is down
                        cv2.circle(img, center=(xindex, yindex), radius=10, color=(0, 255, 0))
                        xpos = np.interp(xindex, (frameR, wCam - frameR), (0, screenwidth))  # what does np.interp do
                        ypos = np.interp(yindex, (frameR, hCam - frameR), (0, screenheight))  # interpolation

                        curLocX = prevLocX + (xpos - prevLocX) / mousesmooth
                        curLocY = prevLocY + (ypos - prevLocY) / mousesmooth
                        # franeR, wCam part makes it so that the pink box represents the whole screen
                        # move the mouse
                        mouse.move(curLocX, curLocY)  # with pyautogui it made fps low so changed to mouse library

                        prevLocX, prevLocY = curLocX, curLocY
                        distance = int(math.sqrt(((xmiddle - xindex) ** 2) + ((ymiddle - yindex) ** 2)))
                        print(distance)
                        if distance < 35:
                            dragclick = True  # makes it so that it won't always do the mouse.release function
                            # changed the libraryand it is much smoother now
                            mouse.press(button='left')  # holds the mouse down
                        else:  # so that it does not realease the mouse if the part above never even eran
                            if dragclick:
                                mouse.release(button='left')
                                dragclick = False


                    # RIGHT CLICK ----------------------------------------------------------------------------------------------------------------
                    # if index finger is up and middle two fingers are down
                    elif fingersuplist[0] == 1 and fingersuplist[1] == 0 and fingersuplist[2] == 0 and fingersuplist[
                        3] == 1 and not rightclick:
                        rightclick = True
                        mouse.right_click()
                        time.sleep(0.5)

                    # MOUSE FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------
                    # gestures like scrolling only available in mouse and keyboard mode
                    # to make sure they didn't accidentally do a gesture then put the recursive function code in on disc
                    else:
                        # print(np.array(normalisedLandmarkList).shape)
                        # print(np.array(normalisedLandmarkList).dtype) # neural network giving an error so debugging
                        normalisedLandmarkList = np.array(normalisedLandmarkList,
                                                          dtype=np.float32)  # the normalised data at first was of type float64, however the
                        # model will only take in data of type float 32, so had to convert it
                        normalisedLandmarkList = normalisedLandmarkList.reshape(1,
                                                                                -1)  # -1  is used when you dont know or want
                        # to explicitly tell the dimension of that axis
                        prediction = model.predict(normalisedLandmarkList)
                        print("prediction: ")
                        whichhandgesture = np.argmax(np.squeeze(prediction))
                        print(np.argmax(np.squeeze(prediction)))

                        WhichGesture(whichhandgesture)

                    # cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

                    # MainWindow.UpdateVideoLabel(cv2image)

            # frame rate
            cTime = time.time()
            fps = 1 / (cTime - pTime)  # float so make into an int
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            # show image
            cv2.imshow("Gesture Recog", img)

    cap.release()
    cv2.destroyAllWindows()


# to destroy the window with stop button we do cap.release so we would need to create a new instance of cap again to be able to recall it
# which is why it was not working in the frist place
# find a way to stop showing the video wihtout having to release cap

# ---------------- GUI ---------------------------------
class Main:
    def __init__(self, main):

        self.sensitivtyinput = 1
        self.smoothnessinput = 4
        self.scrollinginput = 4
        self.pointeroption = 0
        self.dragclickoption = 1
        self.rightclickoption = 2
        self.scrollupoption = 3
        self.scrolldownoption = 4
        self.thread = None
        self.thread2 = None
        buttonframe = Frame(main, bg=backgroundcolor)

        StartButton = Button(buttonframe, text="Start", padx=20, pady=10, bg=buttoncolor, fg=textcolor,
                             command=self.Start)
        StartButton.grid(row=0, column=0, columnspan=1, sticky=W + E, padx=10, pady=10)

        StopButton = Button(buttonframe, text="Stop", padx=20, pady=10, bg=buttoncolor, fg=textcolor, command=self.Stop)
        StopButton.grid(row=1, column=0, columnspan=1, sticky=W + E, padx=10, pady=10)

        InstructionsPageButton = Button(buttonframe, text="Instructions", padx=20, pady=10, bg=buttoncolor
                                        , fg=textcolor, command=self.OpenInstructionsWindow)
        InstructionsPageButton.grid(row=2, column=0, padx=10, pady=10, sticky=W + E)

        GestureSettingsPageButton = Button(buttonframe, text="Gesture Settings", bg=buttoncolor, fg=textcolor,
                                           command=self.OpenGestureSettingsWindow, padx=20, pady=10)
        GestureSettingsPageButton.grid(row=3, column=0, padx=10, pady=10, sticky=W + E)

        MouseSettingsPageButton = Button(buttonframe, text="Mouse Settings", bg=buttoncolor, fg=textcolor,
                                         command=self.OpenMouseSettingsWindow, padx=20, pady=10)

        MouseSettingsPageButton.grid(row=4, column=0, padx=10, pady=10, sticky=W + E)

        buttonframe.grid(row=0, column=0, sticky=N + S)

        # video frame
        VideoFrame = Frame(main)
        self.label = Label(VideoFrame, text="Video shown here", padx=10, pady=10)
        self.label.grid(row=0, column=0)
        VideoFrame.grid(row=0, column=1)

    # def UpdateVideoLabel(self, image):
    #     img = Image.fromarray(image)
    #     img = ImageTk.PhotoImage(image=img)
    #     self.label.img = img
    #
    #     self.label.config(image=img)

    # ----------------------------------------------------------
    def Start(self):
        global isStopped
        if self.thread is None or not self.thread.is_alive():
            isStopped = False
            self.thread = threading.Thread(target=lambda: MainFunction(self.sensitivtyinput, self.smoothnessinput
                                                                       , self.scrollinginput))
            self.thread.start()

    def Stop(self):
        global isStopped

        if self.thread and self.thread.is_alive():
            isStopped = True
            self.thread.join()
            # self.thread2 = threading.Thread(target=self.UpdateLabel)
            # self.thread2.start()

    def UpdateLabel(self):
        self.label.config(text="video shown here")
        self.thread2.join()

    def OpenGestureSettingsWindow(self):
        gesturesettingsWindow = GestureSettingsWindow(self.UpdateGestureSettings, self.pointeroption,
                                                      self.dragclickoption,
                                                      self.rightclickoption, self.scrollupoption, self.scrolldownoption)

    def OpenMouseSettingsWindow(self):
        mousesettingsWindow = MouseSettingsWindow(self.UpdateMouseSettings, self.sensitivtyinput, self.smoothnessinput,
                                                  self.scrollinginput)

    def OpenInstructionsWindow(self):
        instructionsWindow = InstructionsWindow()

    def UpdateMouseSettings(self, sensitivtyinput, smoothnessinput, scrollinginput):
        self.sensitivtyinput = sensitivtyinput
        self.smoothnessinput = smoothnessinput
        self.scrollinginput = scrollinginput

    def UpdateGestureSettings(self, option1, option2, option3, option4, option5):
        self.pointeroption = self.returnindex(option1)
        self.dragclickoption = self.returnindex(option2)
        self.rightclickoption = self.returnindex(option3)
        self.scrollupoption = self.returnindex(option4)
        self.scrolldownoption = self.returnindex(option5)
        print(option1, option2, option3, option4, option5)
        print(self.pointeroption, self.dragclickoption, self.rightclickoption, self.scrollupoption)

    def returnindex(self, option):
        return gesturelist.index(option)


class GestureSettingsWindow:
    def __init__(self, function, pointeroption, dragclickoption, rightclickoption, scrollupoption, scrolldownoption):
        global pointerimage
        global dragclickimage
        global rightclickimage
        global scrollupimage
        global scrolldownimage

        gesturesettingswindow = Toplevel(bg=backgroundcolor)
        gesturesettingswindow.title("Gesture Settings")
        self.updategesturessettings = function
        gesturesettingswindow.geometry("700x500")

        # frame 1 -------------------------------------------------------------
        gestureframe1 = Frame(gesturesettingswindow)
        pointerlabel = Label(gestureframe1, text="Gesture 1")
        pointerlabel.grid(row=0, column=0, padx=10, pady=10)
        # show image
        pointerimage = Image.open("Photos/pointer.jpg").resize((150, 155))
        pointerimageTK = ImageTk.PhotoImage(pointerimage)
        pointerimagelabel = Label(gestureframe1, image=pointerimageTK)
        pointerimagelabel.grid(row=1, column=0)
        pointerimage.image = pointerimageTK

        # dropdown
        self.option1 = StringVar()
        self.option1.set(gesturelist[pointeroption])
        dropdown1 = OptionMenu(gestureframe1, self.option1, *gesturelist)
        dropdown1.grid(row=2, column=0)
        gestureframe1.grid(row=0, column=0, padx=10, pady=10)

        # frame 2 ---------------------------------------------------------------
        gestureframe2 = Frame(gesturesettingswindow)
        dragclicklabel = Label(gestureframe2, text="Gesture 2")
        dragclicklabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        dragclickimage = Image.open("Photos/dragclick.jpg").resize((150, 155))
        dragclickimageTk = ImageTk.PhotoImage(dragclickimage)
        dragclickimagelabel = Label(gestureframe2, image=dragclickimageTk)
        dragclickimagelabel.grid(row=1, column=0)
        dragclickimage.image = dragclickimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option2 = StringVar()
        self.option2.set(gesturelist[dragclickoption])
        dropdown2 = OptionMenu(gestureframe2, self.option2, *gesturelist)
        dropdown2.grid(row=2, column=0)
        gestureframe2.grid(row=0, column=1, padx=10, pady=10)

        # frame 3 ---------------------------------------------------------------
        gestureframe3 = Frame(gesturesettingswindow)
        rightclicklabel = Label(gestureframe3, text="Gesture 3")
        rightclicklabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        rightclickimage = Image.open("Photos/rightclick.jpg").resize((150, 155))
        rightclickimageTk = ImageTk.PhotoImage(rightclickimage)
        rightclickimagelabel = Label(gestureframe3, image=rightclickimageTk)
        rightclickimagelabel.grid(row=1, column=0)
        rightclickimage.image = rightclickimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option3 = StringVar()
        self.option3.set(gesturelist[rightclickoption])
        dropdown3 = OptionMenu(gestureframe3, self.option3, *gesturelist)
        dropdown3.grid(row=2, column=0)
        gestureframe3.grid(row=0, column=2, padx=10, pady=10)

        # frame 4 ---------------------------------------------------------------
        gestureframe4 = Frame(gesturesettingswindow)
        scrolluplabel = Label(gestureframe4, text="Gesture 4")
        scrolluplabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        scrollupimage = Image.open("Photos/scroll up.jpg").resize((150, 155))
        scrollupimageTk = ImageTk.PhotoImage(scrollupimage)
        scrollupimagelabel = Label(gestureframe4, image=scrollupimageTk)
        scrollupimagelabel.grid(row=1, column=0)
        scrollupimage.image = scrollupimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option4 = StringVar()
        self.option4.set(gesturelist[scrollupoption])
        dropdown4 = OptionMenu(gestureframe4, self.option4, *gesturelist)
        dropdown4.grid(row=2, column=0)
        gestureframe4.grid(row=0, column=3, padx=10, pady=10)

        # frame 5 ---------------------------------------------------------------
        gestureframe5 = Frame(gesturesettingswindow)
        scrolldownlabel = Label(gestureframe5, text="Gesture 5")
        scrolldownlabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        scrolldownimage = Image.open("Photos/scrolldown.jpg").resize((150, 155))
        scrolldownimageTk = ImageTk.PhotoImage(scrolldownimage)
        scrolldownimagelabel = Label(gestureframe5, image=scrolldownimageTk)
        scrolldownimagelabel.grid(row=1, column=0)
        scrolldownimage.image = scrolldownimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option5 = StringVar()
        self.option5.set(gesturelist[scrolldownoption])
        dropdown5 = OptionMenu(gestureframe5, self.option5, *gesturelist)
        dropdown5.grid(row=2, column=0)
        gestureframe5.grid(row=1, column=0, padx=5, pady=5)

        # back button -----------------------------------------------------------------
        backbutton = Button(gesturesettingswindow, text="BACK", bg=buttoncolor, fg=textcolor,
                            command=lambda: self.Back(gesturesettingswindow))
        backbutton.grid(row=1, column=2)

    def Back(self, window):
        # submitting data back to main menu screen
        self.updategesturessettings(self.option1.get(), self.option2.get(), self.option3.get(), self.option4.get(),
                                    self.option5.get())
        window.destroy()


class MouseSettingsWindow:
    def __init__(self, updatefunction, sensitivtyvalue, smoothnessvalue, scrollingvalue):
        mousesettingswindow = Toplevel(bg=backgroundcolor)
        mousesettingswindow.geometry("700x500")
        mousesettingswindow.title("Mouse Settings")
        self.updatemousesettingsfunction = updatefunction

        # Title
        titleLabel = Label(mousesettingswindow, text="Mouse Settings", font=10, bg=backgroundcolor)
        titleLabel.grid(row=0, column=0, columnspan=2, sticky='ew')

        # SENSTIVITY FRAME
        sensitvityframe = Frame(mousesettingswindow)

        sensitivityLabel = Label(sensitvityframe, text="Sensitivity:")
        sensitivityLabel.pack()

        # Sensitivity Slider
        self.sensitivityslider = Scale(sensitvityframe, orient=HORIZONTAL, from_=1, to=10, length=500)
        self.sensitivityslider.set(sensitivtyvalue)
        self.sensitivityslider.pack()

        sensitvityframe.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

        # SMOOTHNESS FRAME ----------------------------------------------------------------------------
        smoothnessframe = Frame(mousesettingswindow)
        smoothnesslabel = Label(smoothnessframe, text="Smoothness:")
        smoothnesslabel.pack()

        # Sensitivity Slider
        self.smoothSlider = Scale(smoothnessframe, orient=HORIZONTAL, from_=1, to=10, length=500)
        self.smoothSlider.set(smoothnessvalue)
        self.smoothSlider.pack()

        smoothnessframe.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # SCROLLING SPEED FRAME ----------------------------------------------------------------------------
        scrollingframe = Frame(mousesettingswindow)
        scrollinglabel = Label(scrollingframe, text="Scrolling Speed:")
        scrollinglabel.pack()

        # Sensitivity Slider
        self.scrollSlider = Scale(scrollingframe, orient=HORIZONTAL, from_=1, to=5, length=500)
        self.scrollSlider.set(scrollingvalue)
        self.scrollSlider.pack()
        scrollingframe.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # back button

        backbutton = Button(mousesettingswindow, text="BACK", bg=buttoncolor, fg=textcolor,
                            command=lambda: self.Back(mousesettingswindow))
        backbutton.grid(row=4, column=0)

    def Back(self, window):
        # submitting data back through main menu screen
        self.updatemousesettingsfunction(self.sensitivityslider.get(), self.smoothSlider.get(),
                                         self.scrollSlider.get())
        window.destroy()


class InstructionsWindow:
    def __init__(self):
        instructionsWindow = Toplevel()
        instructionsWindow.title("Instructions")
        instructionsWindow.geometry("700x500")
        instructionsframe = Frame(instructionsWindow)

        # store text in a separate text file or variable
        label1 = Label(instructionsframe, text="Instructions here")
        label1.pack(padx=10, pady=10)
        # more photos of the gestures here to explain how to use the program

        instructionsframe.pack()


root = Tk()
root.configure(bg=backgroundcolor)
root.title("Hand Gesture Application")
root.geometry("700x500")
MainWindow = Main(root)
root.mainloop()
