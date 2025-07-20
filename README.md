AI Story Generator Desktop Application

🚀 Project Overview
This project is an interactive desktop application built with Python that leverages the power of the Google Gemini API to generate creative stories. It serves as a practical demonstration of various Prompt Engineering techniques, allowing users to experiment with how different prompting strategies influence AI-generated content.
Whether you're a developer, an AI enthusiast, or just curious about large language models, this application provides a hands-on way to explore the nuances of instructing AI.

✨ Features
Zero-shot Prompting: Generate stories directly from a simple prompt, relying solely on the model's pre-trained knowledge.
Few-shot Prompting: Guide the AI with a few example prompt-story pairs to influence the style, tone, or structure of the generated narrative.
Chain-of-Thought Prompting (CoT): Instruct the AI to "think step by step" by breaking down the story creation process into logical stages (e.g., character, plot, setting), leading to more structured and coherent outputs.
User-Friendly GUI: An intuitive graphical interface built with tkinter for easy interaction.
Responsive Feedback: Clear messages and disabled inputs during generation to indicate application status.

🛠️ Technologies Used
Python 3.x: The core programming language.
Tkinter: Python's standard GUI (Graphical User Interface) toolkit for the desktop application.
Requests: Python library for making HTTP requests to the Gemini API.
Google Gemini API: The large language model powering the story generation.

⚙️ Setup and Installation
Follow these steps to get the application up and running on your local machine:
Clone the Repository (or download the file):
If you're using Git, clone this repository:
git clone https://github.com/AdityaRana-beepbeep/Prompt-Engineering-Story-App.git
Install Dependencies:
This project requires the requests library. You can install it using pip:
pip install requests
Obtain a Google Gemini API Key:
Go to Google AI Studio.
Sign in with your Google account.
Create a new API key.
Copy your API key. Keep it secure!
Configure Your API Key:
Open the desktop_story_generator.py file in a text editor.
Find the line:
api_key = "YOUR_API_KEY_HERE"
Replace "YOUR_API_KEY_HERE" with the actual API key you obtained from Google AI Studio.
Important: Do NOT commit your API key to a public repository. The .gitignore file should prevent this, but always double-check.

🚀 How to Run
•	After completing the setup steps, you can run the application:
•	Open your terminal or command prompt.
•	Navigate to the project directory where desktop_story_generator.py is located.
•	Execute the script:
•	python desktop_story_generator.py
•	A desktop window will appear, ready for you to generate stories!

💡 Usage
Enter a Story Prompt: Type your desired topic or idea into the "Enter your story prompt/topic:" input field.
Choose a Prompting Method: Select one of the radio buttons:
Zero-shot: For a direct, unguided generation.
Few-shot: To provide the model with examples for style/structure.
Chain-of-Thought: To encourage the model to reason through the story creation process.
Generate Story: Click the "Generate Story" button.
View Output: The generated story will appear in the "Generated Story:" text area.

📸 Screenshots
  
  
  <img width="1919" height="1125" alt="Screenshot 2025-07-20 155847" src="https://github.com/user-attachments/assets/49e982ab-9cab-4fd9-bfc9-3e2849ffd307" />

 
  <img width="1919" height="1130" alt="Screenshot 2025-07-20 155918" src="https://github.com/user-attachments/assets/c9eaa9d6-4a32-4e73-9a36-4340b8e593f7" />

 
  <img width="1919" height="1124" alt="Screenshot 2025-07-20 155957" src="https://github.com/user-attachments/assets/d4d1f4bf-12ee-43b3-88a1-e31bd4a1d5be" />

 
🧠 Prompt Engineering Insights
This project highlights the significant impact of prompt design on AI output. By experimenting with the three prompting methods, you can observe:
Zero-shot: Demonstrates the LLM's baseline knowledge and creative capacity.
Few-shot: Shows how providing context and examples can steer the model towards desired formats or tones without fine-tuning.
Chain-of-Thought: Illustrates the power of breaking down complex tasks into smaller, explicit steps, often leading to more logical, detailed, and higher-quality responses. This technique encourages the model to "reason" before generating, mimicking human thought processes.
This application is a great starting point for understanding and practicing effective prompt engineering for generative AI tasks.

📄 License
This project is open-source and available under the MIT License. 

🤝 Contributing
Feel free to fork this repository, open issues, or submit pull requests to improve the application or add new features!
