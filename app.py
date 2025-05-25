import gradio as gr
import google.generativeai as genai
import pandas as pd
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # ✅ Load .env values into environment

# === Load Environment Variables ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
METABASE_URL = os.getenv("METABASE_URL")
USERNAME = os.getenv("METABASE_USERNAME")
PASSWORD = os.getenv("METABASE_PASSWORD")
DATABASE_ID = int(os.getenv("DATABASE_ID"))


# === Configure Gemini ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# === Get Metabase Session Token ===
def get_metabase_token():
    response = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get Metabase token: {response.text}")
    return response.json()["id"]

# === Fetch Full Schema from Metabase ===
def get_full_schema(token):
    headers = {"X-Metabase-Session": token}
    response = requests.get(f"{METABASE_URL}/api/database/{DATABASE_ID}/metadata", headers=headers)
    metadata = response.json()
    
    schema = "Tables:\n"
    for table in metadata["tables"]:
        table_name = table["name"]
        fields = ", ".join([field["name"] for field in table["fields"]])
        schema += f"- {table_name}({fields})\n"
    return schema

# === Query Data (for Table Output) ===
def query_metabase(sql, token):
    headers = {"X-Metabase-Session": token}
    response = requests.post(
        f"{METABASE_URL}/api/dataset",
        headers=headers,
        json={"type": "native", "native": {"query": sql}, "database": DATABASE_ID}
    )
    print("Dataset response:", response.status_code, response.json())  # DEBUG

    if response.status_code != 200:
        raise Exception(f"Query failed: {response.json()}")

    data = response.json()["data"]["rows"]
    columns = response.json()["data"]["cols"]
    col_names = [col["name"] for col in columns]
    df = pd.DataFrame(data, columns=col_names)
    return df

# === Create Chart Card and Return URL ===
from datetime import datetime

def create_metabase_chart_card(sql, chart_type, token):
    headers = {"X-Metabase-Session": token}
    viz_type_map = {
        "Bar": "bar",
        "Line": "line",
        "Pie": "pie"
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    response = requests.post(
        f"{METABASE_URL}/api/card",
        headers=headers,
        json={
            "name": f"AutoChart_{chart_type}_{timestamp}",
            "dataset_query": {
                "type": "native",
                "native": {"query": sql},
                "database": DATABASE_ID
            },
            "display": viz_type_map.get(chart_type, "table"),
            "visualization_settings": {},
        }
    )
    data = response.json()
    if "id" not in data:
        raise Exception(f"Chart creation failed. Response: {data}")

    card_id = data["id"]
    return f"{METABASE_URL}/card/{card_id}"


# === Generate SQL with Live Schema ===
def generate_sql_from_question(question, schema):
    prompt = f"""You are a data analyst. Convert the following natural language question into SQL using the schema provided.

Schema:
{schema}

Question:
{question}

SQL:"""
    response = model.generate_content(prompt)
    sql_code = response.text.strip("```sql\n").strip("```")
    print("Generated SQL:", sql_code)  # DEBUG
    return sql_code

# === Main Pipeline ===
def pipeline(question, chart_type):
    try:
        token = get_metabase_token()
        live_schema = get_full_schema(token)
        sql = generate_sql_from_question(question, live_schema)

        if chart_type == "Table":
            df = query_metabase(sql, token)
            return sql, df, "✅ Table shown below"
        else:
            chart_url = create_metabase_chart_card(sql, chart_type, token)
            markdown_link = f"🔗 [View {chart_type} Chart in Metabase]({chart_url})"
            return sql, None, markdown_link

    except Exception as e:
        return f"❌ Error: {str(e)}", None, None


# === Gradio UI ===
demo = gr.Interface(
    fn=pipeline,
    inputs=[
        gr.Textbox(label="Ask your question"),
        gr.Radio(choices=["Table", "Bar", "Line", "Pie"], label="Chart Type", value="Table")
    ],
    outputs=[
        gr.Textbox(label="Generated SQL"),
        gr.Dataframe(label="Result Table", visible=True),
        gr.Markdown(label="Chart Link / Message")
    ],
    title="🧠 Gemini-Powered Metabase Agent",
    description="Ask in natural language. Automatically generate SQL and visualize your data!"
)


if __name__ == "__main__":
    demo.launch()
