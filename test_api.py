# test_api.py

import os
from dotenv import load_dotenv

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools


# Load Groq API key
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")


# Company symbol mapping
def get_company_symbol(company: str) -> str:
    """
    Retrieve stock ticker symbol for a company.
    """

    symbols = {
        "apple": "AAPL",
        "tesla": "TSLA",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "microsoft": "MSFT",
        "amazon": "AMZN",
        "nvidia": "NVDA",
        "meta": "META",
        "netflix": "NFLX",
        "intel": "INTC",
        "amd": "AMD",
    }

    return symbols.get(company.strip().lower(), "Unknown")


# Financial AI Agent
test_agent = Agent(

    name="Financial Analyst",

    model=Groq(
        id="qwen/qwen3.8-27b",
        api_key=GROQ_API_KEY
    ),

    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True
        ),
        get_company_symbol
    ],

    show_tool_calls=True,

    markdown=True,

    instructions=[
        "You are an expert financial research assistant.",
        "Always use get_company_symbol to retrieve ticker symbols.",
        "Only analyze companies whose ticker symbols are recognized.",
        "Use Yahoo Finance to retrieve financial information.",
        "Always create tables for stock comparisons.",
        "Explain analyst recommendations clearly.",
        "Never fabricate financial data."
    ],

    debug_mode=True
)


if __name__ == "__main__":

    test_agent.print_response(
        "Summarise and compare the analyst recommendations "
        "for Apple, Tesla, and Nvidia.",
        stream=True
    )