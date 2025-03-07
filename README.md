AI Meeting Summarizer - Project Overview
The AI Meeting Summarizer is a web-based application that records, transcribes, summarizes, and translates meetings automatically. It helps users extract key points, decisions, and action items from meetings and allows seamless task export to platforms like Trello, Asana, Jira, GitHub, and Notion.

🚀 Key Features:
✔ Real-Time Audio Recording & Transcription using Vosk Speech Recognition
✔ Upload Audio Files for transcription & summarization
✔ Live Transcription Streaming for ongoing meetings
✔ Automatic Meeting Summaries with key points, decisions, and action items
✔ Task Export to Task Managers (Trello, Asana, GitHub, Jira, Notion)
✔ Multiple Export Formats (Markdown, JSON, CSV, HTML, Text)
✔ Language Translation Support – Meetings can be translated into multiple languages

🛠 Technology Stack
Backend: Flask (Python)
Speech-to-Text: Vosk ASR (Automatic Speech Recognition)
Text Processing: NLP with SpaCy & Transformers (T5 Model)
Audio Handling: PyDub & FFmpeg
Task Management Integration: API calls to Trello, Jira, Asana, GitHub, and Notion
Translation: Language translation support using NLP models
Frontend: HTML, CSS, JavaScript
📌 How It Works
1️⃣ Record or Upload a Meeting
Users can either record a live meeting or upload an audio file for processing.

2️⃣ Speech-to-Text Transcription
The system converts speech to text using the Vosk ASR model.

3️⃣ Automatic Meeting Summarization
The transcript is analyzed using NLP (SpaCy & Transformers) to extract:

Key points
Decisions made
Action items
Participants mentioned
4️⃣ Translate the Transcript
The extracted transcript can be translated into multiple languages using the translation module.

5️⃣ Task Export to Trello, Asana, Jira, GitHub, or Notion
Action items from the meeting can be exported directly to a task manager.

6️⃣ Download Summary in Various Formats
The summarized meeting can be exported as Markdown, JSON, HTML, CSV, or plain text.

![image](https://github.com/user-attachments/assets/c646bfa3-b03b-44fc-93f8-7e6ccf7b0fa8)


