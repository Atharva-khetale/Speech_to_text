# 🗣️ Real-Time Speech-to-Text Pro

**Real-Time Speech-to-Text Pro** is an intelligent desktop application built using Python and `Tkinter` that transforms live spoken language into text in real-time. With multilingual support, session management, and user-friendly controls, this tool empowers users to transcribe audio efficiently — whether for accessibility, content creation, note-taking, or productivity.

---

## 🚀 Features

- 🎙️ **Live Speech Recognition** using Google’s Speech Recognition API  
- 🌐 **Multi-Language Support** with real-time switching (supports 14+ global languages)
- 📝 **Session Management**  
  - Start, Pause, Resume, and End sessions  
  - Save sessions locally as `.txt`, `.pdf`, or `.docx`  
  - Access and export past session history  
- 💬 **Real-Time Text Display** with smart word highlighting
- 🎛️ **Interactive GUI** built with `Tkinter` and `ttk`
- 🔧 **Ambient Noise Calibration** for more accurate transcription
- 💾 **File Dialog Integration** for saving and exporting sessions

---

## 🛠️ Tech Stack

| Component          | Tech Used                        |
|-------------------|----------------------------------|
| GUI Framework      | `Tkinter` + `ttk`                |
| Speech Recognition | `speech_recognition` (Google API)|
| Audio Handling     | `pyaudio`                        |
| Multithreading     | `threading`, `queue`             |
| File Management    | `filedialog`, `os`, `time`       |

---

## 📸 GUI Overview

- **Top Control Panel**: Start, Pause, Language Dropdown, Session Options  
- **Tabbed Notebook**:  
  - *Current Session*: Live transcription  
  - *Session History*: Past sessions, view & export  
- **Status Bar**: Real-time status messages for actions, errors, and language selection

---

## 🔧 Installation & Setup

### 📦 Requirements

- Python 3.7+
- Install dependencies:
  ```bash
  pip install speechrecognition
  pip install pyaudio
  pip install ttkthemes
