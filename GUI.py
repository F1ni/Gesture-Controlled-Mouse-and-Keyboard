from tkinter import *
from PIL import Image, ImageTk

backgroundcolor = "#B4B4B4"
textcolor = "#FFFFFF"
buttoncolor = "#636363"


class Main:
    def __init__(self, main):
        self.buttonframe = Frame(main, bg=backgroundcolor)

        self.StartButton = Button(self.buttonframe, text="Start", padx=20, pady=10, bg=buttoncolor, fg=textcolor)
        self.StartButton.grid(row=0, column=0, columnspan=1, sticky=W + E, padx=10, pady=10)

        self.StopButton = Button(self.buttonframe, text="Stop", padx=20, pady=10, bg=buttoncolor, fg=textcolor)
        self.StopButton.grid(row=1, column=0, columnspan=1, sticky=W + E, padx=10, pady=10)

        self.InstructionsPageButton = Button(self.buttonframe, text="Instructions", padx=20, pady=10, bg=buttoncolor
                                             , fg=textcolor, command=self.OpenInstructionsWindow)
        self.InstructionsPageButton.grid(row=2, column=0, padx=10, pady=10, sticky=W + E)

        self.GestureSettingsPageButton = Button(self.buttonframe, text="Gesture Settings", bg=buttoncolor, fg=textcolor,
                                                command=self.OpenGestureSettingsWindow, padx=20, pady=10)
        self.GestureSettingsPageButton.grid(row=3, column=0, padx=10, pady=10, sticky=W + E)

        self.MouseSettingsPageButton = Button(self.buttonframe, text="Mouse Settings", bg=buttoncolor, fg=textcolor,
                                              command=self.OpenMouseSettingsWindow, padx=20, pady=10)

        self.MouseSettingsPageButton.grid(row=4, column=0, padx=10, pady=10, sticky=W + E)

        self.buttonframe.grid(row=0, column=0, sticky=N + S)

        # video frame
        self.VideoFrame = Frame(main)
        self.label = Label(self.VideoFrame, text="Video shown here", padx=10, pady=10)
        self.label.grid(row=0, column=0)
        self.VideoFrame.grid(row=0, column=1)

    def OpenGestureSettingsWindow(self):
        gesturesettingsWindow = GestureSettingsWindow()

    def OpenMouseSettingsWindow(self):
        mousesettingsWindow = MouseSettingsWindow(self.UpdateMouseSettings)

    def OpenInstructionsWindow(self):
        instructionsWindow = InstructionsWindow()

    def UpdateMouseSettings(self):
        pass


class GestureSettingsWindow:
    def __init__(self):
        global pointerimage
        global dragclickimage
        global rightclickimage
        global scrollupimage
        global scrolldownimage

        gesturesettingswindow = Toplevel(bg=backgroundcolor)
        gesturesettingswindow.title("Gesture Settings")

        gesturesettingswindow.geometry("700x500")

        self.gesturelist = [
            "scroll up",
            "scroll down",
            "pointer",
            "drag click",
            "right click"
        ]

        # frame 1 -------------------------------------------------------------
        self.gestureframe1 = Frame(gesturesettingswindow)
        self.pointerlabel = Label(self.gestureframe1, text="Pointer")
        self.pointerlabel.grid(row=0, column=0, padx=10, pady=10)
        # show image
        pointerimage = Image.open("Photos/pointer.jpg").resize((150, 155))
        pointerimageTK = ImageTk.PhotoImage(pointerimage)
        pointerimagelabel = Label(self.gestureframe1, image=pointerimageTK)
        pointerimagelabel.grid(row=1, column=0)
        pointerimage.image = pointerimageTK

        # dropdown
        self.option1 = StringVar()
        self.option1.set(self.gesturelist[2])
        self.dropdown1 = OptionMenu(self.gestureframe1, self.option1, *self.gesturelist)
        self.dropdown1.grid(row=2, column=0)
        self.gestureframe1.grid(row=0, column=0, padx=10, pady=10)

        # frame 2 ---------------------------------------------------------------
        self.gestureframe2 = Frame(gesturesettingswindow)
        self.dragclicklabel = Label(self.gestureframe2, text="Drag Click")
        self.dragclicklabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        dragclickimage = Image.open("Photos/dragclick.jpg").resize((150, 155))
        dragclickimageTk = ImageTk.PhotoImage(dragclickimage)
        dragclickimagelabel = Label(self.gestureframe2, image=dragclickimageTk)
        dragclickimagelabel.grid(row=1, column=0)
        dragclickimage.image = dragclickimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option2 = StringVar()
        self.option2.set(self.gesturelist[3])
        self.dropdown2 = OptionMenu(self.gestureframe2, self.option2, *self.gesturelist)
        self.dropdown2.grid(row=2, column=0)
        self.gestureframe2.grid(row=0, column=1, padx=10, pady=10)

        # frame 3 ---------------------------------------------------------------
        self.gestureframe3 = Frame(gesturesettingswindow)
        self.rightclicklabel = Label(self.gestureframe3, text="Right Click")
        self.rightclicklabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        rightclickimage = Image.open("Photos/rightclick.jpg").resize((150, 155))
        rightclickimageTk = ImageTk.PhotoImage(rightclickimage)
        rightclickimagelabel = Label(self.gestureframe3, image=rightclickimageTk)
        rightclickimagelabel.grid(row=1, column=0)
        rightclickimage.image = rightclickimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option3 = StringVar()
        self.option3.set(self.gesturelist[4])
        self.dropdown3 = OptionMenu(self.gestureframe3, self.option3, *self.gesturelist)
        self.dropdown3.grid(row=2, column=0)
        self.gestureframe3.grid(row=0, column=2, padx=10, pady=10)

        # frame 4 ---------------------------------------------------------------
        self.gestureframe4 = Frame(gesturesettingswindow)
        self.scrolluplabel = Label(self.gestureframe4, text="Scroll Up")
        self.scrolluplabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        scrollupimage = Image.open("Photos/scroll up.jpg").resize((150, 155))
        scrollupimageTk = ImageTk.PhotoImage(scrollupimage)
        scrollupimagelabel = Label(self.gestureframe4, image=scrollupimageTk)
        scrollupimagelabel.grid(row=1, column=0)
        scrollupimage.image = scrollupimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option4 = StringVar()
        self.option4.set(self.gesturelist[0])
        self.dropdown4 = OptionMenu(self.gestureframe4, self.option4, *self.gesturelist)
        self.dropdown4.grid(row=2, column=0)
        self.gestureframe4.grid(row=0, column=3, padx=10, pady=10)

        # frame 5 ---------------------------------------------------------------
        self.gestureframe5 = Frame(gesturesettingswindow)
        self.scrolldownlabel = Label(self.gestureframe5, text="Scroll Down")
        self.scrolldownlabel.grid(row=0, column=0, padx=10, pady=10)

        # show image
        scrolldownimage = Image.open("Photos/scroll up.jpg").resize((150, 155))
        scrolldownimageTk = ImageTk.PhotoImage(scrolldownimage)
        scrolldownimagelabel = Label(self.gestureframe5, image=scrolldownimageTk)
        scrolldownimagelabel.grid(row=1, column=0)
        scrolldownimage.image = scrolldownimageTk  # keep a reference to the image or something???
        # something called garbage collection or something???

        # dropdown
        self.option5 = StringVar()
        self.option5.set(self.gesturelist[1])
        self.dropdown5 = OptionMenu(self.gestureframe5, self.option5, *self.gesturelist)
        self.dropdown5.grid(row=2, column=0)
        self.gestureframe5.grid(row=1, column=0, padx=10, pady=10)

        # back button -----------------------------------------------------------------
        self.backbutton = Button(gesturesettingswindow, text="BACK", bg=buttoncolor, fg=textcolor,
                                 command=lambda: self.Back(gesturesettingswindow))
        self.backbutton.grid(row=1, column=2)

    def Back(self, window):
        # submitting data back to main menu screen
        window.destroy()


