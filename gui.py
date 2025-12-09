import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import turtle
import re
import os

from src.lexer import tokenize
from src.parser import Parser
from src.interpreter import Interpreter
from src.turtle_core import MockTurtle
from src.visitors import MementoVisitor, DistanceVisitor
from src.framework_integration import RealTurtleAdapter

# ===================== Theme & Colors =====================
DARK_BG = "#1e1e1e"
DARK_FG = "#d4d4d4"
TURTLE_COLOR = '#008000'
HIGHLIGHT = "#569cd6"
NUMBER_COLOR = "#b5cea8"
KEYWORDS = ["REPEAT", "FORWARD", "FD", "RIGHT", "RT", "LEFT", "LT", "PENUP", "PENDOWN"]

# ===================== Custom Code Editor =====================
class CodeEditor(ScrolledText):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg=DARK_BG, fg=DARK_FG, insertbackground="white", font=("Consolas", 12), undo=True)
        self.bind("<<Modified>>", self.on_change)
        self.highlight_pattern = re.compile(r"\b(" + "|".join(KEYWORDS) + r")\b", re.IGNORECASE)

    def on_change(self, event=None):
        self.tag_remove("keyword", "1.0", tk.END)
        self.tag_remove("number", "1.0", tk.END)

        text = self.get("1.0", tk.END)
        for m in self.highlight_pattern.finditer(text):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.tag_add("keyword", start, end)

        for m in re.finditer(r"\b\d+(\.\d+)?\b", text):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.tag_add("number", start, end)

        self.tag_config("keyword", foreground=HIGHLIGHT)
        self.tag_config("number", foreground=NUMBER_COLOR)
        self.edit_modified(False)

# ===================== Zoom & Pan Canvas =====================
class ZoomPanCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scale_factor = 1.0
        self.bind("<ButtonPress-1>", self.start_pan)
        self.bind("<B1-Motion>", self.do_pan)
        self.bind("<MouseWheel>", self.zoom)  # Windows
        self.bind("<Button-4>", self.zoom)    # Linux scroll up
        self.bind("<Button-5>", self.zoom)    # Linux scroll down
        self.pan_start = None

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def do_pan(self, event):
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]
        self.scan_dragto(-dx, -dy, gain=1)
        self.pan_start = (event.x, event.y)

    def zoom(self, event):
        factor = 1.1 if getattr(event, 'delta', 0) > 0 else 0.9
        self.scale_factor *= factor
        self.scale("all", event.x, event.y, factor, factor)

# ===================== Export Utilities =====================
def export_canvas_png(canvas, filename="turtle_output.png"):
    try:
        from PIL import ImageGrab
        canvas.update()
        x = canvas.winfo_rootx()
        y = canvas.winfo_rooty()
        w = x + canvas.winfo_width()
        h = y + canvas.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, w, h))
        img.save(filename)
        messagebox.showinfo("Export PNG", f"Saved {filename}")
    except Exception as e:
        messagebox.showerror("Export PNG Error", str(e))

