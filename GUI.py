from tkinter import *
from PIL import Image, ImageTk
# import mainv2 as mainscript
import threading

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
    # def Start(self):
    #     if self.thread is None or not self.thread.is_alive():
    #         mainscript.isStopped = False
    #         self.thread = threading.Thread(target=mainscript.MainFunction)
    #         self.thread.start()
    #
    # def Stop(self):
    #     # mainscript.isStopped = True
    #     if self.thread and self.thread.is_alive():
    #         mainscript.isStopped = True  # Assuming you have this global flag
    #         self.thread.join()

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
        scrolldownimage = Image.open("Photos/scroll up.jpg").resize((150, 155))
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
        gestureframe5.grid(row=1, column=0, padx=10, pady=10)

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