class MouseSettingsWindow:
    def __init__(self, updatefunction):
        mousesettingswindow = Toplevel(bg=backgroundcolor)
        mousesettingswindow.geometry("700x500")
        mousesettingswindow.title("Mouse Settings")
        self.updatemousesettingsfunction = updatefunction

        # Title
        self.titleLabel = Label(mousesettingswindow, text="Mouse Settings", font=10, bg=backgroundcolor)
        self.titleLabel.grid(row=0, column=0, columnspan=2, sticky='ew')

        # SENSTIVITY FRAME
        self.sensitvityframe = Frame(mousesettingswindow)

        self.sensitivityLabel = Label(self.sensitvityframe, text="Sensitivity:")
        self.sensitivityLabel.pack()

        # Sensitivity Slider
        self.sensitivityslider = Scale(self.sensitvityframe, orient=HORIZONTAL, from_=1, to=10, length=500)
        self.sensitivityslider.set(1)
        self.sensitivityslider.pack()

        self.sensitvityframe.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

        # SMOOTHNESS FRAME ----------------------------------------------------------------------------
        self.smoothnessframe = Frame(mousesettingswindow)
        self.smoothnesslabel = Label(self.smoothnessframe, text="Smoothness:")
        self.smoothnesslabel.pack()

        # Sensitivity Slider
        self.smoothSlider = Scale(self.smoothnessframe, orient=HORIZONTAL, from_=1, to=10, length=500)
        self.smoothSlider.set(4)
        self.smoothSlider.pack()

        self.smoothnessframe.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # SCROLLING SPEED FRAME ----------------------------------------------------------------------------
        self.scrollingframe = Frame(mousesettingswindow)
        self.scrollinglabel = Label(self.scrollingframe, text="Scrolling Speed:")
        self.scrollinglabel.pack()

        # Sensitivity Slider
        self.scrollSlider = Scale(self.scrollingframe, orient=HORIZONTAL, from_=1, to=5, length=500)
        self.scrollSlider.set(2)
        self.scrollSlider.pack()
        self.scrollingframe.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # back button

        self.backbutton = Button(mousesettingswindow, text="BACK", bg=buttoncolor, fg=textcolor,
                                 command=lambda: self.Back(mousesettingswindow))
        self.backbutton.grid(row=4, column=0)


    def Back(self, window):
        # submitting data back through main menu screen
        self.updatemousesettingsfunction()
        window.destroy()


class InstructionsWindow:
    def __init__(self):
        instructionsWindow = Toplevel()
        instructionsWindow.title("Instructions")
        instructionsWindow.geometry("700x500")
        self.instructionsframe = Frame(instructionsWindow)

        # store text in a separate text file or variable
        self.label1 = Label(self.instructionsframe, text="Instructions here")
        self.label1.pack(padx=10, pady=10)
        # more photos of the gestures here to explain how to use the program

        self.instructionsframe.pack()


root = Tk()
root.configure(bg=backgroundcolor)
root.title("Hand Gesture Application")
root.geometry("700x500")
MainWindow = Main(root)
root.mainloop()
