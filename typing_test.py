import tkinter as tk
import time
from playsound import playsound
import threading

REFERENCE_TEXT = (
    "The quick brown fox jumps over the lazy dog. Typing is a skill that improves with practice. "
    "Accuracy matters more than speed when you're just getting started. Over time, your fingers will "
    "learn the layout of the keyboard, and your typing speed will naturally increase. Remember to keep "
    "your eyes on the screen and not the keyboard. This helps build muscle memory. A consistent rhythm and "
    "proper posture also improve your overall performance. Stay relaxed, and don’t worry about mistakes—"
    "they are part of the learning process. With patience and daily effort, you'll become a faster, more accurate typist."
)

class TypingSpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.geometry("850x300")

        # Theme colors
        self.light_theme = {
            "bg": "#f5f7fa",
            "fg": "#000000",
            "canvas_bg": "#ffffff",
            "text_default": "#ccc",
            "text_correct": "#555",
            "text_incorrect": "red",
            "cursor": "blue",
            "button_bg": "#1976d2",
            "button_fg": "#ffffff"
        }

        self.dark_theme = {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "canvas_bg": "#2e2e2e",
            "text_default": "#888",
            "text_correct": "#ffffff",
            "text_incorrect": "#ff5555",
            "cursor": "#00bfff",
            "button_bg": "#3a3a3a",
            "button_fg": "#ffffff"
        }

        self.current_theme = self.light_theme
        self.time_limit = 60
        self.canvas_font = ("Courier New", 18)
        self.canvas_text_offset = 10

        self.build_typing_screen()

    def apply_theme(self):
        self.root.configure(bg=self.current_theme["bg"])
        if hasattr(self, 'timer_label'):
            self.timer_label.config(bg=self.current_theme["bg"], fg=self.current_theme["fg"])
        if hasattr(self, 'info_label'):
            self.info_label.config(bg=self.current_theme["bg"], fg=self.current_theme["fg"])
        if hasattr(self, 'canvas'):
            self.canvas.config(bg=self.current_theme["canvas_bg"])

    def toggle_theme(self):
        self.current_theme = self.dark_theme if self.current_theme == self.light_theme else self.light_theme
        self.apply_theme()
        self.render_text()

    def build_typing_screen(self):
        self.typed_text = ""
        self.start_time = None
        self.timer_running = False

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg=self.current_theme["bg"])

        self.stats_frame = tk.Frame(self.root, pady=10, bg=self.current_theme["bg"])
        self.stats_frame.pack()

        self.timer_label = tk.Label(self.stats_frame, text="Time Left: 60s", font=("Arial", 14), bg=self.current_theme["bg"], fg=self.current_theme["fg"])
        self.timer_label.pack()

        self.canvas_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        self.canvas_frame.pack(pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, height=60, width=800, bg=self.current_theme["canvas_bg"], highlightthickness=1, relief="solid")
        self.canvas.pack()

        self.info_label = tk.Label(self.root, text="Start typing whenever you're ready.", font=("Arial", 12), fg="gray", bg=self.current_theme["bg"])
        self.info_label.pack(pady=10)

        self.theme_toggle = tk.Button(self.root, text="Toggle Theme", command=self.toggle_theme, bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"], font=("Arial", 10))
        self.theme_toggle.pack(pady=5)

        self.render_text()
        self.root.bind("<Key>", self.handle_keypress)

    def render_text(self):
        self.canvas.delete("all")
        x = self.canvas_text_offset
        y = 30
        char_width = 12

        for i in range(len(REFERENCE_TEXT)):
            char = REFERENCE_TEXT[i]

            if i < len(self.typed_text):
                typed_char = self.typed_text[i]
                color = self.current_theme["text_correct"] if typed_char == char else self.current_theme["text_incorrect"]
            else:
                color = self.current_theme["text_default"]

            self.canvas.create_text(x, y, text=char, font=self.canvas_font, fill=color, anchor="w")

            if i == len(self.typed_text):
                self.canvas.create_line(x, y + 15, x, y - 20, fill=self.current_theme["cursor"], width=2)

            x += char_width

        total_width = len(REFERENCE_TEXT) * char_width
        self.canvas.config(scrollregion=(0, 0, total_width + 40, 60))

        cursor_x = len(self.typed_text) * char_width
        visible_width = self.canvas.winfo_width()

        if cursor_x > visible_width - 100:
            scroll_x = cursor_x - (visible_width // 2)
            self.canvas.xview_moveto(scroll_x / total_width)

    def handle_keypress(self, event):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

        if event.keysym == "BackSpace":
            self.typed_text = self.typed_text[:-1]
        elif len(event.char) == 1 and event.char.isprintable():
            self.typed_text += event.char

        index = len(self.typed_text) - 1
        if 0 <= index < len(REFERENCE_TEXT) and self.typed_text[index] != REFERENCE_TEXT[index]:
            threading.Thread(target=self.play_beep, daemon=True).start()

        self.render_text()

    def play_beep(self):
        try:
            playsound("beep.mp3")
        except Exception as e:
            print("Error playing sound:", e)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        remaining = self.time_limit - elapsed
        self.timer_label.config(text=f"Time Left: {remaining}s")

        if remaining <= 0:
            self.root.unbind("<Key>")
            self.calculate_results()
        else:
            self.root.after(1000, self.update_timer)

    def calculate_results(self):
        typed = self.typed_text
        reference = REFERENCE_TEXT[:len(typed)]

        correct_chars = sum(1 for i in range(len(typed)) if typed[i] == reference[i])
        accuracy = (correct_chars / len(typed)) * 100 if typed else 0

        elapsed = time.time() - self.start_time
        wpm = (len(typed.split()) / elapsed) * 60 if elapsed else 0
        cpm = (len(typed) / elapsed) * 60 if elapsed else 0

        self.show_result_screen(int(wpm), int(cpm), int(accuracy))

    def show_result_screen(self, wpm, cpm, accuracy):
        for widget in self.root.winfo_children():
            widget.destroy()

        result_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        result_frame.pack(expand=True)

        tk.Label(result_frame, text="Typing Test Results", font=("Arial", 18, "bold"), bg=self.current_theme["bg"], fg=self.current_theme["fg"]).pack(pady=10)
        tk.Label(result_frame, text=f"WPM {wpm}", font=("Arial", 14), bg=self.current_theme["bg"], fg="green").pack(pady=5)
        tk.Label(result_frame, text=f"CPM {cpm}", font=("Arial", 14), bg=self.current_theme["bg"], fg="purple").pack(pady=5)
        tk.Label(result_frame, text=f"Accuracy {accuracy}%", font=("Arial", 14), bg=self.current_theme["bg"], fg="orange").pack(pady=5)

        tk.Button(result_frame, text="Try Again", font=("Arial", 12), command=self.build_typing_screen,
                  bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"]).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedApp(root)
    root.mainloop()
