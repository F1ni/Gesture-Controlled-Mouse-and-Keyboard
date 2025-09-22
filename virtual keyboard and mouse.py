import cv2
import mediapipe as mp
import mouse


import math
import numpy as np
import pyautogui
import json
import time
import csv
# gui libraries -------------------------------------------------------
from tkinter import *
import torch
from PIL import Image, ImageTk
import threading

# importing neural network class from the file
from NeuralNetUsingPyTorch import GestureModel

# Boolean -----------------------------------------------------------
dragclick = False
normalclick = False
rightclick = False
isStopped = False

# -------------------------------------------------------------------------------------

gesturehistorylist = []
# Used to create the dataset -------------------------------------------------------------
# mode = 0

# --------------- gui ----------------------------------------------------------------------
# color variables
backgroundcolor = "#B4B4B4"
textcolor = "#FFFFFF"
buttoncolor = "#636363"

# -----------------------------------------------------------------------------------------------
# KEYBOARD VARIABLES --------------------------------------------------------
keys = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),

]

# Keyboard parameters
row_offset = [0, 40, 80]
key_width = 80
key_height = 80
start_x = 150   # left margin
start_y = 200   # top margin
gap = 10       # spacing between keys

class KeyboardButton():
    def __init__(self, label, x, y, w=80, h=80):
        self.label = label
        self.x = x
        self.y = y
        self.w = w
        self.h = h


    def draw(self, img, color=(255, 255, 255), pressed=False):
        if pressed:
            color = (0, 255, 0)


        cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), color, 2)
        cv2.putText(img, self.label,
                    (self.x + 10, self.y + 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, color, 2)

    def contains(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h


buttons = []
for row_index, row in enumerate(keys):
    for col_index, key in enumerate(row):
        x = start_x + row_offset[row_index] + col_index * (key_width + gap)
        y = start_y + row_index * (key_height + gap)
        buttons.append(KeyboardButton(key, x, y, key_width, key_height))

# Spacebar: wide button
space_x = start_x + 100  # shift to the right a bit
space_y = start_y + 3 * (key_height + gap)  # below the 3rd row
space_w = 400            # make it wide
buttons.append(KeyboardButton("SPACE", space_x, space_y, space_w, key_height))

# Enter key: tall button on the right
enter_x = space_x + space_w + 20  # right of spacebar
enter_y = space_y
enter_w = 150
buttons.append(KeyboardButton("ENTER", enter_x, enter_y, enter_w, key_height))

# backspace
back_x = enter_x + enter_w + 20
back_y = enter_y
back_w = 175
buttons.append(KeyboardButton("Remove", back_x, back_y, back_w, key_height))


# neural network
# prediction 0 - scroll up
# prediction 1 - scroll down
# prediction 2 - open hand
# prediction 3 - closed hand (fist)

pytorchmodel = GestureModel(input_size=42, num_classes=4) # initialise the pytorch model
path = "model.pth" # stores the file the model is in
pytorchmodel.load_state_dict(torch.load(path)) # load the saved weights that are in the file
pytorchmodel.eval() # put the model in evaluate mode

distanceofthumbandindex = None

# ---------------- GUI ---------------------------------
# First window that the user sees
class Main:
    def __init__(self, main):
        # load settings from the json file
        with open('settings.json', 'r') as f:
            self.config = json.load(f)


        self.root = main

        main.configure(bg=backgroundcolor) # change colour of background
        main.title("Hand Gesture Application") # change title
        main.geometry("425x350") # change width and length

        # assign the variables with their corresponding value in the dictionary we received from the json file
        self.sensitivtyinput = self.config['sensitivity']
        self.smoothnessinput = self.config['smoothness']
        self.scrollinginput = self.config['scrollingspeed']
        self.pointeroption = self.config["pointer"]
        self.dragclickoption = self.config["drag click"]
        self.scrollupoption = self.config["scroll up"]
        self.scrolldownoption = self.config["scroll down"]
        self.topviewcameravariable = IntVar()
        self.topviewcameravariable.set(self.config["topviewvalue"])
        # set thread to none
        self.thread = None

        buttonframe = Frame(main, bg=backgroundcolor) # create a frame to keep the widgets organised
        buttonframe.grid(row=0, column=0, padx=10, sticky=N + S)
        # initalised and display the widgets onto the gui
        StartButton = Button(buttonframe, text="Start", padx=20, pady=10, bg=buttoncolor, fg=textcolor,
                             command=self.Start)
        StartButton.grid(row=0, column=0, columnspan=1, sticky=W + E, padx=10, pady=10) # sticky makes it 'stick' to the edges. W - west, E - east

        # binds the letter 'o' to self.Start() so the user can start the program without having to use the mouse
        main.bind('o', lambda event: self.Start())

        StopButton = Button(buttonframe, text="Stop", padx=20, pady=10, bg=buttoncolor, fg=textcolor, command=self.Stop)
        StopButton.grid(row=1, column=0, columnspan=1, sticky=W + E, padx=10, pady=10)

        InstructionsPageButton = Button(buttonframe, text="Instructions", padx=20, pady=10, bg=buttoncolor
                                        , fg=textcolor, command=self.OpenInstructionsWindow)
        InstructionsPageButton.grid(row=2, column=0, padx=10, pady=10, sticky=W + E)

        GestureHistoryButton = Button(buttonframe, text="View Gesture History", padx=20, pady=10, bg=buttoncolor,
                                      fg=textcolor, command=self.OpenGestureHistoryWindow)
        GestureHistoryButton.grid(row=3, column=0, padx=10, pady=10, sticky=W + E)

        GestureSettingsPageButton = Button(buttonframe, text="Gesture Settings", bg=buttoncolor, fg=textcolor,
                                           command=self.OpenGestureSettingsWindow, padx=20, pady=10)
        GestureSettingsPageButton.grid(row=0, column=1, sticky=W + E, columnspan=1)

        MouseSettingsPageButton = Button(buttonframe, text="Mouse Settings", bg=buttoncolor, fg=textcolor, padx=20,
                                         pady=10,
                                         command=self.OpenMouseSettingsWindow)
        MouseSettingsPageButton.grid(row=1, column=1, sticky=W + E, columnspan=1)

        SaveButton = Button(buttonframe, text='Save Settings', padx=20, pady=10, bg=buttoncolor, fg=textcolor,
                            command=self.SaveSettings)
        SaveButton.grid(row=2, column=1, sticky=W + E, columnspan=1)

        DefaultSettingsButton = Button(buttonframe, text='Default Settings', padx=20, pady=10, bg=buttoncolor,
                                       fg=textcolor, command=self.DefaultSettings)
        DefaultSettingsButton.grid(row=3, column=1, sticky=W + E, columnspan=1)

        # toggle button - value of this Checkbutton is stored in variable 'topviewcameravariable'
        topViewCamera = Checkbutton(buttonframe, text="Top View Camera?", variable=self.topviewcameravariable,
                                    onvalue=1, offvalue=0,
                                    bg=backgroundcolor)
        topViewCamera.grid(row=4, column=0, padx=10, pady=10)


    def DefaultSettings(self):
        # set config to orginal values
        self.config = {"sensitivity": 1, "smoothness": 4,
                  "scrollingspeed": 2, "pointer": "pointer",
                  "drag click": "drag click", "scroll up": "scroll up",
                  "scroll down": "scroll down", "topviewvalue": 0}
        with open('settings.json', 'w') as f: # rewrite the json file with these values
            json.dump(self.config, f)

    # ----------------------------------------------------------

    def SaveSettings(self):
        # set the new values of the settings in the dictionary
        self.config['sensitivity'] = self.sensitivtyinput
        self.config['smoothness'] = self.smoothnessinput
        self.config['scrollingspeed'] = self.scrollinginput
        self.config["pointer"] = self.pointeroption
        self.config["drag click"] = self.dragclickoption
        self.config["scroll up"] = self.scrollupoption
        self.config["scroll down"] = self.scrolldownoption
        self.config["topviewvalue"] = self.topviewcameravariable.get()
        with open('settings.json', 'w') as f: # rewrite the json file with these new values
            json.dump(self.config, f)

    def Start(self):
        global isStopped
        if self.thread is None or not self.thread.is_alive(): # check if the thread empty or if already running
            isStopped = False
            self.thread = threading.Thread(target=lambda: MainFunction(self.sensitivtyinput, self.smoothnessinput
                                                                       , self.scrollinginput, self.pointeroption,
                                                                       self.dragclickoption
                                                                       , self.scrollupoption, self.scrolldownoption,
                                                                       self.topviewcameravariable.get()))
            self.thread.start() # run main function

    def Stop(self):
        global isStopped
        if self.thread and self.thread.is_alive(): # checks if thread is not none and if it is running
            isStopped = True
            self.thread.join() # stops the thready

    def OpenGestureSettingsWindow(self):
        gesturesettingsWindow = GestureSettingsWindow(self.root, self.pointeroption,
                                                      self.dragclickoption, self.scrollupoption, self.scrolldownoption)

    def OpenMouseSettingsWindow(self):
        mousesettingsWindow = MouseSettingsWindow(self.sensitivtyinput, self.smoothnessinput,
                                                  self.scrollinginput, self.root)

    def OpenInstructionsWindow(self):
        instructionsWindow = InstructionsWindow()

    def OpenGestureHistoryWindow(self):
        gesturehistorywindow = GestureHistoryWindow()

# child class
class GestureSettingsWindow(Main): # inherit properties from the parent class (Main)
    def __init__(self, main, pointeroption, dragclickoption, scrollupoption, scrolldownoption):
        # these global variables need to be done due to pythons garbage collection
        # if it is not done then the images do not show
        global pointerimage
        global dragclickimage
        global rightclickimage
        global scrollupimage
        global scrolldownimage
        Main.__init__(self, main) # way to initialise from the parent class into this one

        gesturesettingswindow = Toplevel(bg=backgroundcolor) # creates a new window on top of the main window
        gesturesettingswindow.title("Gesture Settings")
        gesturesettingswindow.geometry("750x500") # ("length x width")

        self.gesturelistforclicking = ["pointer", "drag click"]
        self.gesturelistforscrolling = ["scroll up", "scroll down"]


        # using frames to structure the widgets, makes it easier to debug as each part is in its own frame
        # frame 1 -------------------------------------------------------------

        gestureframe1 = Frame(gesturesettingswindow)
        pointerlabel = Label(gestureframe1, text="Gesture 1")
        pointerlabel.grid(row=0, column=0, padx=10, pady=10)
        # show image
        pointerimage = Image.open("Photos/pointer.png").resize((150, 155))
        pointerimageTK = ImageTk.PhotoImage(pointerimage)
        pointerimagelabel = Label(gestureframe1, image=pointerimageTK)
        pointerimagelabel.grid(row=1, column=0)
        pointerimage.image = pointerimageTK # need to keep a reference to the image due to pythons garbage collection

        # dropdown
        self.option1 = StringVar() # the value of the dropdown is stored in this variable
        self.option1.set(self.gesturelistforclicking[self.returnindex(self.gesturelistforclicking, pointeroption)])
        # set the value of the dropdown to what the user had changed it to before
        dropdown1 = OptionMenu(gestureframe1, self.option1, *self.gesturelistforclicking)
        dropdown1.grid(row=2, column=0)
        gestureframe1.grid(row=0, column=0, padx=10, pady=10)

        # frame 2 ---------------------------------------------------------------
        gestureframe2 = Frame(gesturesettingswindow)
        dragclicklabel = Label(gestureframe2, text="Gesture 2")
        dragclicklabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        dragclickimage = Image.open("Photos/dragclick.png").resize((150, 155))
        dragclickimageTk = ImageTk.PhotoImage(dragclickimage)
        dragclickimagelabel = Label(gestureframe2, image=dragclickimageTk)
        dragclickimagelabel.grid(row=1, column=0)
        dragclickimage.image = dragclickimageTk


        # dropdown
        self.option2 = StringVar() # the value of the dropdown is stored in this variable
        self.option2.set(self.gesturelistforclicking[self.returnindex(self.gesturelistforclicking, dragclickoption)])
        dropdown2 = OptionMenu(gestureframe2, self.option2, *self.gesturelistforclicking)
        dropdown2.grid(row=2, column=0)
        gestureframe2.grid(row=0, column=1, padx=10, pady=10)

        # frame 3 ---------------------------------------------------------------
        gestureframe3 = Frame(gesturesettingswindow)
        rightclicklabel = Label(gestureframe3, text="Gesture 3")
        rightclicklabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        rightclickimage = Image.open("Photos/rightclick.png").resize((150, 155))
        rightclickimageTk = ImageTk.PhotoImage(rightclickimage)
        rightclickimagelabel = Label(gestureframe3, image=rightclickimageTk)
        rightclickimagelabel.grid(row=1, column=0)
        rightclickimage.image = rightclickimageTk  # keep a reference to the image or something???


        # dropdown
        self.option3 = StringVar() # the value of the dropdown is stored in this variable
        self.option3.set("Right Click")
        dropdown3 = OptionMenu(gestureframe3, self.option3, "Right Click")
        # the user is unable to change the function of this gesture so it will always be set as right click
        dropdown3.grid(row=2, column=0)
        gestureframe3.grid(row=0, column=2, padx=10, pady=10)

        # frame 4 ---------------------------------------------------------------
        gestureframe4 = Frame(gesturesettingswindow)
        scrolluplabel = Label(gestureframe4, text="Gesture 4")
        scrolluplabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        scrollupimage = Image.open("Photos/scroll up.png").resize((150, 155))
        scrollupimageTk = ImageTk.PhotoImage(scrollupimage)
        scrollupimagelabel = Label(gestureframe4, image=scrollupimageTk)
        scrollupimagelabel.grid(row=1, column=0)
        scrollupimage.image = scrollupimageTk

        # dropdown
        self.option4 = StringVar()
        self.option4.set(self.gesturelistforscrolling[self.returnindex(self.gesturelistforscrolling, scrollupoption)])
        dropdown4 = OptionMenu(gestureframe4, self.option4, *self.gesturelistforscrolling)
        dropdown4.grid(row=2, column=0)
        gestureframe4.grid(row=0, column=3, padx=10, pady=10)

        # frame 5 ---------------------------------------------------------------
        gestureframe5 = Frame(gesturesettingswindow)
        scrolldownlabel = Label(gestureframe5, text="Gesture 5")
        scrolldownlabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        scrolldownimage = Image.open("Photos/scrolldown.png").resize((150, 155))
        scrolldownimageTk = ImageTk.PhotoImage(scrolldownimage)
        scrolldownimagelabel = Label(gestureframe5, image=scrolldownimageTk)
        scrolldownimagelabel.grid(row=1, column=0)
        scrolldownimage.image = scrolldownimageTk

        # dropdown
        self.option5 = StringVar()
        self.option5.set(self.gesturelistforscrolling[self.returnindex(self.gesturelistforscrolling, scrolldownoption)])
        dropdown5 = OptionMenu(gestureframe5, self.option5, *self.gesturelistforscrolling)
        dropdown5.grid(row=2, column=0)
        gestureframe5.grid(row=1, column=0, padx=5, pady=5)

        # back button -----------------------------------------------------------------
        backbutton = Button(gesturesettingswindow, text="BACK", bg=buttoncolor, fg=textcolor,
                            command=lambda: self.Back(gesturesettingswindow))
        backbutton.grid(row=1, column=2)

    def Back(self, window):
        # submitting data back to the main menu screen using the variables that were inherited
        self.pointeroption = self.option1.get()
        self.dragclickoption = self.option2.get()
        self.scrollupoption = self.option4.get()
        self.scrolldownoption = self.option5.get()

        window.destroy() # destroys the window

    def returnindex(self, list, word):
        return list.index(word) # returns the index of where the word is in the list

# child class
class MouseSettingsWindow(Main):
    def __init__(self, sensitivtyvalue, smoothnessvalue, scrollingvalue, main):
        Main.__init__(self, main)
        mousesettingswindow = Toplevel(bg=backgroundcolor) # creates another window in front of the current one
        mousesettingswindow.geometry("700x500")
        mousesettingswindow.title("Mouse Settings")

        # Title
        titleLabel = Label(mousesettingswindow, text="Mouse Settings", font=10, bg=backgroundcolor)
        titleLabel.grid(row=0, column=0, columnspan=2, sticky='ew')

        # SENSTIVITY FRAME
        sensitvityframe = Frame(mousesettingswindow)
        sensitivityLabel = Label(sensitvityframe, text="Sensitivity:")
        sensitivityLabel.pack()

        # Sensitivity Slider
        # create slider
        self.sensitivityslider = Scale(sensitvityframe, orient=HORIZONTAL, from_=1, to=10, length=500)
        self.sensitivityslider.set(sensitivtyvalue) # set the sensitivity value of slider
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

        defaultsettingsbutton = Button(mousesettingswindow, text="Default Settings", bg=buttoncolor,
                                       fg=textcolor, command=self.DefaultSettings)
        defaultsettingsbutton.grid(row=4, column=1)

        backbutton = Button(mousesettingswindow, text="BACK", bg=buttoncolor, fg=textcolor,
                            command=lambda: self.Back(mousesettingswindow))
        backbutton.grid(row=4, column=0)

    def DefaultSettings(self): # Overrides the method in main, demonstrating polymorphism
        self.sensitivityslider.set(1)
        self.smoothSlider.set(4)
        self.scrollSlider.set(2)

    def Back(self, window):
        # submitting data back to the main menu screen using the variables that were inherited
        self.sensitivtyinput = self.sensitivityslider.get()
        self.smoothnessinput = self.smoothSlider.get()
        self.scrollinginput = self.scrollSlider.get()
        window.destroy() # destroys the window


class InstructionsWindow:
    def __init__(self):
        global pointerimage # needs to be a global variable for some reason otherwise it won't show up. Python garbage collection
        global holdclickimage
        global rightclickimage
        global scrollupimage
        global scrolldownimage

        instructionsWindow = Toplevel()
        instructionsWindow.title("Instructions")
        instructionsWindow.geometry("700x500")
        instructionsframe = Frame(instructionsWindow)

        # https://www.tutorialspoint.com/resizing-images-with-imagetk-photoimage-with-tkinter
        pointerimage = Image.open("Photos/pointer.png").resize((100, 150))
        pointerimage = ImageTk.PhotoImage(pointerimage)

        holdclickimage = Image.open("Photos/dragclick.png").resize((100, 150))
        holdclickimage = ImageTk.PhotoImage(holdclickimage)

        rightclickimage = Image.open("Photos/rightclick.png").resize((100, 150))
        rightclickimage = ImageTk.PhotoImage(rightclickimage)

        scrollupimage = Image.open("Photos/scroll up.png").resize((100, 150))
        scrollupimage = ImageTk.PhotoImage(scrollupimage)

        scrolldownimage = Image.open("Photos/scrolldown.png").resize((100, 150))
        scrolldownimage = ImageTk.PhotoImage(scrolldownimage)


        # initialise the text widget
        instructionstextwidget = Text(instructionsframe, height=20, width=200, font=("Helvetica", 10, "bold"))
        instructionstextwidget.pack()
        # insert all of the instructions. \n is used to indicate a line break
        instructionstextwidget.insert(END, "OVERALL USAGE: \n1. Press 'o' or click the start button to start the capture. Click the Stop button or "
                                           "press 'esc' to stop the capture \n"
                                           "2. Show your hand to the camera. NOTE: The pink box represents the whole screen. If you bring your finger to the"
                                           "corner of the screen, then the mouse will also be at the corner of the screen\n"
                                           "3. To calibrate the software, show an open hand to the camera. This is needed when you have the changed "
                                           "your distance from the camera\nThe number in the top left of the caputre is the number of frames per second"
                                           ". When you show a gesture to the camera, the text that comes up indicates what function you are performing."
                                           " \n\nMove Mouse and LEFT CLICK:\n1. To move the mouse, put your thumb and index finger up "
                                           "(shown in the image), it can be in any orientation, just needs to"
                                           "point up \n2. To peform a LEFT CLICK, bring the thumb closer to the index finger, like shown in the picture \n"
                                           "3. Make sure to bring the thumb away from the index finger, to be able to click again \n")
        instructionstextwidget.image_create(END, image=pointerimage)
        instructionstextwidget.insert(END, "\n\nMove mouse and HOLD CLICK:\n1. To move the mouse, put your thumb, index and middle finger up. Can"
                                           "be done in any oreientation. Make sure the middle finger is apart when you do not want to "
                                           "click\n2. To perform HOLD CLICK, bring in the middle finger to your index finger\n")
        instructionstextwidget.image_create(END, image=holdclickimage)
        instructionstextwidget.insert(END, "\nRIGHT CLICK: \nTo perform a right click, put your thumb, index and little finger up. Can be in any orientation\n\n")
        instructionstextwidget.image_create(END, image=rightclickimage)
        instructionstextwidget.insert(END, "\nSCROLLING:\nShow this gesture to SCROLL UP (can be in any orientation)\n")
        instructionstextwidget.image_create(END, image=scrollupimage)
        instructionstextwidget.insert(END, "\n\nShow this gesture to SCROLL DOWN (can be in any orientation)\n")
        instructionstextwidget.image_create(END, image=scrolldownimage)
        instructionstextwidget.insert(END, "\n\nVIEW GESTURE HISTORY PAGE: \n1. To view the previous 5 gestures that you have used"
                                           "go to the gesture history window. The gesture at the top of the list is the most recent one."
                                           "\n\nGESTURE SETTINGS WINDOW: \nIf you want to change the function that"
                                           "the gesture does, go to this window and choose an option from the dropdown. Press back and then restart"
                                           "the capture\n\nMOUSE SETTINGS WINDOW:\nIn this window you can change the sensitivity, smoothness or scrolling speed."
                                           "After you are happy with the changes, press the BACK button and relaunch the capture\n\nDEFAULT SETTINGS BUTTON:"
                                           "\nThe default settings are the values that I think are the most useable. Press this button, to change back"
                                           "to the original settings. Then restart the application\nNOTE: If the program is to crash, check if there\n"
                                           "is a camera attached to the device")
        instructionstextwidget.config(state=DISABLED) # disable the widget so that you are unable to edit it

        instructionsframe.pack()


class GestureHistoryWindow:
    def __init__(self):
        global gesturehistorylist
        historywindow = Toplevel()
        historywindow.title("Gesture History")
        historywindow.geometry("300x200")

        text = Text(historywindow, height=6, width=30, state=NORMAL)
        text.pack(padx=10, pady=10)
        reversedlist = gesturehistorylist[::-1] # reverses the list
        for i, item in enumerate(reversedlist): # enumerate stores the count the count in i and the item in the list in item
            text.insert(END, str(i + 1) + " " + item + "\n")  # makes it so the item is put in the next line

        text.config(state=DISABLED) # makes it so that the text box is uneditable
        # the value at number 1 is the oldest gestuer and number 5 is the newest gesture


class CircularGestureQueue:  # first in first out
    def __init__(self, max_size):
        self.max_size = max_size
        self.gesture_history = [None] * max_size  # intially set to none
        self.front = 0  # index of the front element
        self.rear = 0  # index where the next element will be inserted
        self.previousgesture = ""  # used to check if the previous gesture is the same. if not then it will be added
        # to the gesture history queue

    def add_gesture(self, gesture):
        # Check if the queue is full before inserting
        if self.is_full():
            self.front = (self.front + 1) % self.max_size  # moves the front index in a circular manner

        self.previousgesture = gesture

        # when the queue is full the front pointer will move such that the oldest gesture gets replaced by the latest
        self.gesture_history[self.rear] = gesture # gesture is added to the rear of the queue
        self.rear = (self.rear + 1) % self.max_size  # increases the rear index by 1, then when it reaches the end
        # it will move back to the front

    def Dequeue(self):
        try:
            return self.gesture_history[self.rear - 1]
        except:
            return "Empty"

    def get_history(self):
        history = []
        # can't do it from self.front to self.rear because sometimes the end index will be smaller than the start index
        # adding self.size accounts for the end index being less than the start index
        for i in range(self.front, self.front + self.size()):
            index = i % self.max_size # without % - i would keep increasing with no bounds. also needed due to the wrap around
            history.append(self.gesture_history[index])
        return history

    def is_full(self):
        # (self.rear + 1) % self.max_size - calculates the next index after self.rear
        if (self.rear + 1) % self.max_size == self.front: # check if the next index after rear is equal to front
            return True
        else:
            return False

    def size(self):
        # adding self.max size is needed here as it ensures the value is always non negative
        return (self.rear - self.front + self.max_size) % self.max_size


def MainFunction(mousesens, mousesmooth, scrollspeed, pointergestureoption, indexandmiddleoption, pointupoption,
                 pointdownoption, topviewcamerabool):
    global isStopped
    global rightclick
    global gesturehistorylist
    global distanceofthumbandindex

    middlefingerup = False
    wCam, hCam = 1280, 720 # width and height of cam
    frameR = 200  # pink box - reduce the frame so that you don't have to go right to the bottom of the screen

    cap = cv2.VideoCapture(0) # start video capture
    cap.set(3, wCam) # set the width and height of the cam
    cap.set(4, hCam)



    gesturehistoryqueue = CircularGestureQueue(6) # initialise queue of size 6
    pTime = 0  # need for frame rate
    calibrateddistancefordragclick = 30 # distance that is used to check if a click is made
    calibrateddistancefornormalclick = 30

    prevLocX, prevLocY = 0, 0 # initialise smoothening variables

    # -----Mediapipe variables------------------------------------------------------------------------
    mp_holistic = mp.solutions.holistic
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    fingersuplist = [0, 0, 0, 0, 0]  # [index, middle, 4th finger, little finger, thumb]

    # keyboard stuff

    fingertip_id_for_mediapipe = [4, 8, 12, 16, 20]
    finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

    last_hovered_key = {}
    finger_extended = {}

    # minimum confidence value for a detection to be considered successful
    # minimum confidence value for a hand to be cosidered successfully tracked
    # max number of hands is 1 - it will only detect and track one hand no matter how many are placed in frame
    # if someone else puts hand in frame, it will keep detecting the person whose hand was in the frame first
    with (mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=2) as hands):
        while cap.isOpened() and not isStopped:
            # break by pressing esc
            key = cv2.waitKey(10)
            if key == 27:  # esc key
                break

            # code to create the dataset - not needed for the final list
            # if key == 107:  # k
            #     mode = 3
            # elif key == 110:  # n
            #     mode = 0
            #     print(gesturehistoryqueue.get_history())

            success, img = cap.read()  # reads the video captured and returns two values

            if not success:  # if there is no image then break out of the loop # error handling
                break

            if topviewcamerabool == 0: # if top view camera is not on then flip the image
                img = cv2.flip(img, 1)

            h, w, _ = img.shape
            # detection by mediapipe
            img, results = DetectHands(img, hands) # returns two values


            # Default: no hover
            # hovered = set()
            # current_time = time.time()
            key_states = {button.label: {'pressed': False, "hovered": None} for button in buttons}

            # if there is a hand captured in the frame and only one hand the activate mouse
            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) <= 1:
                for handLandmarks in results.multi_hand_landmarks:
                    # draw the landmarks on the frame
                    mp_drawing.draw_landmarks(img, handLandmarks, mp_hands.HAND_CONNECTIONS)

                    # takes in the handlandmark list and gets rid of the z values of each landmark
                    landmark_list = CalcLandmarkList(img, handLandmarks)
                    # coordinates are normalised between 0 and 1 to be fed into the neural network
                    normalisedLandmarkList = normaliseLandmarkList(landmark_list)

                    # LoggingHandGestures(normalisedLandmarkList) - used to log the data for the dataset

                    # landmark coordinates
                    xindex, yindex = landmark_list[8][0], landmark_list[8][1] # x and y coordinates for index finger
                    xmiddle, ymiddle = landmark_list[12][0], landmark_list[12][1] # x and y coordinates for middle finger
                    xlowerindex, ylowerindex = landmark_list[6][0], landmark_list[6][1] # x, y coordinates for the lower part of index finger
                    xthumbtip, ythumbtip = landmark_list[4][0], landmark_list[4][1] # x, y coordinates for the thumb tip

                    whichhand = whichHand(landmark_list)  # checks which hand is showing - right or left
                    fingersuplist = fingersUp(landmark_list, whichhand, fingersuplist) # checks which fingers are up
                    # print(fingersuplist) - debugging
                    print(fingersuplist)
                    # print(landmark_list)
                    # creates the pink box on the frame to represent the screen
                    cv2.rectangle(img, (100, 100), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

                    # MOUSE FUNCTIONS -------------------------------------------------------------------------------------
                    # checks if the index finger is up, middle and little fingers are down and if the thumb is up
                    if fingersuplist[0] == 1 and fingersuplist[1] == 0 and fingersuplist[
                        4] == 1 and fingersuplist[3] == 0:
                        middlefingerup = False

                        # create a line from the tip of the thumb to the lower part of the index finger - used for visual feedback
                        cv2.line(img, (xthumbtip, ythumbtip), (xlowerindex, ylowerindex), (0, 0, 255), 4)

                        # if the previous gesture is not the same as this one, then add this gesture to the queue
                        if gesturehistoryqueue.previousgesture != pointergestureoption:
                            gesturehistoryqueue.add_gesture(pointergestureoption)

                        # Check what function it is meant to run - this can be changed based on the users preference
                        prevLocX, prevLocY = WhatFunction(pointergestureoption, landmark_list, mousesens, mousesmooth, img, "pointer",
                                     xindex, yindex, xmiddle, ymiddle, xlowerindex, ylowerindex, xthumbtip, ythumbtip,
                                     calibrateddistancefornormalclick, calibrateddistancefordragclick, prevLocX, prevLocY, frameR,
                                                          wCam, hCam)


                    # DRAG CLICK ----------------------------------------------------------------------------------------------------------------
                    # if thumb, index and middle finger are up and if 4th finger is down then
                    elif fingersuplist[0] == 1 and fingersuplist[1] == 1 and fingersuplist[2] == 0 and fingersuplist[4] == 1:
                        # coordinates to move mouse. if thumb, index and middle finger are all up and 4th finger is down
                        middlefingerup = False

                        # create a line between the top of the index finger to thte top of the middle finger - used for visual feedback
                        cv2.line(img, (xindex, yindex), (xmiddle, ymiddle), (0, 0, 255), 4)

                        # if the previous gesture is not the same as this one, then add this gesture to the queue
                        if gesturehistoryqueue.previousgesture != indexandmiddleoption:
                            gesturehistoryqueue.add_gesture(indexandmiddleoption)

                        # Check what function it is meant to run - this can be changed based on the users preference
                        prevLocX, prevLocY = WhatFunction(indexandmiddleoption, landmark_list, mousesens, mousesmooth, img, "indexandmiddle",
                                     xindex, yindex, xmiddle, ymiddle, xlowerindex, ylowerindex, xthumbtip, ythumbtip,
                                     calibrateddistancefornormalclick, calibrateddistancefordragclick, prevLocX, prevLocY,
                                                          frameR, wCam, hCam)

                    # RIGHT CLICK ----------------------------------------------------------------------------------------------------------------
                    # if index finger is up, middle two fingers are down and little finger is up and right click is false
                    elif fingersuplist[0] == 1 and fingersuplist[1] == 0 and fingersuplist[
                        3] == 1 and fingersuplist[4] == 1 and not rightclick:


                        # if the previous gesture is not the same as this one (right click), then add this gesture to the queue
                        if gesturehistoryqueue.previousgesture != "Right Click":
                            gesturehistoryqueue.add_gesture("Right Click")

                        rightclick = True # set right click to true so that it doesnt keep repeating right click
                        mouse.right_click() # using the mouse library to perform a right click

                    # if middle finger is up - get rid of later - omit this from the documentation
                    elif fingersuplist[0] == 0 and fingersuplist[1] == 1 and fingersuplist[2] == 0 and fingersuplist[
                        3] == 0 and fingersuplist[4] == 0:

                        if not middlefingerup:
                            middlefingerup = True
                            if gesturehistoryqueue.previousgesture != "Middle Finger":
                                gesturehistoryqueue.add_gesture("Middle Finger")
                            pyautogui.hotkey("alt", "f4")

                    # MOUSE FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------

                    else:
                        # print(np.array(normalisedLandmarkList).shape)
                        # print(np.array(normalisedLandmarkList).dtype) # neural network giving an error so debugging it


                        # the normalised data at first was of type float64, however the
                        # model will only take in data of type float 32, so had to convert it
                        normalisedLandmarkList = np.array(normalisedLandmarkList, dtype=np.float32)

                        # 1 is used to show the number of rows, -1 is used as a placeholder to automatically
                        # calculate the number of columns
                        normalisedLandmarkList = normalisedLandmarkList.reshape(1, -1)

                        # converts the normalised landmark list into a pytorch tensor with data type float32
                        input_data = torch.tensor(normalisedLandmarkList, dtype=torch.float32)

                        # disables the gradient computation during forward pass for efficiency
                        with torch.no_grad():
                            # pass the input data into the pytorch model and store result in output
                            output = pytorchmodel(input_data)

                        # get the index of the maximum value in the output tensor
                        prediction = torch.argmax(output).item()
                        print("Prediction: " + str(prediction))

                        if prediction == 0: # if prediction is scroll up gesture
                            if gesturehistoryqueue.previousgesture != pointupoption:
                                gesturehistoryqueue.add_gesture(pointupoption)

                            WhichGesture(scrollspeed, pointupoption)
                        elif prediction == 1:
                            if gesturehistoryqueue.previousgesture != pointdownoption:
                                gesturehistoryqueue.add_gesture(pointdownoption)

                            WhichGesture(scrollspeed, pointdownoption)
                        elif prediction == 2: # if the prediction is open hand gesture
                            # calculates the distance between the wrist and tip of the middle finger
                            handsize = CalulateHandSize(landmark_list)

                            # calibrate the distance for a normal click action
                            # the calibrated distance is set to 30% of the calculated hand size - 1.28 for laptop?
                            calibrateddistancefornormalclick = int(handsize * 0.3)

                            # calibrate the distance for a drag-click action
                            # the calibrated distance is set to 20% of the calculated hand size - 0.3 for laptop
                            calibrateddistancefordragclick = int(handsize * 0.2)

                        middlefingerup = False

                    # if the gesture history queue is not empty
                    if gesturehistoryqueue.size() != 0:
                        # put the name of the gesture that is being shown on the top right of the camera frame
                        cv2.putText(img, gesturehistoryqueue.Dequeue(),
                                    (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))

                        # set the gesture history list to the previous 5 gestures that the user has put up
                        gesturehistorylist = gesturehistoryqueue.get_history()
                    print("calibrateddistance for normal click: " + str(calibrateddistancefornormalclick)) # debugging
                    #print("calibrateddistance for drag click: " + str(calibrateddistancefordragclick)) # debugging

            elif results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
                # keyboard mode
                #currently_pressed = set()
                for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    handedness = results.multi_handedness[hand_id].classification[0].label
                    mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    for fingertip_id in fingertip_id_for_mediapipe:
                        finger = hand_landmarks.landmark[fingertip_id]
                        fingerAndHandId = (handedness, fingertip_id)
                        finger_x, finger_y = int(finger.x * w), int(finger.y * h)
                        # finger_z = finger.z
                        hovered_key = None
                        for button in buttons:
                            if button.contains(finger_x, finger_y):
                                key_states[button.label]['hovered'] = True
                                hovered_key = button.label
                                break

                        extented_now = is_finger_extended(hand_landmarks, fingertip_id, handedness)

                        if fingerAndHandId not in finger_extended:
                            finger_extended[fingerAndHandId] = False
                            last_hovered_key[fingerAndHandId] = None

                        if extented_now:
                            last_hovered_key[fingerAndHandId] = hovered_key

                        if finger_extended[fingerAndHandId] and not extented_now:
                            if last_hovered_key[fingerAndHandId]:
                                print("pressed" + last_hovered_key[fingerAndHandId])
                                keyToPrint = last_hovered_key[fingerAndHandId].lower()
                                key_states[last_hovered_key[fingerAndHandId]]['pressed'] = True
                                last_hovered_key[fingerAndHandId] = None

                                if keyToPrint == "space":
                                    pyautogui.press('space')
                                elif keyToPrint == "enter":
                                    pyautogui.press('enter')
                                elif keyToPrint == "remove":
                                    pyautogui.press('backspace')
                                else:
                                    pyautogui.typewrite(keyToPrint.lower())

                        finger_extended[fingerAndHandId] = extented_now

                # draw the buttons
                for button in buttons:
                    is_pressed = key_states[button.label]['pressed']
                    is_hovered = key_states[button.label]['hovered']
                    if is_pressed:
                        button.draw(img, pressed=True)  # green
                    elif is_hovered:
                        button.draw(img, (144, 213, 255))
                    else:
                        button.draw(img)
            # calculate frame rate
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            cv2.putText(img, "Calibration: " + str(calibrateddistancefornormalclick) + "   Current: " + str(distanceofthumbandindex),
                        (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            # show image
            cv2.imshow("Gesture Recog", img)

    cap.release() # if it breaks out of the loop - then destroy the window
    cv2.destroyAllWindows()

def WhatFunction(nameoffunction, landmark_list, mousesens, mousesmooth, img, statusgesture, xindex, yindex,
                 xmiddle, ymiddle, xlowerindex, ylowerindex, xthumbtip, ythumbtip, distfornormalclick, distfordragclick,
                 prevLocX, prevLocY, frameR, wCam, hCam):
    global normalclick
    global rightclick
    global dragclick
    global distanceofthumbandindex
    screenwidth, screenheight = pyautogui.size()  # get resolution of the users

    # calculate x and y positions of the mouse
    xpos = np.interp(xindex, (frameR, wCam - frameR), (0, screenwidth))
    ypos = np.interp(yindex, (frameR, hCam - frameR), (0, screenheight))

    # calculate the distance between the thumb and index and convert it to an integer
    distanceofthumbandindex = CalculateDistanceBetweenPoint(xlowerindex, ylowerindex, xthumbtip, ythumbtip)

    # calculate distance between the index and middle finger and convert to an integer
    distance = CalculateDistanceBetweenPoint(xmiddle, ymiddle, xindex, yindex)

    # x and y positions based on smoothening
    curLocX = prevLocX + (xpos - prevLocX) / (mousesmooth * mousesens)
    curLocY = prevLocY + (ypos - prevLocY) / (mousesmooth * mousesens)
    print("distancebetweenthumbandindex: " + str(distanceofthumbandindex))
    # print("ditsance between index and middle finger: " + str(distance)) - debugging

    # check the name of function to determine the interaction mode
    if nameoffunction == "pointer":
        rightclick = False

        # draw green circle on image at current hand position for visual feedback
        cv2.circle(img, center=(xindex, yindex), radius=10, color=(0, 255, 0))

        # move cursor to the current hand position
        mouse.move(curLocX, curLocY)
        prevLocX, prevLocY = curLocX, curLocY

        # check gesture status for pointer mode
        if statusgesture == "pointer":
            # check for normal click using the calibrated distance that we calculated when the user puts up an open hand
            if distanceofthumbandindex < distfornormalclick:
                # having it here makes it so that this still happens and does not go to the else statement
                if not normalclick:

                    normalclick = True


                    # use mouse library to perform a left click
                    mouse.click()
                    # print("click") - debugging
            else:
                normalclick = False # reset normal click
        # check if to perform a drag click
        elif statusgesture == "drag click":
            if distance < distfordragclick:
                if not normalclick:
                    # check for drag click using the calibrated distance that we calculated when the user puts up an open hand

                    normalclick = True  # makes it so that it won't do the mouse.release function everytime
                    # changed the library to mouse library rather than pyautogui and it is much smoother now

                    mouse.click()
                        # print("click")

            else:  # so that it does not realease the mouse if the part above never even eran

                normalclick = False
    # check the name of function to determine the interaction mode
    elif nameoffunction == "drag click":  # drag clicking
        # draw a green circle on the image at the current hand position
        cv2.circle(img, center=(xindex, yindex), radius=10, color=(0, 255, 0))
        mouse.move(curLocX, curLocY)  # with pyautogui it made fps low so changed

         # to mouse library
        prevLocX, prevLocY = curLocX, curLocY

        # print(distance)
        if statusgesture == "pointer":
            if distanceofthumbandindex < distfornormalclick:  # if distance is less than a certain number
                # coordinates to move mouse. if thumb, index and middle finger are all up and 4th finger is down
                dragclick = True
                mouse.press(button='left')
                # print("click")
            else:
                if dragclick:
                    mouse.release(button='left')
                    dragclick = False
        elif statusgesture == "indexandmiddle":
            if distance < distfordragclick:
                dragclick = True  # makes it so that it won't always do the mouse.release function
                # changed the libraryand it is much smoother now
                mouse.press(button='left')  # holds the mouse down
            else:  # so that it does not realease the mouse if the part above never even eran
                if dragclick:
                    mouse.release(button='left')
                    dragclick = False

    return prevLocX, prevLocY


def whichHand(landmarklist):  # algorithm
    if (landmarklist[20][0] - landmarklist[16][0]) < 0:
        # tip of the pinky finger minus the tip of the 4th finger - if it is negative it means it
        # is your left hand else it is your right had
        return "LEFT"
    else:
        return "RIGHT"


def CalcLandmarkList(image, landmarks):
    img_width, img_height = image.shape[1], image.shape[0]  # gets the width and height of the video screen
    points = []
    # iterate through each landmark detected by mediapipe
    for i, landmark in enumerate(landmarks.landmark):
        landmark_x = int(landmark.x * img_width)
        landmark_y = int(landmark.y * img_height)
        # convert the relative coordinates of the landmarks provided by the Mediapipe library into
        # absolute pixel coordinates on the image

        # append these coordinates into a 2D array
        points.append([landmark_x, landmark_y])
        # each landmark is represented by a pair of x and y coords
        # note: we do not need z point as we do not want to change it / normalise it
    return points


# used to create the dataset that was passed into the neural network
def LoggingHandGestures(normalised_landmark_list):
    # logs the list into a csv file so the neural network can use it to compare and make a prediction
    if mode == 3:
        print("logging")
        gesturespath = 'Model/gestures.csv'
        # opens the path of the gestures folder and makes it writeable - 'a' means opened for appending
        openedfile = open(gesturespath, 'a', newline='') # makes it so that no new line is created

        writer = csv.writer(openedfile)  # opened using csv writer
        writer.writerow([4, *normalised_landmark_list])  # writes the row with a 3 at the beginning
        # The * symbol is used to unpack the array elements into individual values within the row.

        # screenshot of this not working on discord server
        # it still kept overwriting the data so this did not work
        # instead of writing it should be a which means appending

        time.sleep(0.5)


def fingersUp(landmarkList, which_hand, fingersuplist):
    # checks if the tip of the index finger is above the the middle of the index finger
    if landmarkList[8][1] < landmarkList[6][1]:
        fingersuplist[0] = 1 # if it is then set index 0 to 1
    else:
        fingersuplist[0] = 0

    # checks if the tip of the middle finger is above the the middle of the middle finger
    if landmarkList[12][1] < landmarkList[10][1]:
        fingersuplist[1] = 1
    else:
        fingersuplist[1] = 0

    # checks if the tip of the ring finger is above the the middle of the ring finger
    if landmarkList[16][1] < landmarkList[14][1]:
        fingersuplist[2] = 1
    else:
        fingersuplist[2] = 0

    # check if the tip of the little finger is above the middle of little finger
    if landmarkList[20][1] < landmarkList[18][1]:
        fingersuplist[3] = 1
    else:
        fingersuplist[3] = 0

    print(landmarkList[4][1], landmarkList[3][1])

    if which_hand == "RIGHT" and landmarkList[4][0] < landmarkList[5][
        0]:  # Right Thumb
        # checks if the x coord of the tip of the thumb is
        # less than the bottom of the index finger landmark
        fingersuplist[4] = 1
    elif which_hand == "LEFT" and landmarkList[4][0] > landmarkList[5][
        0]:  # Left Thumb
        # checks if the x coord of the tip of the thumb is
        # greater than the bottom of the index finger landmark
        fingersuplist[4] = 1
    else:
        fingersuplist[4] = 0

    return fingersuplist


def normaliseLandmarkList(landmarkList):
    # converting to relative coordinates so i can use it in a neural network
    b_x, b_y = 0, 0  # base values, wrist coordinates (x, y)
    for i, lmk_point in enumerate(landmarkList):
        # i is the index of the current element (lmk_point) in the landmarkList.
        # lmk_point is the actual value of the current element in the landmarkList.
        if i == 0:  # if it is at index (wrist) which is 0 then
            b_x = lmk_point[0]  # represents the base coordinates of the wrists x and y position
            b_y = lmk_point[1]

        landmarkList[i][0] = landmarkList[i][0] - b_x  # gets each x value and subtracts it from the base value of the wrist
        landmarkList[i][1] = landmarkList[i][1] - b_y  # gets each y value
        # this essentially makes all the points relative to the wrist

        # mediapipe will provide 3d coordinates for the landmarks so we will need to flatten them into a 1d vector (2d arrray)
        landmarkList = list(flattenlist(landmarkList))
        max_value = max(list(map(abs, landmarkList)))  # for each element in the landmark list it will do absolute on it

        def normalise_(n):  # local function so can only be used in this function
            return n / max_value  # nested function

        landmarkList = list(map(normalise_, landmarkList))  # applying the normalise function to all of them
        # maps makes all elements do the normalise function
        return landmarkList


def DetectHands(image, handsmodel):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # changes colour of image so it can be processed
    image.flags.writeable = False  # makes it not writeable
    result = handsmodel.process(image) # use mediapipe to process the image
    image.flags.writeable = True  # makes it writeable
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # change colour back to orginal
    return image, result # return image and processed result


def WhichGesture(scrollspeed, option):
    if option == "scroll up":
        mouse.wheel(delta=1 * scrollspeed) # use the mouse library to perform the scroll up
    else:
        mouse.wheel(delta=-1 * scrollspeed)


def CalulateHandSize(landmarklist): # calculates the sie of the hand
    # only do if the gesture is the open hand
    if landmarklist is None: # if nothing in landmark list
        return None

    wristx, wristy = landmarklist[0][0], landmarklist[0][1] # coordinates from the wrist (x and y, no z)
    middletipx, middletipy = landmarklist[12][0], landmarklist[12][1] # coordinates for the tip of the middle finger

    size = math.sqrt((wristx - wristy) ** 2 + (middletipx - middletipy) ** 2) # calculate size using those coords
    print("size: " + str(size)) # debugging
    return size # returns the size because it is a function


def flattenlist(iterableList):  # ALGORITHM
    for it in iterableList:
        for element in it:
            yield element

def CalculateDistanceBetweenPoint(xpoint1, ypoint1, xpoint2, ypoint2):
    return int(math.sqrt(((xpoint1 - xpoint2) ** 2) + ((ypoint1 - ypoint2) ** 2)))


# keyboard functions
def is_finger_extended(hand_landmarks, fingertip_id, handedness):
    if fingertip_id == 4:  # Thumb
        if handedness == "Right":
            return hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x
        else:  # Left thumb is mirrored
            return hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x
    else:
        # For other fingers: tip above the joint → extended
        return hand_landmarks.landmark[fingertip_id].y < hand_landmarks.landmark[fingertip_id - 2].y



root = Tk()

MainWindow = Main(root) # starts here

root.mainloop()
