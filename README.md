# Freshservice AI Assistant

An AI system to answer questions about the Freshservice API. It scrapes official documentation and uses a RAG pipeline with Google Gemini LLM for accurate answers.

*cite: Developed for the Artificial Intelligence Intern Assessment.*

---

## 🎯 Problem Statement

The goal is to build a system that can read the Freshservice API docs. Users can then ask questions, and the system gives answers from the scraped data. It must handle dynamic web content and provide accurate answers.

---

## 💡 Solution: AI-Powered RAG System

The system uses a three-phase pipeline: web scraping, RAG processing, and a simple interface.

### Phase 1: Web Scraping

The scraper collects all API documentation from Freshservice. It uses **Selenium** and **BeautifulSoup4** to handle JavaScript-heavy pages. The content is stored in a structured `JSON` file (`output/freshservice_docs.json`).

### Phase 2: RAG Pipeline

The pipeline loads the JSON knowledge base. Text is split into chunks and converted to embeddings using **Sentence-Transformers**. User queries are matched with the most relevant chunks via cosine similarity. Finally, **Google Gemini** generates answers based only on the retrieved data.

### Phase 3: User Interface

The UI is built with **Streamlit**. Users can ask questions in a chat-like interface. Each answer shows the sources and confidence score for transparency.

---

## 🛠️ Tech Stack

* **Language**: Python
* **LLM & RAG**: Google Gemini, Sentence-Transformers, Scikit-learn
* **Web Scraping**: Selenium, BeautifulSoup4
* **UI**: Streamlit
* **Libraries**: Transformers, PyTorch, NumPy

---

## 📂 Project Structure

```
├── .gitignore
├── app.py
├── launch.py
├── rag.py
├── requirements.txt
├── scraper.py
└── output/
    └── freshservice_docs.json
```

---

## 🚀 Getting Started

### 1. Prerequisites

* Python 3.8+
* Git

### 2. Installation & Setup

**Clone the repository**

```bash
git clone https://github.com/<Your-GitHub-Username>/FreshService-Assistant.git
cd FreshService-Assistant
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

### 3. Running the Application

```bash
streamlit run app.py
```

Open the URL in your browser to start interacting with the assistant.

---

## 💡 Example Usage

1. Open the app in your browser.
2. Type a question about the Freshservice API in the chat box.
3. Press Enter or click the send button.
4. The assistant will reply with an answer.
5. Expand the "Sources" section to see where the answer came from.
