import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import json
import threading # For running API call and TTS in separate threads to keep GUI responsive
import pyttsx3   # For Text-to-Speech

def generate_zero_shot_prompt(user_prompt):
    """
    Generates a zero-shot prompt.
    Args:
        user_prompt (str): The user's input prompt.
    Returns:
        str: The zero-shot prompt.
    """
    return f"Write a short story about: {user_prompt}"

def generate_few_shot_prompt(user_prompt):
    """
    Generates a few-shot prompt with examples.
    Args:
        user_prompt (str): The user's input prompt.
    Returns:
        str: The few-shot prompt.
    """
    return f"""Here are a few examples of stories based on prompts:

Prompt: A detective solving a mystery in a haunted mansion.
Story: Detective Miles Corbin adjusted his fedora as he stepped into Blackwood Manor, a place whispered to be cursed. Dust motes danced in the slivers of moonlight, illuminating cobweb-draped chandeliers. The case was simple: a missing heirloom. But the chilling whispers and phantom footsteps suggested a more spectral culprit. Miles, a man of logic, found himself questioning everything as a cold breath ghosted his neck, and a spectral hand pointed towards a hidden passage behind a crumbling fireplace. Following the eerie guidance, he discovered not only the missing jewel but also the diary of a heartbroken ghost, revealing a tale of betrayal and a hidden will. The mystery was solved, but Miles left with a new respect for the unseen.

Prompt: A space explorer discovering a new alien species.
Story: Commander Eva Rostova's probe detected an unusual energy signature on Kepler-186f. Landing her shuttle, she found a forest of bioluminescent flora, pulsating with soft light. Deeper within, she encountered them: beings of pure light, shifting and swirling like living nebulae. They communicated not with sound, but with intricate patterns of light that conveyed complex emotions and histories. Eva spent weeks observing, learning their silent language, and realized they were not just a new species, but a living library of cosmic knowledge, sharing their wisdom through ethereal dances.

Now, write a short story about: {user_prompt}"""

def generate_chain_of_thought_prompt(user_prompt):
    """
    Generates a chain-of-thought prompt.
    Args:
        user_prompt (str): The user's input prompt.
    Returns:
        str: The chain-of-thought prompt.
    """
    return f"""Let's think step by step to create a compelling short story about: {user_prompt}.

First, brainstorm a main character, their core desire, and a significant obstacle they face.
Second, outline a simple plot: introduction, rising action (with the obstacle), climax (where they confront the obstacle), falling action, and resolution.
Third, consider the setting and its atmosphere.
Finally, write the story, incorporating these elements."""

def get_story_from_gemini(full_prompt):
    """
    Calls the Gemini API to generate a story.
    Args:
        full_prompt (str): The complete prompt to send to the model.
    Returns:
        str: The generated story, or an error message if generation fails.
    """
    # IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual Gemini API key.
    # You can get one from Google AI Studio: https://aistudio.google.com/app/apikey
    api_key = "AIzaSyAlWhf3vTzvdfDQCRproN7EUK0ajbf209A"

    if api_key == "YOUR_API_KEY_HERE" or not api_key:
        # Using messagebox for critical error that prevents API call
        messagebox.showerror("API Key Error", "API key is missing. Please replace 'YOUR_API_KEY_HERE' with your actual API key in the script.")
        return "Error: API key is missing. Please set it in the script."

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    chat_history = []
    chat_history.append({"role": "user", "parts": [{"text": full_prompt}]})

    payload = {"contents": chat_history}

    try:
        response = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Could not generate a story. The AI response was empty or malformed."
    except requests.exceptions.RequestException as e:
        return f"An error occurred while connecting to the API: {e}"
    except json.JSONDecodeError:
        return "Failed to decode JSON response from the API."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

class StoryGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("AI Story Generator")
        master.geometry("800x750") # Slightly larger default window size
        master.resizable(True, True) # Allow resizing

        # Initialize Text-to-Speech engine
        try:
            self.tts_engine = pyttsx3.init()
            # You can set properties like voice, rate, volume here
            # voices = self.tts_engine.getProperty('voices')
            # self.tts_engine.setProperty('voice', voices[0].id) # Change voice if needed
            self.tts_engine.setProperty('rate', 170) # Speed of speech
            self.tts_engine_ready = True
        except Exception as e:
            self.tts_engine = None
            self.tts_engine_ready = False
            messagebox.showwarning("TTS Warning", f"Text-to-Speech engine could not be initialized: {e}\nVoice features will be disabled.")

        # Configure grid weights for responsive layout
        master.grid_rowconfigure(0, weight=0) # Title row
        master.grid_rowconfigure(1, weight=0) # Prompt input row
        master.grid_rowconfigure(2, weight=0) # Prompt method radio buttons
        master.grid_rowconfigure(3, weight=0) # Message/loading row
        master.grid_rowconfigure(4, weight=0) # Generate button row
        master.grid_rowconfigure(5, weight=1) # Story output textarea row (expands vertically)
        master.grid_rowconfigure(6, weight=0) # Read/Stop buttons row
        master.grid_columnconfigure(0, weight=1) # Main column (expands horizontally)

        # Title
        self.title_label = tk.Label(master, text="AI Story Generator", font=("Arial", 24, "bold"), fg="#4f46e5") # Purple title
        self.title_label.grid(row=0, column=0, pady=20, sticky="ew")

        # Prompt Input Frame
        self.prompt_frame = tk.Frame(master, padx=10, pady=5)
        self.prompt_frame.grid(row=1, column=0, sticky="ew")
        self.prompt_frame.grid_columnconfigure(0, weight=1) # Allow entry to expand

        self.prompt_label = tk.Label(self.prompt_frame, text="Enter your story prompt/topic:", font=("Arial", 12, "bold"))
        self.prompt_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.prompt_entry = tk.Entry(self.prompt_frame, font=("Arial", 11), bd=2, relief=tk.GROOVE) # Added border style
        self.prompt_entry.grid(row=1, column=0, sticky="ew")

        # Prompt Method Selection Frame
        self.method_frame = tk.Frame(master, padx=10, pady=10)
        self.method_frame.grid(row=2, column=0, sticky="ew")
        self.method_frame.grid_columnconfigure(0, weight=1) # For label alignment

        self.method_label = tk.Label(self.method_frame, text="Choose prompting method:", font=("Arial", 12, "bold"))
        self.method_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.prompt_method = tk.StringVar(value="zero-shot") # Default selected
        self.radio_buttons_frame = tk.Frame(self.method_frame) # Frame for radio buttons
        self.radio_buttons_frame.grid(row=1, column=0, sticky="w")

        self.zero_shot_radio = tk.Radiobutton(self.radio_buttons_frame, text="Zero-shot", variable=self.prompt_method, value="zero-shot", font=("Arial", 11), fg="#374151", selectcolor="#e0e7ff") # Added fg and selectcolor
        self.zero_shot_radio.pack(side=tk.LEFT, padx=10, pady=5)

        self.few_shot_radio = tk.Radiobutton(self.radio_buttons_frame, text="Few-shot", variable=self.prompt_method, value="few-shot", font=("Arial", 11), fg="#374151", selectcolor="#e0e7ff")
        self.few_shot_radio.pack(side=tk.LEFT, padx=10, pady=5)

        self.chain_of_thought_radio = tk.Radiobutton(self.radio_buttons_frame, text="Chain-of-Thought", variable=self.prompt_method, value="chain-of-thought", font=("Arial", 11), fg="#374151", selectcolor="#e0e7ff")
        self.chain_of_thought_radio.pack(side=tk.LEFT, padx=10, pady=5)

        # Message/Loading Indicator
        self.message_label = tk.Label(master, text="", font=("Arial", 11), wraplength=780) # Added wraplength
        self.message_label.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Generate Button
        self.generate_button = tk.Button(master, text="Generate Story", command=self.start_story_generation,
                                         font=("Arial", 14, "bold"), bg="#4f46e5", fg="white",
                                         activebackground="#6366f1", activeforeground="white",
                                         relief=tk.RAISED, bd=4, cursor="hand2") # Added cursor
        self.generate_button.grid(row=4, column=0, pady=20, padx=10, sticky="ew")

        # Story Output Frame
        self.output_frame = tk.Frame(master, padx=10, pady=5)
        self.output_frame.grid(row=5, column=0, sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1) # Text area expands

        self.output_label = tk.Label(self.output_frame, text="Generated Story:", font=("Arial", 12, "bold"))
        self.output_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.story_output = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, font=("Arial", 11), bd=2, relief=tk.SUNKEN, bg="#f9fafb") # Added background color
        self.story_output.grid(row=1, column=0, sticky="nsew") # sticky="nsew" makes it expand

        # Read/Stop Buttons Frame
        self.tts_button_frame = tk.Frame(master, padx=10, pady=10)
        self.tts_button_frame.grid(row=6, column=0, sticky="ew")
        self.tts_button_frame.grid_columnconfigure(0, weight=1)
        self.tts_button_frame.grid_columnconfigure(1, weight=1)

        self.read_button = tk.Button(self.tts_button_frame, text="Read Story", command=self.start_reading_story,
                                     font=("Arial", 12, "bold"), bg="#28a745", fg="white",
                                     activebackground="#218838", activeforeground="white",
                                     relief=tk.RAISED, bd=3, cursor="hand2")
        self.read_button.grid(row=0, column=0, padx=5, sticky="ew")
        # Initially disable read button until a story is generated
        self.read_button.config(state=tk.DISABLED if not self.tts_engine_ready else tk.NORMAL)


        self.stop_button = tk.Button(self.tts_button_frame, text="Stop Reading", command=self.stop_reading_story,
                                     font=("Arial", 12, "bold"), bg="#dc3545", fg="white",
                                     activebackground="#c82333", activeforeground="white",
                                     relief=tk.RAISED, bd=3, cursor="hand2")
        self.stop_button.grid(row=0, column=1, padx=5, sticky="ew")
        # Initially disable stop button
        self.stop_button.config(state=tk.DISABLED)

    def show_message(self, message, is_error=False):
        """Displays a message in the message label with appropriate color."""
        self.message_label.config(text=message, fg="red" if is_error else "#2563eb") # Blue for info, red for error

    def clear_message(self):
        """Clears the message label."""
        self.message_label.config(text="")

    def set_inputs_state(self, state):
        """Sets the state of input widgets (tk.NORMAL or tk.DISABLED)."""
        self.prompt_entry.config(state=state)
        self.zero_shot_radio.config(state=state)
        self.few_shot_radio.config(state=state)
        self.chain_of_thought_radio.config(state=state)
        self.generate_button.config(state=state)
        # Disable TTS buttons when other inputs are disabled (e.g., during generation)
        self.read_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)


    def start_story_generation(self):
        """Starts the story generation process in a separate thread."""
        user_prompt = self.prompt_entry.get().strip()
        if not user_prompt:
            self.show_message("Please enter a story prompt.", is_error=True)
            return

        self.clear_message()
        self.story_output.delete(1.0, tk.END) # Clear previous story
        self.story_output.insert(tk.END, "Generating story... Please wait.")
        self.set_inputs_state(tk.DISABLED) # Disable inputs during generation

        # Run the API call in a separate thread to prevent GUI freezing
        threading.Thread(target=self._generate_story_thread, args=(user_prompt,)).start()

    def _generate_story_thread(self, user_prompt):
        """
        Threaded function to handle story generation and API call.
        Updates GUI elements from the main thread using after().
        """
        selected_method = self.prompt_method.get()
        full_prompt = ""

        if selected_method == "zero-shot":
            full_prompt = generate_zero_shot_prompt(user_prompt)
        elif selected_method == "few-shot":
            full_prompt = generate_few_shot_prompt(user_prompt)
        elif selected_method == "chain-of-thought":
            full_prompt = generate_chain_of_thought_prompt(user_prompt)
        else:
            full_prompt = generate_zero_shot_prompt(user_prompt) # Fallback

        generated_story = get_story_from_gemini(full_prompt)

        # Update GUI elements back on the main thread
        self.master.after(0, self._update_gui_after_generation, generated_story)

    def _update_gui_after_generation(self, generated_story):
        """Updates the GUI after story generation is complete."""
        self.story_output.delete(1.0, tk.END)
        self.story_output.insert(tk.END, generated_story)
        self.set_inputs_state(tk.NORMAL) # Re-enable inputs

        if "Error:" in generated_story or "Could not generate" in generated_story:
            self.show_message("Story generation failed. See output for details.", is_error=True)
            self.read_button.config(state=tk.DISABLED) # Keep read button disabled on error
        else:
            self.show_message("Story generated successfully!", is_error=False) # Success message
            if self.tts_engine_ready:
                self.read_button.config(state=tk.NORMAL) # Enable read button if TTS is ready

    def start_reading_story(self):
        """Starts reading the story aloud in a separate thread."""
        if not self.tts_engine_ready:
            messagebox.showwarning("TTS Not Ready", "Text-to-Speech engine is not available.")
            return

        story_text = self.story_output.get(1.0, tk.END).strip()
        if not story_text or story_text == "Generating story... Please wait.":
            self.show_message("No story to read.", is_error=True)
            return

        self.read_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.show_message("Reading story...", is_error=False)

        # Start TTS in a new thread
        threading.Thread(target=self._read_story_thread, args=(story_text,)).start()

    def _read_story_thread(self, text):
        """Threaded function to handle TTS."""
        if self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            # After speech is done, update button states on the main thread
            self.master.after(0, self._update_tts_buttons_after_speech)

    def stop_reading_story(self):
        """Stops the current story narration."""
        if self.tts_engine:
            self.tts_engine.stop()
            self.show_message("Story narration stopped.", is_error=False)
            self.read_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def _update_tts_buttons_after_speech(self):
        """Updates TTS button states after speech finishes naturally."""
        self.read_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.clear_message() # Clear "Reading story..." message

if __name__ == "__main__":
    root = tk.Tk()
    app = StoryGeneratorApp(root)
    root.mainloop()
