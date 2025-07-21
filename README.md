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
git clone [https://github.com/AdityaRana-beepbeep/Prompt-Engineering-Story-App.git]
cd [Prompt-Engineering-Story-App]
