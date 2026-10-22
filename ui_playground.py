# ui_playground.py

import os
from datetime import date
from dotenv import load_dotenv

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

from phi.agent import Agent
from phi.model.groq import Groq
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.playground import Playground, serve_playground_app


# 1. ENVIRONMENT CONFIGURATION

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Add it to your .env file."
    )

MODEL_ID = os.getenv(
    "GROQ_MODEL_ID",
    "qwen/qwen3.8-27b"
)

DB_FILE = "agents.db"


# 2. GROQ MODEL

def get_model():
    return Groq(
        id=MODEL_ID,
        api_key=GROQ_API_KEY,
        temperature=0.1
    )


# 3. WEB RESEARCH AGENT

web_agent = Agent(
    name="Web Agent",

    role=(
        "Search the web for recent information "
        "and provide reliable sources."
    ),

    model=get_model(),

    tools=[
        DuckDuckGo(
            search=True,
            news=False,
            fixed_max_results=3,
            timeout=10
        )
    ],

    tool_call_limit=1,

    instructions=[
        "You are an expert web research assistant.",

        f"Today's date is {date.today().isoformat()}.",

        "Use web search to retrieve relevant information.",

        "Perform at most one web search per request.",

        "Never repeat a failed search.",

        "If a search fails, explain that the information "
        "could not be verified.",

        "Only report findings supported by retrieved sources.",

        "Include source URLs whenever available.",

        "Keep answers concise and well structured."
    ],

    storage=SqlAgentStorage(
        table_name="web_agent",
        db_file=DB_FILE
    ),

    add_history_to_messages=True,

    show_tool_calls=False,
    markdown=True,
    debug_mode=False
)


# 4. FINANCIAL ANALYST AGENT

finance_agent = Agent(
    name="Finance Agent",

    role=(
        "Analyze stock prices, financial fundamentals "
        "and analyst recommendations."
    ),

    model=get_model(),

    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_info=True,
            company_news=True
        )
    ],

    tool_call_limit=4,

    instructions=[
        "You are an expert financial research assistant.",

        "Use Yahoo Finance tools to retrieve financial data.",

        "Retrieve stock prices, fundamentals and analyst ratings.",

        "Use Markdown tables when comparing financial data.",

        "Make no more than four tool calls per request.",

        "Never retry a failed tool call.",

        "Do not fabricate financial information.",

        "Clearly state when data is unavailable.",

        "Mention the data date when available.",

        "Provide concise and understandable explanations."
    ],

    storage=SqlAgentStorage(
        table_name="finance_agent",
        db_file=DB_FILE
    ),

    add_history_to_messages=True,

    show_tool_calls=False,
    markdown=True,
    debug_mode=False
)


# 5. CREATE PHIDATA PLAYGROUND APPLICATION

app = Playground(
    agents=[
        finance_agent,
        web_agent
    ]
).get_app()


# 6. LOCAL WEB INTERFACE

