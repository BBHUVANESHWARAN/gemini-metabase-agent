# gemini-metabase-agent
Gradio + Gemini + Metabase AI Agent project

# 🧠 Gemini-Powered Metabase Agent

This is a Natural Language to SQL Gradio app that uses **Google Gemini** to convert questions into SQL and visualize data with **Metabase**. It supports table output and automatic chart generation (Bar, Line, Pie) — all through natural language queries!

## 🚀 Features

- 🔎 Ask any natural language question related to your database
- 🤖 Gemini API generates SQL automatically using live database schema
- 📊 Query results returned as:
  - Table (pandas dataframe)
  - Metabase charts (Bar, Line, Pie)
- 🧱 Full schema is retrieved dynamically from Metabase
- 🖼️ Gradio frontend for easy interaction

---

## 📂 Project Structure

gemini-metabase-agent/
│
├── app.py # Main application code (Gradio + Metabase logic)
├── .env # API keys and environment config
├── requirements.txt # All Python dependencies
└── README.md # This file


---

## ⚙️ Setup Instructions

### 1. 🔑 Create a `.env` file

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
METABASE_URL=http://localhost:3000
METABASE_USERNAME=your_email@example.com
METABASE_PASSWORD=your_metabase_password
DATABASE_ID=2

2. 🐍 Install dependencies

pip install -r requirements.txt

3. ▶️ Run the App Locally

python app.py
