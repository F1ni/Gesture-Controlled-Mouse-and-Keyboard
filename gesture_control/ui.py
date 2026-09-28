"""Accessible Tkinter control panel for the camera-based application."""

import queue
import tkinter as tk
from tkinter import messagebox, ttk

from .config import Settings, load_settings, save_settings
from .engine import ControlEngine, Feedback


BG = "#f4f7f8"
SURFACE = "#ffffff"
INK = "#172a33"
MUTED = "#4e646d"
ACCENT = "#075e65"
ALERT = "#a52a35"


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Gesture Control · Hands-free computer access")
        self.root.geometry("980x720")
        self.root.minsize(760, 610)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.engine: ControlEngine | None = None
        self.settings = load_settings()
        self._style()
        self._variables()
        self._layout()
        self.root.bind("<Escape>", lambda _event: self.stop())
        self.root.bind("<Control-o>", lambda _event: self.start())
        self.root.bind("o", lambda _event: self.start())
        self.root.after(80, self._poll)

    def _style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=SURFACE)
        style.configure("TLabel", background=BG, foreground=INK, font=("Segoe UI", 11))
        style.configure("Card.TLabel", background=SURFACE, foreground=INK, font=("Segoe UI", 11))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Hero.TLabel", background=BG, foreground=INK, font=("Segoe UI Semibold", 22))
        style.configure("Section.TLabel", background=BG, foreground=INK, font=("Segoe UI Semibold", 14))
        style.configure("Value.TLabel", background=SURFACE, foreground=INK, font=("Segoe UI Semibold", 16))
        style.configure("TButton", font=("Segoe UI Semibold", 11), padding=(16, 10))
        style.configure("Primary.TButton", background=ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", "#054a50"), ("disabled", "#9aafb2")])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI Semibold", 11), padding=(22, 12))
        style.configure("TCombobox", font=("Segoe UI", 11), padding=5)

    def _variables(self) -> None:
        s = self.settings
        self.sensitivity = tk.IntVar(value=s.sensitivity)
        self.smoothness = tk.IntVar(value=s.smoothness)
        self.scroll_speed = tk.IntVar(value=s.scrollingspeed)
        self.camera_index = tk.IntVar(value=s.camera_index)
        self.top_view = tk.IntVar(value=s.topviewvalue)
        self.pointer = tk.StringVar(value=s.pointer)
        self.drag_click = tk.StringVar(value=s.drag_click)
        self.scroll_up = tk.StringVar(value=s.scroll_up)
        self.scroll_down = tk.StringVar(value=s.scroll_down)
        self.camera_status = tk.StringVar(value="Disconnected")
        self.mode_status = tk.StringVar(value="Idle")
        self.gesture_status = tk.StringVar(value="—")
        self.action_status = tk.StringVar(value="—")
        self.calibration_status = tk.StringVar(value="Not calibrated")
        self.control_status = tk.StringVar(value="Control paused")

    def _layout(self) -> None:
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Gesture Control", style="Hero.TLabel").pack(anchor="w")
        ttk.Label(container, text="Hands-free mouse and keyboard control through your camera",
                  style="Muted.TLabel").pack(anchor="w", pady=(2, 16))
        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True)
        dashboard = ttk.Frame(notebook, padding=(8, 20))
        controls = ttk.Frame(notebook, padding=(8, 20))
        guide = ttk.Frame(notebook, padding=(8, 20))
        notebook.add(dashboard, text="Overview")
        notebook.add(controls, text="Controls & settings")
        notebook.add(guide, text="How to use")
        self._dashboard(dashboard)
        self._controls(controls)
        self._guide(guide)
        footer = ttk.Frame(container)
        footer.pack(fill="x", pady=(14, 0))
        ttk.Label(footer, text="O or Ctrl+O  Start     Esc  Stop quickly", style="Muted.TLabel").pack(side="left")
        ttk.Label(footer, text="Camera preview opens in a separate window", style="Muted.TLabel").pack(side="right")

    def _dashboard(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Tracking", style="Section.TLabel").pack(anchor="w", pady=(0, 12))
        action_row = ttk.Frame(parent)
        action_row.pack(fill="x")
        self.start_button = ttk.Button(action_row, text="Start control", style="Primary.TButton", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(action_row, text="Stop control", command=self.stop, state="disabled")
        self.stop_button.pack(side="left", padx=(12, 0))
        ttk.Label(action_row, textvariable=self.control_status, style="Muted.TLabel").pack(side="left", padx=20)

        grid = ttk.Frame(parent)
        grid.pack(fill="x", pady=(25, 15))
        for column in range(2):
            grid.columnconfigure(column, weight=1)
        for row, (label, variable) in enumerate((
            ("Camera", self.camera_status), ("Control mode", self.mode_status),
            ("Gesture seen", self.gesture_status), ("Action", self.action_status),
        )):
            card = ttk.Frame(grid, style="Card.TFrame", padding=17)
            card.grid(row=row // 2, column=row % 2, sticky="nsew", padx=5, pady=5)
            ttk.Label(card, text=label, style="Card.TLabel").pack(anchor="w")
            ttk.Label(card, textvariable=variable, style="Value.TLabel", wraplength=340).pack(anchor="w", pady=(5, 0))

        ttk.Label(parent, text="Recent actions", style="Section.TLabel").pack(anchor="w", pady=(8, 8))
        self.history = tk.Listbox(parent, height=5, font=("Segoe UI", 11),
                                  bg=SURFACE, fg=INK, selectbackground=ACCENT,
                                  relief="flat", highlightthickness=1,
                                  highlightbackground="#d5e1e4", activestyle="none")
        self.history.pack(fill="x")
        self.history.insert("end", "No gestures recognised yet")
        ttk.Label(parent, textvariable=self.calibration_status, style="Muted.TLabel").pack(anchor="w", pady=(12, 0))

    def _controls(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Movement & camera", style="Section.TLabel").pack(anchor="w", pady=(0, 12))
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(fill="x")
        for row, (label, variable, low, high) in enumerate((
            ("Sensitivity", self.sensitivity, 1, 10),
            ("Smoothness", self.smoothness, 1, 10),
            ("Scroll speed", self.scroll_speed, 1, 5),
        )):
            ttk.Label(settings_frame, text=label, width=20).grid(row=row, column=0, sticky="w", pady=7)
            scale = tk.Scale(settings_frame, variable=variable, from_=low, to=high,
                             orient="horizontal", length=300, showvalue=True,
                             bg=BG, fg=INK, highlightthickness=0, troughcolor="#d5e1e4")
            scale.grid(row=row, column=1, sticky="w", padx=10)
        ttk.Label(settings_frame, text="Camera index", width=20).grid(row=3, column=0, sticky="w", pady=7)
        tk.Spinbox(settings_frame, from_=0, to=9, textvariable=self.camera_index, width=5,
                   font=("Segoe UI", 11)).grid(row=3, column=1, sticky="w", padx=10)
        ttk.Checkbutton(settings_frame, text="Top-view camera (do not mirror image)",
                        variable=self.top_view).grid(row=4, column=0, columnspan=2, sticky="w", pady=10)

        ttk.Separator(parent).pack(fill="x", pady=16)
        ttk.Label(parent, text="Gesture mappings", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(parent, text="Mappings take effect the next time control starts.",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 8))
        mapping_frame = ttk.Frame(parent)
        mapping_frame.pack(fill="x")
        for row, (label, variable, choices) in enumerate((
            ("Pointer pose", self.pointer, ("pointer", "drag click")),
            ("Index + middle pose", self.drag_click, ("pointer", "drag click")),
            ("Learned scroll pose 1", self.scroll_up, ("scroll up", "scroll down")),
            ("Learned scroll pose 2", self.scroll_down, ("scroll up", "scroll down")),
        )):
            ttk.Label(mapping_frame, text=label, width=25).grid(row=row, column=0, sticky="w", pady=5)
            ttk.Combobox(mapping_frame, textvariable=variable, values=choices,
                         state="readonly", width=22).grid(row=row, column=1, sticky="w", padx=10)
        buttons = ttk.Frame(parent)
        buttons.pack(anchor="w", pady=18)
        ttk.Button(buttons, text="Save settings", style="Primary.TButton", command=self.save).pack(side="left")
        ttk.Button(buttons, text="Restore defaults", command=self.defaults).pack(side="left", padx=12)

    def _guide(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Getting started", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        for line in (
            "1. Connect a camera and choose its index under Controls & settings.",
            "2. Select Start control or press O / Ctrl+O. The camera preview opens separately.",
            "3. Show one hand for mouse control; show two hands for the virtual keyboard.",
            "4. Show an open hand to calibrate after moving closer to or farther from the camera.",
            "5. Press Esc in either window or select Stop control to pause immediately.",
        ):
            ttk.Label(parent, text=line, wraplength=850).pack(anchor="w", pady=3)
        ttk.Separator(parent).pack(fill="x", pady=18)
        ttk.Label(parent, text="Gestures", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        for line in (
            "Thumb + index raised → move the pointer; bring thumb toward index to click.",
            "Thumb + index + middle raised → move and hold left click by bringing middle toward index.",
            "Thumb + index + little finger raised → right click once per pose.",
            "Model-recognised scroll poses → scroll up or down; directions can be swapped.",
            "Two hands → hover over a drawn key, then bend the finger to type it.",
            "Middle finger alone → closes the active window with Alt+F4. Use with care.",
        ):
            ttk.Label(parent, text=line, wraplength=850).pack(anchor="w", pady=3)
        ttk.Label(parent, text="The virtual keyboard includes letters, Space, Enter and Backspace.",
                  style="Muted.TLabel").pack(anchor="w", pady=(14, 0))

    def _current_settings(self) -> Settings:
        settings = Settings(sensitivity=self.sensitivity.get(), smoothness=self.smoothness.get(),
                            scrollingspeed=self.scroll_speed.get(), pointer=self.pointer.get(),
                            drag_click=self.drag_click.get(), scroll_up=self.scroll_up.get(),
                            scroll_down=self.scroll_down.get(), topviewvalue=self.top_view.get(),
                            camera_index=self.camera_index.get())
        settings.validate()
        return settings

    def save(self) -> None:
        try:
            self.settings = self._current_settings()
            save_settings(self.settings)
        except (ValueError, OSError, tk.TclError) as exc:
            messagebox.showerror("Settings could not be saved", str(exc), parent=self.root)
            return
        self.control_status.set("Settings saved")

    def defaults(self) -> None:
        default = Settings()
        for variable, value in ((self.sensitivity, default.sensitivity),
                                (self.smoothness, default.smoothness),
                                (self.scroll_speed, default.scrollingspeed),
                                (self.camera_index, default.camera_index),
                                (self.top_view, default.topviewvalue),
                                (self.pointer, default.pointer),
                                (self.drag_click, default.drag_click),
                                (self.scroll_up, default.scroll_up),
                                (self.scroll_down, default.scroll_down)):
            variable.set(value)
        self.control_status.set("Defaults selected · Save settings to keep them")

    def start(self) -> None:
        if self.engine and self.engine.thread and self.engine.thread.is_alive():
            return
        try:
            settings = self._current_settings()
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Invalid settings", str(exc), parent=self.root)
            return
        self.engine = ControlEngine(settings,
                                    lambda feedback: self.events.put(("feedback", feedback)),
                                    lambda error: self.events.put(("error", error)),
                                    lambda: self.events.put(("done", None)))
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.control_status.set("Starting camera…")
        self.camera_status.set("Connecting…")
        self.engine.start()

    def stop(self) -> None:
        if self.engine:
            self.engine.stop()
            self.control_status.set("Stopping control…")

    def _poll(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "feedback":
                    feedback: Feedback = payload
                    self.camera_status.set(feedback.camera)
                    self.mode_status.set(feedback.mode)
                    self.gesture_status.set(feedback.gesture)
                    self.action_status.set(feedback.action)
                    self.calibration_status.set(f"Click calibration: {feedback.calibration} px")
                    self.control_status.set("Control active")
                    self.history.delete(0, "end")
                    for item in feedback.history or ("No gestures recognised yet",):
                        self.history.insert("end", item)
                elif kind == "error":
                    self.control_status.set("Control stopped after an error")
                    messagebox.showerror("Gesture Control", str(payload), parent=self.root)
                elif kind == "done":
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.camera_status.set("Disconnected")
                    self.mode_status.set("Idle")
                    if self.control_status.get() != "Control stopped after an error":
                        self.control_status.set("Control paused")
        except queue.Empty:
            pass
        self.root.after(80, self._poll)

    def close(self) -> None:
        self.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    try:
        App(root)
    except ValueError as exc:
        messagebox.showerror("Gesture Control settings", str(exc), parent=root)
        root.destroy()
        return
    root.mainloop()
