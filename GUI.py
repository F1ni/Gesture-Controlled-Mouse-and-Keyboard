from tkinter import *

class Main:
    def __init__(self, main):
        self.buttonframe = Frame(main)

        self.StartButton = Button(self.buttonframe, text="Start", padx=20, pady=10)
        self.StartButton.grid(row=0, column=0, columnspan=1, sticky=W+E, padx=10, pady=10)

        self.StopButton = Button(self.buttonframe, text="Stop", padx=20, pady=10)
        self.StopButton.grid(row=1, column=0, columnspan=1, sticky=W+E, padx=10, pady=10)

        self.InstructionsPageButton = Button(self.buttonframe, text="Instructions", padx=20, pady=10, command=self.OpenInstructionsWindow)
        self.InstructionsPageButton.grid(row=2, column=0, padx=10, pady=10, sticky=W+E)

        self.GestureSettingsPageButton = Button(self.buttonframe, text="Gesture Settings", command=self.OpenGestureSettingsWindow, padx=20, pady=10)
        self.GestureSettingsPageButton.grid(row=3, column=0, padx=10, pady=10, sticky=W+E)

        self.MouseSettingsPageButton = Button(self.buttonframe, text="Mouse Settings", command=self.OpenMouseSettingsWindow,padx=20, pady=10)

        self.MouseSettingsPageButton.grid(row=4, column=0, padx=10, pady=10, sticky=W+E)

        self.buttonframe.grid(row=0, column=0, sticky=N+S)


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
        self.frame = Frame(gesturesettingswindow)

        self.label1 = Label(gesturesettingswindow, text="Gesture Settings here")
        self.label1.pack(padx=10, pady=10)

        self.frame.pack()


class MouseSettingsWindow:
    def __init__(self):
        mousesettingswindow = Toplevel()
        self.frame = Frame(mousesettingswindow)

        self.label1 = Label(mousesettingswindow, text="Mouse Settings here")
        self.label1.pack(padx=10, pady=10)

        self.frame.pack()

class InstructionsWindow:
    def __init__(self):
        instructionsWindow = Toplevel()
        self.frame = Frame(instructionsWindow)

        self.label1 = Label(instructionsWindow, text="Instructions here")
        self.label1.pack(padx=10, pady=10)

        self.frame.pack()


root = Tk()
root.configure(bg="#27374D")
root.geometry("700x500")
MainWindow = Main(root)
root.mainloop()
