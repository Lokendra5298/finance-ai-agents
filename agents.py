# agents.py

import os
from datetime import date
from dotenv import load_dotenv

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools


# 1. Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")


# 2. Configure Groq model
MODEL_ID = "qwen/qwen3.8-27b"


def get_model():
    return Groq(
        id=MODEL_ID,
        api_key=GROQ_API_KEY,
        temperature=0.1
    )


# 3. Financial Analyst Agent
financial_agent = Agent(
    name="Financial Analyst",

    role="Analyze stock fundamentals and analyst recommendations.",

    model=get_model(),

    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True
        )
    ],

    tool_call_limit=3,

    show_tool_calls=False,
    markdown=True,
    debug_mode=False,

    instructions=[
        "You are a financial analyst.",
        "Use Yahoo Finance to retrieve financial information.",
        "Make at most 3 tool calls.",
        "Do not repeat failed tool calls.",
        "If financial data is unavailable, state that clearly.",
        "Summarize analyst recommendations in a Markdown table.",
        "Do not fabricate financial information.",
        "Provide a final response after retrieving available data."
    ]
)


# 4. Web Researcher Agent
web_researcher = Agent(
    name="Web Researcher",

    role="Research recent company news and market developments.",

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

    show_tool_calls=False,
    markdown=True,
    debug_mode=False,

    instructions=[
        "You are a financial news researcher.",

        f"Today's date is {date.today().isoformat()}.",
        "Search for recent company news.",
        "Perform only ONE web search.",
        "Never retry a failed search.",
        "If the search fails or returns no results, "
        "report that recent news could not be verified.",
        "Do not attempt alternative search queries.",
        "Only report news supported by retrieved sources.",
        "Include source links and publication dates when available.",
        "Provide a concise final summary."
    ]
)


# 5. Multi-Agent Team
agents_team = Agent(
    name="Financial Research Team",

    team=[
        financial_agent,
        web_researcher
    ],

    model=get_model(),

    tool_call_limit=2,

    show_tool_calls=False,
    markdown=True,
    debug_mode=False,

    instructions=[
        "You coordinate a financial research team.",
        "Delegate financial analysis to Financial Analyst.",
        "Delegate news research to Web Researcher.",
        "Delegate each task only once.",
        "Do not repeatedly delegate the same task.",
        "Do not retry a failed agent task.",
        "If an agent fails, summarize available information.",
        "Always provide a final response.",
        "Use Markdown tables for financial comparisons.",
        "Include verified source links.",
        "Do not fabricate missing information.",
        "Keep the final response concise and informative."
    ]
)


# 6. Run Multi-Agent System
if __name__ == "__main__":

    query = (
        "Summarise the analyst recommendations "
        "and share the latest information about Nvidia."
    )

    try:
        agents_team.print_response(
            query,
            stream=False
        )

    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")

    except Exception as e:
        print(f"\nAgent execution failed: {e}")