# ===================== Main GUI =====================
class TurtleIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Turtle Language IDE")
        self.geometry("1200x750")
        self.configure(bg=DARK_BG)

        self.mementos = []
        self.step_index = 0

        self.create_layout()

    # ---------------- Layout ----------------
    def create_layout(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Editor
        editor_frame = tk.Frame(self, bg=DARK_BG)
        editor_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        editor_frame.rowconfigure(1, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        tk.Label(editor_frame, text="Program Editor", bg=DARK_BG, fg=DARK_FG, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.editor = CodeEditor(editor_frame)
        self.editor.grid(row=1, column=0, sticky="nsew")
        btn_frame = tk.Frame(editor_frame, bg=DARK_BG)
        btn_frame.grid(row=2, column=0, pady=4, sticky="w")
        ttk.Button(btn_frame, text="Run", command=self.run_program).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Step", command=self.step_program).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Reset", command=self.reset_steps).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Load File", command=self.load_file).grid(row=0, column=3, padx=2)
        ttk.Button(btn_frame, text="Save File", command=self.save_file).grid(row=0, column=4, padx=2)

        # Canvas + Stats
        canvas_frame = tk.Frame(self, bg=DARK_BG)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        canvas_frame.rowconfigure(0, weight=3)
        canvas_frame.rowconfigure(1, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        tk.Label(canvas_frame, text="Canvas", bg=DARK_BG, fg=DARK_FG, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.tk_canvas = ZoomPanCanvas(canvas_frame, width=700, height=550, bg="white")
        self.tk_canvas.grid(row=0, column=0, sticky="nsew")
        self.screen = turtle.TurtleScreen(self.tk_canvas)
        self.screen.tracer(0)

        # Create a RawTurtle as the "turtle icon"
        self.real_turtle = turtle.RawTurtle(self.screen)
        self.real_turtle.shape("turtle")
        self.real_turtle.showturtle()
        self.real_turtle.speed(0)
        self.real_turtle.color(TURTLE_COLOR)

        # Stats Panel
        stats_frame = tk.Frame(canvas_frame, bg=DARK_BG)
        stats_frame.grid(row=1, column=0, sticky="nsew", pady=6)
        tk.Label(stats_frame, text="Execution Info", bg=DARK_BG, fg=DARK_FG, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.status_label = tk.Label(stats_frame, text="Status: Ready", bg=DARK_BG, fg=DARK_FG)
        self.status_label.grid(row=1, column=0, sticky="w")
        self.distance_label = tk.Label(stats_frame, text="Distance: 0", bg=DARK_BG, fg=DARK_FG)
        self.distance_label.grid(row=2, column=0, sticky="w")
        self.step_label = tk.Label(stats_frame, text="Step: 0 / 0", bg=DARK_BG, fg=DARK_FG)
        self.step_label.grid(row=3, column=0, sticky="w")

        ttk.Button(stats_frame, text="Export PNG", command=lambda: export_canvas_png(self.tk_canvas)).grid(row=4, column=0, pady=2, sticky="w")

    # ---------------- File I/O ----------------
    def load_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not f: return
        with open(f) as file:
            self.editor.delete("1.0", tk.END)
            self.editor.insert(tk.END, file.read())

    def save_file(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt")
        if not f: return
        with open(f, "w") as file:
            file.write(self.editor.get("1.0", tk.END))

    # ---------------- Parsing ----------------
    def parse_program(self):
        source = self.editor.get("1.0", tk.END)
        tokens = tokenize(source)
        parser = Parser(tokens)
        return parser.parse()

    # ---------------- Run ----------------
    def run_program(self):
        self.status_label.config(text="Status: Running...")
        self.real_turtle.reset()
        self.real_turtle.color(TURTLE_COLOR)
        self.screen.update()

        try:
            program = self.parse_program()
            adapter = RealTurtleAdapter(self.real_turtle)
            interp = Interpreter(adapter)

            # Run step by step using after() for main-thread safety
            self._run_program_steps(interp, program, 0)
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")

    def _run_program_steps(self, interp, program, index):
        if index >= len(program):
            self.screen.update()
            self.status_label.config(text="Status: Finished")
            return

        # Execute one statement
        interp.execute_node(program[index])
        self.screen.update()

        # Schedule next statement
        self.after(50, lambda: self._run_program_steps(interp, program, index + 1))

    # ---------------- Step Mode ----------------
    def reset_steps(self):
        self.real_turtle.reset()
        self.real_turtle.color(TURTLE_COLOR)
        self.screen.update()
        self.mementos = []
        self.step_index = 0
        self.distance_label.config(text="Distance: 0")
        self.step_label.config(text="Step: 0 / 0")
        self.status_label.config(text="Status: Steps reset")

    def step_program(self):
        if not self.mementos:
            self.status_label.config(text="Status: Preparing steps...")
            program = self.parse_program()
            visitor = MementoVisitor(MockTurtle())
            distance = DistanceVisitor()
            for stmt in program:
                stmt.accept(visitor)
                stmt.accept(distance)
            self.mementos = visitor.mementos
            self.distance_label.config(text=f"Distance: {distance.total_distance}")

        if self.step_index >= len(self.mementos):
            self.status_label.config(text="Status: No more steps.")
            return

        state = self.mementos[self.step_index]
        self.step_index += 1

        # Apply state
        self.real_turtle.penup()
        self.real_turtle.setpos(state.x, state.y)
        self.real_turtle.setheading(state.heading)
        if state.pen_down: self.real_turtle.pendown()
        self.screen.update()

        self.step_label.config(text=f"Step: {self.step_index} / {len(self.mementos)}")
        self.status_label.config(text="Status: Stepping...")

# ===================== Main =====================
if __name__ == "__main__":
    app = TurtleIDE()
    app.mainloop()