@app.get("/", response_class=HTMLResponse)
async def homepage():

    return """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Financial AI Advisor</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            margin: 0;
            padding: 0;
            color: #1e293b;
        }

        header {
            background: #0f172a;
            color: white;
            text-align: center;
            padding: 30px 20px;
        }

        header h1 {
            margin: 0;
            font-size: 30px;
        }

        header p {
            color: #cbd5e1;
        }

        .container {
            max-width: 950px;
            margin: 35px auto;
            padding: 25px;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.07);
        }

        h2 {
            color: #0f172a;
        }

        select, textarea {
            width: 100%;
            padding: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 15px;
            margin-top: 10px;
        }

        textarea {
            min-height: 120px;
            resize: vertical;
        }

        button {
            background: #2563eb;
            color: white;
            border: none;
            padding: 13px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 15px;
        }

        button:hover {
            background: #1d4ed8;
        }

        button:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }

        #response {
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            line-height: 1.7;
            min-height: 100px;
        }

        .status {
            font-size: 14px;
            color: #64748b;
            margin-top: 10px;
        }

        a {
            color: #2563eb;
        }

    </style>

</head>

<body>

<header>

    <h1>Financial AI Advisor</h1>

    <p>
        Groq-Powered Financial Research and Web Analysis
    </p>

</header>


<div class="container">

    <div class="card">

        <h2>Select AI Agent</h2>

        <select id="agent">

            <option value="finance">
                Financial Analyst
            </option>

            <option value="web">
                Web Researcher
            </option>

        </select>

        <h2>Ask Your Question</h2>

        <textarea id="question"
            placeholder="Example: Analyze Nvidia stock and its analyst recommendations."></textarea>

        <button id="askButton" onclick="askAgent()">
            Ask AI Agent
        </button>

        <p class="status" id="status"></p>

    </div>


    <div class="card">

        <h2>AI Response</h2>

        <div id="response">
            Your AI response will appear here.
        </div>

    </div>


    <div class="card">

        <h2>Application Details</h2>

        <p><b>LLM Provider:</b> Groq</p>

        <p><b>Framework:</b> Phidata</p>

        <p><b>Financial Data:</b> Yahoo Finance</p>

        <p><b>Web Search:</b> DuckDuckGo</p>

        <p><b>Conversation Storage:</b> SQLite</p>

        <p>
            <a href="/docs" target="_blank">
                FastAPI Documentation
            </a>
        </p>

    </div>

</div>


<script>

async function askAgent() {

    const agent = document.getElementById("agent").value;

    const question = document.getElementById("question").value.trim();

    const responseDiv = document.getElementById("response");

    const status = document.getElementById("status");

    const button = document.getElementById("askButton");

    if (!question) {
        alert("Please enter your question.");
        return;
    }

    button.disabled = true;

    status.innerText = "Analyzing your question...";

    responseDiv.innerText = "";

    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                agent: agent,
                question: question
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }

        responseDiv.innerText = data.response;

        status.innerText = "Analysis completed.";

    }

    catch (error) {

        responseDiv.innerText = "Error: " + error.message;

        status.innerText = "Request failed.";

    }

    finally {
        button.disabled = false;
    }

}

</script>

</body>
</html>
"""


# 7. API ENDPOINT FOR AI RESPONSES

@app.post("/ask")
async def ask_agent(request: Request):

    try:

        data = await request.json()

        agent_name = data.get("agent", "finance")

        question = data.get("question", "").strip()

        if not question:
            return JSONResponse(
                status_code=400,
                content={"error": "Question cannot be empty."}
            )

        if agent_name == "finance":
            selected_agent = finance_agent

        elif agent_name == "web":
            selected_agent = web_agent

        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid agent selected."}
            )

        # Generate response without streaming
        result = selected_agent.run(
            question,
            stream=False
        )

        answer = result.content

        if answer is None:
            answer = "The agent did not return a response."

        return JSONResponse(
            content={
                "agent": agent_name,
                "question": question,
                "response": str(answer)
            }
        )

    except Exception as error:

        print(f"Agent error: {error}")

        return JSONResponse(
            status_code=500,
            content={
                "error": (
                    "The agent could not complete the request. "
                    "Check the server logs for details."
                )
            }
        )


# 8. HEALTH CHECK

@app.get("/health")
async def health():

    return {
        "status": "running",
        "provider": "Groq",
        "model": MODEL_ID,
        "agents": [
            "Finance Agent",
            "Web Agent"
        ]
    }


# 9. START APPLICATION

if __name__ == "__main__":

    print("\nFinancial AI Advisor")
    print("----------------------------")
    print(f"Model: {MODEL_ID}")
    print("Server: http://localhost:7777")
    print("API Docs: http://localhost:7777/docs")
    print("Health: http://localhost:7777/health")
    print("----------------------------\n")

    serve_playground_app(
        "ui_playground:app",
        reload=False
    )