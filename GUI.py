from tkinter import *

backgroundcolor = "#B4B4B4"
textcolor = "#FFFFFF"


class Main:
    def __init__(self, main):
        self.buttonframe = Frame(main, bg=backgroundcolor)

        self.StartButton = Button(self.buttonframe, text="Start", padx=20, pady=10, bg="#636363", fg=textcolor)
        self.StartButton.grid(row=0, column=0, columnspan=1, sticky=W + E, padx=10, pady=10)

        self.StopButton = Button(self.buttonframe, text="Stop", padx=20, pady=10, bg="#636363", fg=textcolor)
        self.StopButton.grid(row=1, column=0, columnspan=1, sticky=W + E, padx=10, pady=10)

        self.InstructionsPageButton = Button(self.buttonframe, text="Instructions", padx=20, pady=10, bg="#636363"
                                             , fg=textcolor, command=self.OpenInstructionsWindow)
        self.InstructionsPageButton.grid(row=2, column=0, padx=10, pady=10, sticky=W + E)

        self.GestureSettingsPageButton = Button(self.buttonframe, text="Gesture Settings", bg="#636363", fg=textcolor,
                                                command=self.OpenGestureSettingsWindow, padx=20, pady=10)
        self.GestureSettingsPageButton.grid(row=3, column=0, padx=10, pady=10, sticky=W + E)

        self.MouseSettingsPageButton = Button(self.buttonframe, text="Mouse Settings", bg="#636363", fg=textcolor,
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
        mousesettingsWindow = MouseSettingsWindow()

    def OpenInstructionsWindow(self):
        instructionsWindow = InstructionsWindow()


class GestureSettingsWindow:
    def __init__(self):
        gesturesettingswindow = Toplevel()
        gesturesettingswindow.title("Gesture Settings")
        self.gesturesettingsframe = Frame(gesturesettingswindow)
        gesturesettingswindow.geometry("700x500")

        self.gesturelist = [
            "scroll up",
            "scroll down",
            "pointer",
            "drag click",
            "right click"
        ]
        self.gesturesettingstitlelabel = Label(self.gesturesettingsframe, text="Gesture Settings here")
        self.gesturesettingstitlelabel.pack(padx=10, pady=10)

        self.option1 = StringVar()
        self.dropdown1 = OptionMenu(self.gesturesettingsframe, self.option1, *self.gesturelist)
        self.dropdown1.pack()

        self.gesturesettingsframe.pack()


class MouseSettingsWindow:
    def __init__(self):
        mousesettingswindow = Toplevel(bg=backgroundcolor)
        mousesettingswindow.geometry("700x500")
        mousesettingswindow.title("Mouse Settings")

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

        self.frame.pack()


root = Tk()
root.configure(bg=backgroundcolor)
root.title("Hand Gesture Application")
root.geometry("700x500")
MainWindow = Main(root)
root.mainloop()
