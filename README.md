# 🧠 Text Summarization Web App

A full-stack AI-powered web application that generates concise summaries from text using both **Transformer-based (T5)** and **NLTK extractive** techniques.

---

## 🚀 Features

* ✨ Transformer-based summarization (T5)
* 📊 NLTK extractive summarization
* 🔍 Compare both models side-by-side
* 📄 Upload files:

  * `.txt`
  * `.pdf`
  * `.docx`
* ⏱ Displays time taken for each summary
* 📉 Compression ratio (original vs summary)
* 📋 Copy summary to clipboard
* ⬇️ Download summary as `.txt`
* 💖 Cute animated loading UI

---

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* Transformers (Hugging Face)
* NLTK
* PyPDF2
* python-docx

### Frontend

* HTML
* CSS (Pastel UI)
* JavaScript (Vanilla)

---

## 📂 Project Structure

```
Text Summarization Tool/
│
├── app.py
├── summarizer.py
├── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── utils/
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/roshini0108/text-summarization-app.git
cd text-summarization-app
```

---

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Download NLTK data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

### 5. Run backend

```bash
python -m uvicorn app:app --reload
```

---

### 6. Open frontend

Open this file in your browser:

```
frontend/index.html
```

---

## 🌐 API Endpoints

### POST `/summarize`

```json
{
  "text": "...",
  "method": "transformer | nltk",
  "summary_length": "short | medium | long"
}
```

---

### POST `/compare`

```json
{
  "text": "...",
  "summary_length": "short | medium | long"
}
```

---

### POST `/upload`

* Upload `.txt`, `.pdf`, `.docx`
* Returns extracted text

---

## 🎯 Future Improvements

* GPU acceleration for faster inference
* User authentication
* Save summary history
* Deployment (Render / Vercel)

---

## 👩‍💻 Author

**Roshini Mutyala**
B.Tech CSE Student | AI & Web Development Enthusiast

---

## ⭐ If you like this project

Give it a star ⭐ on GitHub!
