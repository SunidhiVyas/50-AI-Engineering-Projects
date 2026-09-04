from typing import List
from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from agno.tools.duckduckgo import DuckDuckGoTools
from textwrap import dedent

from tools.wikipedia_search import wikipedia_search
from tools.google_news_discovery import google_news_discovery_run
from tools.jikan_search import jikan_search
from tools.social_media_search import (
    social_media_search,
    social_media_trending_search,
)
from tools.search_articles import search_articles


load_dotenv()


class ReturnItem(BaseModel):
    url: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    source_name: str = Field(...)
    tool_used: str = Field(...)
    published_date: str = Field(...)
    is_scrapping_required: bool = Field(...)


class SearchResults(BaseModel):
    items: List[ReturnItem] = Field(...)


SEARCH_AGENT_DESCRIPTION = """
You are a helpful assistant that searches the web for relevant information.
"""

SEARCH_AGENT_INSTRUCTIONS = dedent("""
    You are a helpful news and information search assistant.

    Your job is to search for relevant, recent and high-quality sources.

    For news-related queries, prefer Google News.

    Use DuckDuckGo when general web search is useful.

    Use Wikipedia when the user needs background information.

    Use social media search when social media information is specifically
    requested.

    Return useful and relevant sources only.

    Avoid duplicate sources.

    Prefer reputable sources.

    Keep the final answer concise and easy to understand.

    IMPORTANT:
    Do not invent URLs, titles, dates, or facts.

    IMPORTANT:
    Use the available search tools when needed.
""")


def search_agent_run(agent: Agent, query: str) -> str:
    """
    Search for relevant sources using Google News, DuckDuckGo,
    Wikipedia and other lightweight search tools.
    """

    print("Search Agent Input:", query)

    session_id = agent.session_id

    from services.internal_session_service import SessionService

    # Get current session state
    session = SessionService.get_session(session_id)
    current_state = session["state"]

    # Create the local Qwen search agent
    search_agent = Agent(
        model=Ollama(id="qwen2.5:0.5b"),
        instructions=SEARCH_AGENT_INSTRUCTIONS,
        description=SEARCH_AGENT_DESCRIPTION,
        tools=[
            google_news_discovery_run,
            DuckDuckGoTools(),
            wikipedia_search,
            jikan_search,
            social_media_search,
            social_media_trending_search,
            search_articles,
        ],
        session_id=session_id,
    )

    # Run search
    response = search_agent.run(query, session_id=session_id)

    # Get normal text response
    result_text = response.content

    # Save the search output in our SQLite session
    current_state["stage"] = "search"
    current_state["search_results"] = [
        {
            "url": "",
            "title": "AI Search Results",
            "description": result_text,
            "source_name": "search_agent",
            "tool_used": "Google News / DuckDuckGo",
            "published_date": "",
            "is_scrapping_required": False,
        }
    ]

    SessionService.save_session(
        session_id,
        current_state,
    )

    return (
        f"Found search results about '{query}'.\n\n"
        f"{result_text}"
    )