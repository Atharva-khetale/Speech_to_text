import speech_recognition as sr
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import queue
import time


class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Speech-to-Text Pro")
        self.root.geometry("900x650")

        # Speech recognition components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.stop_listening = None
        self.text_buffer = ""
        self.audio_queue = queue.Queue()

        # Session management
        self.session_active = False
        self.session_history = []
        self.current_session = []

        # Language support
        self.languages = {
            'English': 'en-US',
            'Spanish': 'es-ES',
            'French': 'fr-FR',
            'German': 'de-DE',
            'Italian': 'it-IT',
            'Portuguese': 'pt-PT',
            'Russian': 'ru-RU',
            'Japanese': 'ja-JP',
            'Chinese': 'zh-CN',
            'Hindi': 'hi-IN',
            'Arabic': 'ar-SA',
            'Dutch': 'nl-NL',
            'Korean': 'ko-KR',
            'Turkish': 'tr-TR'
        }
        self.current_language = 'en-US'

        # Create GUI elements
        self.create_widgets()

        # Adjust for ambient noise automatically
        self.adjust_for_ambient_noise()

        # Start the audio processing thread
        self.process_audio_thread = threading.Thread(target=self.process_audio_queue, daemon=True)
        self.process_audio_thread.start()

    def create_widgets(self):
        """Create all GUI components"""
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TCombobox', padding=5)

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Control panel frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # Left control panel
        left_control = ttk.Frame(control_frame)
        left_control.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Language selection
        lang_frame = ttk.Frame(left_control)
        lang_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)

        self.lang_var = tk.StringVar()
        self.lang_combobox = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=list(self.languages.keys()),
            state="readonly",
            width=15
        )
        self.lang_combobox.current(0)  # Default to English
        self.lang_combobox.pack(side=tk.LEFT)
        self.lang_combobox.bind("<<ComboboxSelected>>", self.change_language)

        # Right control panel
        right_control = ttk.Frame(control_frame)
        right_control.pack(side=tk.RIGHT)

        # Start/Stop button
        self.toggle_button = ttk.Button(
            right_control,
            text="Start New Session",
            command=self.toggle_session,
            style='TButton'
        )
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        # Pause/Resume button
        self.pause_button = ttk.Button(
            right_control,
            text="Pause",
            command=self.toggle_pause,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # Session management button
        session_menu = tk.Menu(self.root, tearoff=0)
        session_menu.add_command(label="Save Current Session", command=self.save_session)
        session_menu.add_command(label="Clear Current Session", command=self.clear_current_session)
        session_menu.add_separator()
        session_menu.add_command(label="View Session History", command=self.show_history)

        self.session_button = ttk.Button(
            right_control,
            text="Session ▼",
            command=lambda: session_menu.post(self.session_button.winfo_rootx(),
                                              self.session_button.winfo_rooty() + self.session_button.winfo_height())
        )
        self.session_button.pack(side=tk.LEFT, padx=5)

        # Text display with tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Current session tab
        self.current_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.current_tab, text="Current Session")

        self.text_display = scrolledtext.ScrolledText(
            self.current_tab,
            wrap=tk.WORD,
            font=('Arial', 12),
            padx=10,
            pady=10
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Start a new session")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X)

        # Configure tags for text display
        self.text_display.tag_config('highlight', background='yellow')

    def change_language(self, event=None):
        """Handle language selection change"""
        selected_lang = self.lang_var.get()
        self.current_language = self.languages.get(selected_lang, 'en-US')
        self.status_var.set(f"Language changed to {selected_lang}")

        # If we're in a session, update the recognition
        if self.session_active and self.is_listening:
            self.stop_listening()
            self.start_listening()

    def adjust_for_ambient_noise(self):
        """Calibrate the recognizer for ambient noise"""

        def do_calibration():
            self.status_var.set("Adjusting for ambient noise... (stay silent)")
            with self.microphone as source:
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=2)
                    self.status_var.set("Ready - Start a new session")
                except Exception as e:
                    self.status_var.set(f"Error: {str(e)}")
                    messagebox.showerror("Error", f"Microphone error: {str(e)}")

        threading.Thread(target=do_calibration, daemon=True).start()

    def toggle_session(self):
        """Start or stop a session"""
        if self.session_active:
            self.end_session()
        else:
            self.start_session()

    def start_session(self):
        """Begin a new transcription session"""
        self.session_active = True
        self.current_session = []
        self.text_buffer = ""
        self.text_display.delete(1.0, tk.END)

        self.toggle_button.config(text="End Session")
        self.pause_button.config(state=tk.NORMAL, text="Pause")
        self.lang_combobox.config(state=tk.DISABLED)

        self.start_listening()
        self.status_var.set(f"Session started - Listening... (Language: {self.get_language_name()})")

    def end_session(self):
        """End the current session"""
        self.stop_listening()

        # Save to history
        if self.text_buffer.strip():
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.session_history.append({
                'timestamp': timestamp,
                'language': self.get_language_name(),
                'content': self.text_buffer
            })

        self.session_active = False
        self.toggle_button.config(text="Start New Session")
        self.pause_button.config(state=tk.DISABLED)
        self.lang_combobox.config(state="readonly")

        self.status_var.set(f"Session ended - Ready to start new session")

    def toggle_pause(self):
        """Pause or resume listening"""
        if self.is_listening:
            self.stop_listening()
            self.pause_button.config(text="Resume")
            self.status_var.set("Session paused - Click Resume to continue")
        else:
            self.start_listening()
            self.pause_button.config(text="Pause")
            self.status_var.set(f"Session resumed - Listening... (Language: {self.get_language_name()})")

    def get_language_name(self):
        """Get the display name for the current language code"""
        for name, code in self.languages.items():
            if code == self.current_language:
                return name
        return "English"

    def start_listening(self):
        """Begin real-time transcription"""
        if self.is_listening or not self.session_active:
            return

        self.is_listening = True

        def callback(recognizer, audio):
            self.audio_queue.put(audio)

        self.stop_listening = self.recognizer.listen_in_background(
            self.microphone,
            callback,
            phrase_time_limit=5
        )

    def process_audio_queue(self):
        """Process audio from the queue in a separate thread"""
        while True:
            audio = self.audio_queue.get()
            if audio is None:
                break

            try:
                text = self.recognizer.recognize_google(audio, language=self.current_language)
                self.current_session.append(text)
                self.text_buffer += text + " "

                # Update the GUI from the main thread
                self.root.after(0, self.update_display)

            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                self.root.after(0, lambda: self.status_var.set(f"API Error: {e}"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))

    def stop_listening(self):
        """Stop the transcription"""
        if not self.is_listening:
            return

        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)
        self.is_listening = False

    def update_display(self):
        """Update the text display with the current buffer"""
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, self.text_buffer)

        # Highlight the most recent addition if there's content
        if self.current_session:
            start_pos = self.text_display.search(
                self.current_session[-1],
                "1.0",
                stopindex=tk.END,
                backwards=True
            )
            if start_pos:
                end_pos = f"{start_pos}+{len(self.current_session[-1])}c"
                self.text_display.tag_add('highlight', start_pos, end_pos)
                self.text_display.after(1000, lambda: self.text_display.tag_remove('highlight', start_pos, end_pos))

        self.text_display.see(tk.END)

    def save_session(self):
        """Save the current session to a file"""
        if not self.text_buffer.strip():
            messagebox.showwarning("Warning", "No text to save in current session!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ],
            title="Save Current Session"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Session Transcript ({self.get_language_name()})\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(self.text_buffer)
                self.status_var.set(f"Session saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save session: {str(e)}")

    def clear_current_session(self):
        """Clear the current session"""
        if self.session_active:
            if messagebox.askyesno("Confirm", "Clear current session? This cannot be undone."):
                self.text_buffer = ""
                self.current_session = []
                self.text_display.delete(1.0, tk.END)
                self.status_var.set("Current session cleared - Continue speaking")
        else:
            messagebox.showinfo("Info", "No active session to clear")

    def show_history(self):
        """Show session history in a new window"""
        if not self.session_history:
            messagebox.showinfo("History", "No previous sessions available")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("Session History")
        history_window.geometry("800x600")

        notebook = ttk.Notebook(history_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        for i, session in enumerate(reversed(self.session_history)):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=session['timestamp'])

            text = scrolledtext.ScrolledText(
                tab,
                wrap=tk.WORD,
                font=('Arial', 12),
                padx=10,
                pady=10
            )
            text.pack(fill=tk.BOTH, expand=True)

            text.insert(tk.END, f"Language: {session['language']}\n")
            text.insert(tk.END, f"Time: {session['timestamp']}\n")
            text.insert(tk.END, "=" * 40 + "\n\n")
            text.insert(tk.END, session['content'])
            text.config(state=tk.DISABLED)

            # Add save button for each session
            save_btn = ttk.Button(
                tab,
                text="Save This Session",
                command=lambda s=session: self.save_history_session(s)
            )
            save_btn.pack(pady=5)

    def save_history_session(self, session):
        """Save a historical session to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title=f"Save Session from {session['timestamp']}"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Session Transcript ({session['language']})\n")
                    f.write(f"Time: {session['timestamp']}\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(session['content'])
                messagebox.showinfo("Success", f"Session saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save session: {str(e)}")


def main():
    root = tk.Tk()

    # Set theme if available
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
        root.set_theme("arc")
    except ImportError:
        pass

    app = SpeechToTextApp(root)

    # Set minimum window size
    root.minsize(700, 500)

    # Handle window close
    def on_closing():
        if app.session_active:
            if messagebox.askokcancel("Quit", "A session is active. Are you sure you want to quit?"):
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()