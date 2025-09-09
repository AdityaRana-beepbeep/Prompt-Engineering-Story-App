# Updated
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import requests
import json
import threading
import pyttsx3
import os
from dotenv import load_dotenv
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import fitz # Import for PDF reading

# Load environment variables from .env file
load_dotenv()

# --- PROMPT GENERATION FUNCTIONS ---
def generate_zero_shot_prompt(user_prompt):
    """Generates a zero-shot prompt."""
    return f"Write a short story about: {user_prompt}"

def generate_few_shot_prompt(user_prompt):
    """Generates a few-shot prompt with concise examples."""
    return f"""Examples:
Prompt: Brave knight quest.
Story: Sir Reginald, brave and true, sought the Dragon's Tear. Through enchanted forests and over treacherous mountains, he faced goblins and riddles. He found the dragon, not fierce, but guarding a single, glowing tear. It healed his ailing village, proving courage comes in many forms.

Prompt: Alien discovery.
Story: Commander Eva landed on Kepler-186f. Bioluminescent flora pulsed. She met beings of pure light, communicating through shifting patterns. They were a living cosmic library, sharing wisdom through ethereal dances.

Now, write a short story about: {user_prompt}"""

def generate_chain_of_thought_prompt(user_prompt):
    """Generates a chain-of-thought prompt with concise steps."""
    return f"""Let's think step by step to create a compelling short story about: {user_prompt}.

1. Character: Define main character, desire, obstacle.
2. Plot: Outline intro, rising action (obstacle), climax, falling action, resolution.
3. Setting: Describe atmosphere.
4. Story: Write, incorporating these elements."""

def get_story_from_gemini(full_prompt, api_key, stop_event):
    """Calls the Gemini API to generate a story with a stop event."""
    if not api_key:
        return "Error: API key is missing. Please set it in a .env file."

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {"contents": [{"role": "user", "parts": [{"text": full_prompt}]}]}

    try:
        response = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        response.raise_for_status()

        if stop_event.is_set():
            return "Generation canceled by user."

        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and result["candidates"][0].get("content"):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_message = result.get("error", {}).get("message", "Unknown API error.")
            return f"Could not generate a story. Error: {error_message}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred while connecting to the API: {e}"
    except json.JSONDecodeError:
        return "Failed to decode JSON response from the API."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

class StoryGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Story Generator")
        self.master.geometry("900x800")
        self.master.resizable(True, True)

        self.API_KEY = os.getenv("GEMINI_API_KEY")

        # Initialize TTS engine
        try:
            self.tts_engine = pyttsx3.init()
            self.voices = self.tts_engine.getProperty('voices')
            self.tts_engine_ready = True
        except Exception as e:
            self.tts_engine = None
            self.tts_engine_ready = False
            messagebox.showwarning("TTS Warning", f"Text-to-Speech engine could not be initialized: {e}\nVoice features will be disabled.")

        # Threading control
        self.api_stop_event = threading.Event()
        self.generation_thread = None

        # New: Language mapping
        self.language_map = {
            "English": "en",
            "Hindi": "hi",
            "Spanish": "es",
            "French": "fr"
            # Add more languages here as needed
        }
        self.reverse_language_map = {v: k for k, v in self.language_map.items()}

        self.setup_ui()
        self.update_language_options()
        self.update_tts_options()

    def setup_ui(self):
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(5, weight=1)

        # --- HEADER FRAME ---
        header_frame = ttk.Frame(self.master, padding=(10, 10))
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="AI Story Generator", font=("Helvetica", 28, "bold"))
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="ew")

        # --- INPUTS FRAME ---
        inputs_frame = ttk.Frame(self.master, padding=(10, 5))
        inputs_frame.grid(row=1, column=0, sticky="ew")
        inputs_frame.grid_columnconfigure(0, weight=1)
        inputs_frame.grid_columnconfigure(1, weight=0)

        prompt_label_frame = ttk.Frame(inputs_frame)
        prompt_label_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(prompt_label_frame, text="Enter your story prompt/topic:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.pdf_file_label = ttk.Label(prompt_label_frame, text="", font=("Helvetica", 10, "italic"), bootstyle="info")
        self.pdf_file_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        prompt_label_frame.grid_columnconfigure(0, weight=1)
        
        self.prompt_entry = ttk.Entry(inputs_frame, font=("Helvetica", 11), bootstyle="primary")
        self.prompt_entry.grid(row=1, column=0, sticky="ew")
        self.prompt_entry.bind("<KeyRelease>", self.update_prompt_char_count)

        self.upload_button = ttk.Button(inputs_frame, text="Upload PDF", command=self.upload_pdf, bootstyle="secondary", cursor="hand2")
        self.upload_button.grid(row=1, column=1, padx=(5, 0), sticky="ew")

        self.char_count_label = ttk.Label(inputs_frame, text="Characters: 0", font=("Helvetica", 10))
        self.char_count_label.grid(row=2, column=0, sticky="e", pady=(5, 0), columnspan=2)

        # --- PROMPT METHOD FRAME ---
        method_frame = ttk.Frame(self.master, padding=(10, 10))
        method_frame.grid(row=2, column=0, sticky="ew")
        ttk.Label(method_frame, text="Choose prompting method:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5), columnspan=3)

        self.prompt_method = tk.StringVar(value="zero-shot")
        self.method_radio_buttons = [
            ttk.Radiobutton(method_frame, text="Zero-shot", variable=self.prompt_method, value="zero-shot", bootstyle="info, toolbutton"),
            ttk.Radiobutton(method_frame, text="Few-shot", variable=self.prompt_method, value="few-shot", bootstyle="info, toolbutton"),
            ttk.Radiobutton(method_frame, text="Chain-of-Thought", variable=self.prompt_method, value="chain-of-thought", bootstyle="info, toolbutton")
        ]
        for i, rb in enumerate(self.method_radio_buttons):
            rb.grid(row=1, column=i, padx=(0, 5) if i == 0 else 5)

        # --- CONTROL BUTTONS & PROGRESS BAR ---
        control_frame = ttk.Frame(self.master, padding=(10, 5))
        control_frame.grid(row=3, column=0, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        self.generate_button = ttk.Button(control_frame, text="Generate Story", command=self.start_story_generation, bootstyle="primary", cursor="hand2")
        self.generate_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.cancel_button = ttk.Button(control_frame, text="Cancel", command=self.cancel_generation, bootstyle="danger", state=tk.DISABLED, cursor="hand2")
        self.cancel_button.grid(row=0, column=1, padx=(5, 5), sticky="ew")

        self.clear_button = ttk.Button(control_frame, text="Clear", command=self.clear_fields, bootstyle="secondary", cursor="hand2")
        self.clear_button.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", mode="indeterminate", bootstyle="primary")
        self.progress_bar.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.progress_bar.stop()

        # --- STORY OUTPUT FRAME ---
        output_frame = ttk.Frame(self.master, padding=(10, 5))
        output_frame.grid(row=5, column=0, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)

        output_header_frame = ttk.Frame(output_frame)
        output_header_frame.grid(row=0, column=0, sticky="ew")
        output_header_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(output_header_frame, text="Generated Story:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.copy_button = ttk.Button(output_header_frame, text="Copy", command=self.copy_story, bootstyle="info", cursor="hand2", state=tk.DISABLED)
        self.copy_button.grid(row=0, column=1, sticky="e", padx=(10, 0))

        self.story_output = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Helvetica", 11), height=15, bd=1, relief=tk.SUNKEN)
        self.story_output.grid(row=1, column=0, sticky="nsew")

        # --- TTS CONTROLS & SAVE BUTTON ---
        tts_frame = ttk.Frame(self.master, padding=(10, 5))
        tts_frame.grid(row=6, column=0, sticky="ew")
        tts_frame.grid_columnconfigure(0, weight=1)
        tts_frame.grid_columnconfigure(1, weight=1)
        tts_frame.grid_columnconfigure(2, weight=1)

        # Language selection
        ttk.Label(tts_frame, text="Language:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.language_combo = ttk.Combobox(tts_frame, state="readonly", bootstyle="info")
        self.language_combo.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(0, 5))
        self.language_combo.bind("<<ComboboxSelected>>", self.update_voice_options)

        # Voice selection
        ttk.Label(tts_frame, text="Voice:", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.voice_combo = ttk.Combobox(tts_frame, state="readonly", bootstyle="info")
        self.voice_combo.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 5))
        self.voice_combo.bind("<<ComboboxSelected>>", self.set_tts_voice)

        # Rate slider
        ttk.Label(tts_frame, text="Speech Rate:", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.rate_slider = ttk.Scale(tts_frame, from_=100, to=250, orient=tk.HORIZONTAL, command=self.set_tts_rate)
        self.rate_slider.set(170)
        self.rate_slider.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(5, 0))

        # Buttons
        read_stop_frame = ttk.Frame(tts_frame)
        read_stop_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        read_stop_frame.grid_columnconfigure(0, weight=1)
        read_stop_frame.grid_columnconfigure(1, weight=1)

        self.read_button = ttk.Button(read_stop_frame, text="Read Story", command=self.start_reading_story, bootstyle="success", cursor="hand2", state=tk.DISABLED)
        self.read_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.stop_button = ttk.Button(read_stop_frame, text="Stop Reading", command=self.stop_reading_story, bootstyle="danger", cursor="hand2", state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.save_button = ttk.Button(tts_frame, text="Save Story", command=self.save_story, bootstyle="info", cursor="hand2", state=tk.DISABLED)
        self.save_button.grid(row=3, column=2, sticky="ew", pady=(10, 0), padx=(5, 0))

        # --- STATUS BAR ---
        self.status_bar = ttk.Label(self.master, text="Ready.", font=("Helvetica", 10), bootstyle="secondary")
        self.status_bar.grid(row=7, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        # List of widgets to control state
        self.controllable_widgets = [
            self.prompt_entry, self.upload_button, self.generate_button, self.rate_slider,
            self.language_combo, self.voice_combo
        ]
        self.controllable_widgets.extend(self.method_radio_buttons)

    def update_prompt_char_count(self, event=None):
        char_count = len(self.prompt_entry.get())
        self.char_count_label.config(text=f"Characters: {char_count}")

    def update_language_options(self):
        """Populates the language combobox with available options."""
        if self.tts_engine_ready:
            available_languages = set()
            for voice in self.voices:
                lang_code_parts = voice.id.split('_')
                if len(lang_code_parts) > 1:
                    lang_code = lang_code_parts[1].split('-')[0].lower()
                    if lang_code in self.reverse_language_map:
                        available_languages.add(self.reverse_language_map[lang_code])
            
            sorted_languages = sorted(list(available_languages))
            self.language_combo['values'] = sorted_languages
            if "English" in sorted_languages:
                self.language_combo.set("English")
            elif sorted_languages:
                self.language_combo.set(sorted_languages[0])

            self.update_voice_options()
        else:
            self.language_combo.config(state="disabled")

    def update_voice_options(self, event=None):
        """Populates the voice combobox based on the selected language."""
        if self.tts_engine_ready:
            selected_language_name = self.language_combo.get()
            selected_lang_code = self.language_map.get(selected_language_name, "en") # Default to English

            filtered_voices = [
                voice for voice in self.voices 
                if voice.id.lower().startswith(f"hkey_local_machine\\software\\microsoft\\speech\\voices\\tokens\\{selected_lang_code}")
            ]
            
            voice_names = [f"{v.name} ({v.gender.capitalize()})" if v.gender else v.name for v in filtered_voices]
            self.voice_combo['values'] = voice_names
            
            if voice_names:
                self.voice_combo.set(voice_names[0])
                self.tts_engine.setProperty('voice', filtered_voices[0].id)
                self.voice_combo.config(state="readonly")
            else:
                self.voice_combo.set("No voices found")
                self.voice_combo.config(state="disabled")
                self.tts_engine.setProperty('voice', None)
        else:
            self.voice_combo.config(state="disabled")
            
    def update_tts_options(self):
        """Sets the rate slider value."""
        if self.tts_engine_ready:
            self.rate_slider.set(self.tts_engine.getProperty('rate'))
        else:
            self.rate_slider.config(state="disabled")

    def set_tts_voice(self, event):
        if self.tts_engine_ready:
            selected_voice_name = self.voice_combo.get().split(' (')[0]
            for voice in self.voices:
                if voice.name == selected_voice_name:
                    self.tts_engine.setProperty('voice', voice.id)
                    break

    def set_tts_rate(self, value):
        if self.tts_engine_ready:
            self.tts_engine.setProperty('rate', int(float(value)))

    def show_status(self, message, bootstyle="secondary"):
        self.status_bar.config(text=message, bootstyle=bootstyle)
        self.master.update_idletasks()

    def set_inputs_state(self, state):
        for widget in self.controllable_widgets:
            widget.config(state=state)
        if state == tk.NORMAL:
            self.language_combo.config(state="readonly")
            self.voice_combo.config(state="readonly" if self.voice_combo['values'] else "disabled")

    def start_story_generation(self):
        user_prompt = self.prompt_entry.get().strip()
        if not user_prompt:
            messagebox.showerror("Input Error", "Please enter a story prompt.")
            return

        self.story_output.delete(1.0, tk.END)
        self.show_status("Generating story...", "info")
        self.set_inputs_state(tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.read_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        
        self.api_stop_event.clear()
        self.generation_thread = threading.Thread(target=self._generate_story_thread, args=(user_prompt, ))
        self.generation_thread.start()

    def _generate_story_thread(self, user_prompt):
        selected_method = self.prompt_method.get()
        full_prompt = ""

        if selected_method == "zero-shot":
            full_prompt = generate_zero_shot_prompt(user_prompt)
        elif selected_method == "few-shot":
            full_prompt = generate_few_shot_prompt(user_prompt)
        elif selected_method == "chain-of-thought":
            full_prompt = generate_chain_of_thought_prompt(user_prompt)

        self.master.after(0, lambda: self.show_status(f"Generating story (approx. {int(len(full_prompt)/4)} tokens)...", "info"))
        generated_story = get_story_from_gemini(full_prompt, self.API_KEY, self.api_stop_event)

        processed_story_text = self.parse_generated_story(generated_story, selected_method)
        self.master.after(0, self._update_gui_after_generation, processed_story_text)

    def parse_generated_story(self, generated_story, selected_method):
        # Clean markdown
        processed_story_text = generated_story.replace('**', '').replace('*', '').strip()
        
        # Remove extra prompt details based on method
        if selected_method == "few-shot":
            story_marker = "Story:"
            if story_marker in processed_story_text:
                processed_story_text = processed_story_text.rsplit(story_marker, 1)[-1].strip()
            # The model might also just continue the text without a 'Story:' marker
            elif "Now, write a short story about:" in processed_story_text:
                processed_story_text = processed_story_text.rsplit("Now, write a short story about:", 1)[-1].strip()

        elif selected_method == "chain-of-thought":
            story_marker = "4. Story:"
            if story_marker in processed_story_text:
                processed_story_text = processed_story_text.rsplit(story_marker, 1)[-1].strip()
            # If marker is not found, attempt to clean up the response
            else:
                lines = processed_story_text.split('\n')
                story_lines = [line for line in lines if not line.strip().startswith(('1.', '2.', '3.', 'Character:', 'Plot:', 'Setting:'))]
                processed_story_text = '\n'.join(story_lines).strip()
        
        return processed_story_text.strip()
    
    def _update_gui_after_generation(self, generated_story):
        self.progress_bar.stop()
        self.set_inputs_state(tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.story_output.delete(1.0, tk.END)
        self.story_output.insert(tk.END, generated_story)

        if "Error:" in generated_story or "Could not generate" in generated_story or "Canceled" in generated_story:
            self.show_status("Story generation failed or was canceled.", "danger")
        else:
            self.show_status("Story generated successfully!", "success")
            self.save_button.config(state=tk.NORMAL)
            self.copy_button.config(state=tk.NORMAL)
            if self.tts_engine_ready:
                self.read_button.config(state=tk.NORMAL)

    def cancel_generation(self):
        self.api_stop_event.set()
        self.show_status("Canceling story generation...", "warning")
        if self.generation_thread and self.generation_thread.is_alive():
            self.progress_bar.stop()
            self.set_inputs_state(tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.story_output.delete(1.0, tk.END)
            self.story_output.insert(tk.END, "Story generation was canceled.")
            self.show_status("Generation canceled.", "danger")

    def clear_fields(self):
        self.prompt_entry.delete(0, tk.END)
        self.story_output.delete(1.0, tk.END)
        self.pdf_file_label.config(text="")
        self.char_count_label.config(text="Characters: 0")
        self.save_button.config(state=tk.DISABLED)
        self.read_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.show_status("Ready.", "secondary")

    def start_reading_story(self):
        if not self.tts_engine_ready:
            messagebox.showwarning("TTS Not Ready", "Text-to-Speech engine is not available.")
            return

        story_text = self.story_output.get(1.0, tk.END).strip()
        if not story_text or "Error:" in story_text or "Canceled" in story_text:
            self.show_status("No story to read.", "warning")
            return

        self.read_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.show_status("Reading story...", "info")

        threading.Thread(target=self._read_story_thread, args=(story_text,)).start()

    def _read_story_thread(self, text):
        if self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        self.master.after(0, self._update_tts_buttons_after_speech)

    def stop_reading_story(self):
        if self.tts_engine:
            self.tts_engine.stop()
            self.show_status("Story narration stopped.", "warning")
            self._update_tts_buttons_after_speech()

    def _update_tts_buttons_after_speech(self):
        self.read_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        self.copy_button.config(state=tk.NORMAL)
        self.show_status("Ready.", "success" if "success" in self.status_bar.cget("bootstyle") else "secondary")

    def save_story(self):
        story_text = self.story_output.get(1.0, tk.END).strip()
        if not story_text:
            messagebox.showwarning("Save Error", "No story to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")],
            title="Save Story As"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(story_text)
                self.show_status(f"Story saved to {os.path.basename(file_path)}", "success")
            except Exception as e:
                self.show_status(f"Failed to save file: {e}", "danger")

    def copy_story(self):
        story_text = self.story_output.get(1.0, tk.END).strip()
        if story_text:
            self.master.clipboard_clear()
            self.master.clipboard_append(story_text)
            self.show_status("Story copied to clipboard!", "info")
        else:
            self.show_status("Nothing to copy.", "warning")

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select a PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return

        self.show_status("Reading PDF file...", "info")
        extracted_text = self.read_pdf_text(file_path)

        if extracted_text:
            self.prompt_entry.delete(0, tk.END)
            self.prompt_entry.insert(0, extracted_text)
            self.update_prompt_char_count()
            self.pdf_file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            self.show_status("PDF content loaded into prompt entry.", "success")
        else:
            self.show_status("Failed to read PDF. It might be password-protected or corrupt.", "danger")
            self.pdf_file_label.config(text="")

    def read_pdf_text(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            messagebox.showerror("PDF Error", f"Could not read PDF: {e}")
            return None

if __name__ == "__main__":
    if os.getenv("GEMINI_API_KEY") is None:
        messagebox.showerror("API Key Error", "GEMINI_API_KEY not found. Please create a .env file with GEMINI_API_KEY='YOUR_API_KEY_HERE'")
    else:
        app_theme = "solar"
        root = ttk.Window(themename=app_theme)
        app = StoryGeneratorApp(root)
        root.mainloop()