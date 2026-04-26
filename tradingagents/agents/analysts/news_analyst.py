from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news, get_global_news
from tradingagents.agents.utils.material_facts_tools import get_material_facts
from tradingagents.dataflows.config import get_config


def create_news_analyst(llm):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [
            get_material_facts,
            get_news,
            get_global_news,
        ]

        system_message = (
            "You are a news researcher tasked with analyzing recent news, material facts (Fatos Relevantes), and trends relevant to trading and macroeconomics. "
            "Use the available tools strategically:\n"
            "1. get_material_facts(ticker, trade_date) - Fetch official CVM announcements (highest priority for company-specific analysis)\n"
            "2. get_news(query, start_date, end_date) - Search for company-specific or targeted news\n"
            "3. get_global_news(curr_date, look_back_days, limit) - Broader macroeconomic and market-wide news\n\n"
            "Priority sequence for a stock analysis:\n"
            "- Start with get_material_facts to capture official company announcements\n"
            "- Supplement with company-specific news via get_news\n"
            "- Add global market context via get_global_news\n\n"
            "Material facts (Fatos Relevantes) are official CVM disclosures about events that may significantly impact the stock price. "
            "These carry high credibility and should be weighted heavily in your analysis.\n\n"
            "Do not simply state the trends are mixed; provide detailed and fine-grained analysis with specific insights that may help traders make decisions."
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. We are looking at the company {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node
