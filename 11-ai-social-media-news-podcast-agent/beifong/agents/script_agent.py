from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from textwrap import dedent
from datetime import datetime


load_dotenv()


class Dialog(BaseModel):
    speaker: str = Field(...)
    text: str = Field(...)


class Section(BaseModel):
    type: str = Field(...)
    title: Optional[str] = Field(None)
    dialog: List[Dialog] = Field(...)


class PodcastScript(BaseModel):
    title: str = Field(...)
    sections: List[Section] = Field(...)


PODCAST_AGENT_DESCRIPTION = """
You are a helpful podcast script writer.
Create clear, engaging and informative podcast scripts.
"""


PODCAST_AGENT_INSTRUCTIONS = dedent("""
    You are a podcast script writer.

    Create an engaging podcast discussion from the provided news sources.

    The podcast has two hosts:

    ALEX:
    - Analytical
    - Fact-focused
    - Explains important details
    - Discusses why the news matters

    MORGAN:
    - Focuses on human impact
    - Discusses practical effects
    - Adds social and ethical context
    - Keeps the conversation natural

    Podcast structure:

    1. Introduction
    2. Main news headlines
    3. Detailed discussion of important stories
    4. Broader impact and future implications
    5. Conclusion

    Keep the conversation natural and interesting.

    Use only information available in the provided sources.
    Do not invent facts, URLs, statistics or events.

    Write the podcast in the requested language.

    Clearly label speakers as:

    ALEX:
    MORGAN:

    Include the source titles when discussing stories.
""")


def format_search_results_for_podcast(
    search_results: List[dict],
) -> tuple[str, List[str]]:

    created_at = datetime.now().strftime(
        "%B %d, %Y at %I:%M %p"
    )

    structured_content = [
        f"PODCAST CREATION: {created_at}\n"
    ]

    sources = []

    for idx, search_result in enumerate(search_results):

        try:
            title = search_result.get(
                "title",
                "Untitled Source"
            )

            url = search_result.get(
                "url",
                ""
            )

            description = search_result.get(
                "description",
                ""
            )

            full_text = search_result.get(
                "full_text",
                ""
            )

            content = full_text or description

            if title or content:

                if url:
                    sources.append(url)

                structured_content.append(
                    f"""
SOURCE {idx + 1}

Title:
{title}

URL:
{url}

Content:
{content}

--- END SOURCE ---
""".strip()
                )

        except Exception as e:
            print(
                f"Error processing search result: {e}"
            )

    content_texts = "\n\n".join(
        structured_content
    )

    return content_texts, sources


def podcast_script_agent_run(
    agent: Agent,
    query: str,
    language_name: str,
) -> str:

    """
    Generate a podcast script from the current
    session's search results.
    """

    from services.internal_session_service import (
        SessionService
    )

    session_id = agent.session_id

    session = SessionService.get_session(
        session_id
    )

    session_state = session["state"]

    print(
        "Podcast Script Agent Input:",
        query
    )

    search_results = session_state.get(
        "search_results",
        []
    )

    if not search_results:
        return (
            "No search results found to generate "
            "the podcast script."
        )

    content_texts, sources = (
        format_search_results_for_podcast(
            search_results
        )
    )

    if not content_texts:
        return (
            "No useful sources found to generate "
            "podcast script."
        )

    podcast_script_agent = Agent(
        model=Ollama(
            id="qwen2.5:0.5b"
        ),
        instructions=PODCAST_AGENT_INSTRUCTIONS,
        description=PODCAST_AGENT_DESCRIPTION,
        session_id=session_id,
    )

    prompt = f"""
Create a podcast script about:

{query}

Language:
{language_name}

Use these sources:

{content_texts}

Write the complete conversation in {language_name}.

Use this format:

ALEX: ...
MORGAN: ...

Start with a short introduction, discuss the
important stories, explain why they matter,
discuss broader impact, and finish with a
short conclusion.
"""

    response = podcast_script_agent.run(
        prompt,
        session_id=session_id,
    )

    script_text = response.content

    session_state["generated_script"] = {
        "title": f"{query} - Podcast",
        "language": language_name,
        "sources": sources,
        "script": script_text,
        "created_at": datetime.now().isoformat(),
    }

    session_state["stage"] = "script"

    SessionService.save_session(
        session_id,
        session_state
    )

    if not script_text:
        return (
            "Failed to generate podcast script."
        )

    return (
        f"Generated podcast script for "
        f"'{query}' using "
        f"{len(sources)} sources.\n\n"
        f"{script_text}"
    )