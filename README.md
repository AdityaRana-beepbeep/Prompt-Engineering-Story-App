# 📖 AI Story Generator Desktop Application

## ✨ Overview

This project is a desktop application that generates creative stories using Google's powerful Gemini API. It's designed to showcase and allow experimentation with different **Prompt Engineering** techniques: Zero-shot, Few-shot, and Chain-of-Thought prompting.

A key new feature is the integration of **Text-to-Speech (TTS)**, enabling the application to read the generated stories aloud, enhancing accessibility and providing a more immersive user experience.

## 🚀 Features

* **Zero-shot Prompting:** Generate stories directly from a simple topic or prompt, relying solely on the model's pre-trained knowledge.
* **Few-shot Prompting:** Guide the AI with a few examples of input-output pairs to steer the story generation towards a desired style, tone, or structure.
* **Chain-of-Thought Prompting (CoT):** Encourage the AI to "think step-by-step" by breaking down the complex task of story creation into smaller, logical reasoning steps, often leading to more coherent and detailed narratives.
* **Voice Recitation (TTS):** Listen to your generated stories aloud with integrated Text-to-Speech functionality.
* **User-Friendly GUI:** An intuitive graphical interface built with Tkinter for easy interaction.

## 🛠️ Technologies Used

* **Python 3.x:** The core programming language for the application logic.
* **Tkinter:** Python's standard GUI (Graphical User Interface) toolkit, used for building the desktop application's interface.
* **Requests:** A popular Python library for making HTTP requests to external APIs.
* **pyttsx3:** A cross-platform Python library for Text-to-Speech conversion, utilizing the speech synthesis engines available on the operating system.
* **Google Gemini API (Generative Language API):** The powerful Large Language Model (LLM) API from Google that generates the story content.

## ⚙️ How to Run Locally

Follow these steps to set up and run the AI Story Generator on your local machine.

### 1. Clone the Repository

First, clone this GitHub repository to your local machine:

```bash
git clone [[https://github.com/]https://github.com/AdityaRana-beepbeep/Prompt-Engineering-Story-App].git
cd [Prompt-Engineering-App]
2. Install Dependencies
You'll need to install the required Python libraries. It's recommended to use a virtual environment.

Bash

# Create a virtual environment (optional but recommended)
python -m venv venv
# Activate the virtual environment
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install the necessary Python packages
pip install requests pyttsx3
Note on pyttsx3:
pyttsx3 relies on your operating system's built-in Text-to-Speech engines.

Windows: Usually works out-of-the-box with Microsoft SAPI.

macOS: Uses NSSpeechSynthesizer, typically works without extra setup.

Linux: You might need to install espeak or festival if you don't have a default TTS engine. For example, on Debian/Ubuntu:

Bash

sudo apt-get install espeak
3. Obtain and Configure Your Google Gemini API Key
Your application needs an API key to communicate with the Google Gemini API.

Go to Google AI Studio: Open your web browser and navigate to https://aistudio.google.com/app/apikey.

Log in: Ensure you are logged in with the Google account associated with your Google Cloud project.

Create/Select Project: Click "Get API key" and select "Create API Key in existing project". Choose your Google Cloud project (e.g., "story generator") from the dropdown.

Copy Your API Key: A new API key will be generated and displayed. Copy this entire key string carefully.

Configure API Key Restrictions (CRITICAL for security and functionality):

On the API key details page (usually opens after creation, or accessible by clicking the key name), find the "Application restrictions" and "API restrictions" sections.

Application restrictions: Select "None". This allows your desktop application to use the key from your local machine.

API restrictions: Select "Restrict key". From the dropdown list, find and select "Generative Language API". This explicitly authorizes your key to access the Gemini model.

Click "Save" at the bottom of the page.

4. Insert Your API Key into the Script
Open the desktop_story_generator.py file in a text editor.

Locate the line:

Python

api_key = "YOUR_API_KEY_HERE"
Replace "YOUR_API_KEY_HERE" with the exact API key you copied from Google AI Studio. Ensure the key is enclosed in double quotes.

Python

api_key = "AIzaSyBZXfaKk2g5klZfoNaOtIWriYO1IiuKsw8_your_actual_full_key_here"
Save the desktop_story_generator.py file.

⚠️ Security Warning: For production applications, hardcoding API keys is not recommended. Consider using environment variables or a secure secret management system. For this personal project, ensuring desktop_story_generator.py is in your .gitignore file (which it should be if you followed initial setup) prevents it from being committed to GitHub.

5. Run the Application
Now you can run the desktop application:

Bash

python desktop_story_generator.py
A GUI window will appear, allowing you to generate and listen to AI-powered stories!

📸 Screenshots / Demo
<img width="1919" height="1199" alt="Screenshot 2025-07-21 104220" src="https://github.com/user-attachments/assets/14e33edd-3847-434b-8b51-a5a38c5756bd" />

💡 Future Enhancements
Allow users to select different voices or adjust speech rate/volume.

Add a "Save Story" feature to export generated text to a file.

Implement a history of generated stories.

Explore more advanced prompt engineering techniques or custom instructions.

Integrate image generation based on story themes (requires more complex APIs and rendering).

📄 License
This project is open-source and available under the MIT License. (You might want to create a LICENSE file in your repo with the MIT license text)
