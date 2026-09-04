import json
import uuid
from fastapi import status
from fastapi.responses import JSONResponse

from db.agent_config_v2 import AVAILABLE_LANGS
from services.internal_session_service import SessionService

from agno.agent import Agent
from agno.models.ollama import Ollama

from agents.search_agent import search_agent_run
from agents.scrape_agent import scrape_agent_run
from agents.script_agent import podcast_script_agent_run


class PodcastAgentService:
    """Lightweight local podcast agent service."""

    def __init__(self):
        pass

    async def create_session(self, request=None):
        """Create a new local podcast session."""

        if request and request.session_id:
            try:
                SessionService.get_session(
                    request.session_id
                )

                return {
                    "session_id": request.session_id
                }

            except Exception:
                pass

        session_id = str(uuid.uuid4())

        # Initialize the SQLite session
        SessionService.get_session(session_id)

        return {
            "session_id": session_id
        }

    async def chat(self, request):
        """
        Process a user request directly using:

        Search → Scrape → Script
        """

        try:
            session_id = request.session_id
            message = request.message.strip()

            if not message:
                return {
                    "session_id": session_id,
                    "response": "Please enter a topic.",
                    "stage": "idle",
                    "session_state": "{}",
                    "is_processing": False,
                    "process_type": None,
                }

            print(
                f"Processing request for session "
                f"{session_id}: {message}"
            )

            # Make sure session exists
            session = SessionService.get_session(
                session_id
            )

            session_state = session.get(
                "state",
                {}
            )

            # ---------------------------------
            # Stage 1: Search
            # ---------------------------------

            agent = Agent(
                model=Ollama(
                    id="qwen2.5:0.5b"
                ),
                session_id=session_id,
            )

            search_response = search_agent_run(
                agent,
                message
            )

            print(
                "Search stage completed."
            )

            # ---------------------------------
            # Stage 2: Scrape
            # ---------------------------------

            scrape_response = scrape_agent_run(
                agent,
                message
            )

            print(
                "Scrape stage completed."
            )

            # ---------------------------------
            # Stage 3: Podcast Script
            # ---------------------------------

            script_response = (
                podcast_script_agent_run(
                    agent,
                    message,
                    "English"
                )
            )

            print(
                "Podcast script stage completed."
            )

            # Get final state
            session = SessionService.get_session(
                session_id
            )

            session_state = session.get(
                "state",
                {}
            )

            return {
                "session_id": session_id,
                "response": script_response,
                "stage": session_state.get(
                    "stage",
                    "script"
                ),
                "session_state": json.dumps(
                    session_state
                ),
                "is_processing": False,
                "process_type": None,
            }

        except Exception as e:

            print(
                f"Error processing request: {e}"
            )

            return JSONResponse(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content={
                    "session_id": request.session_id,
                    "response": (
                        "I encountered an error "
                        f"while processing your request: "
                        f"{str(e)}"
                    ),
                    "stage": "error",
                    "session_state": "{}",
                    "is_processing": False,
                    "process_type": None,
                },
            )

    async def check_result_status(
        self,
        request
    ):
        """Return the current session state."""

        try:

            session = SessionService.get_session(
                request.session_id
            )

            session_state = session.get(
                "state",
                {}
            )

            return {
                "session_id": request.session_id,
                "response": "",
                "stage": session_state.get(
                    "stage",
                    "idle"
                ),
                "session_state": json.dumps(
                    session_state
                ),
                "is_processing": False,
                "process_type": None,
                "task_id": None,
            }

        except Exception as e:

            return JSONResponse(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content={
                    "session_id": request.session_id,
                    "response": str(e),
                    "stage": "error",
                    "session_state": "{}",
                    "is_processing": False,
                },
            )

    async def list_sessions(
        self,
        page=1,
        per_page=10
    ):
        """List local SQLite sessions."""

        try:

            result = SessionService.list_sessions(
                page=page,
                per_page=per_page
            )

            return {
                "sessions": result.get(
                    "items",
                    []
                ),
                "pagination": {
                    "total": result.get(
                        "total",
                        0
                    ),
                    "page": page,
                    "per_page": per_page,
                    "total_pages": result.get(
                        "total_pages",
                        0
                    ),
                },
            }

        except Exception as e:

            return JSONResponse(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content={
                    "error": str(e)
                },
            )

    async def delete_session(
        self,
        session_id: str
    ):
        """Delete a local session."""

        try:

            result = SessionService.delete_session(
                session_id
            )

            return {
                "success": True,
                "message": result.get(
                    "message",
                    "Session deleted."
                ),
            }

        except Exception as e:

            return JSONResponse(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content={
                    "error": str(e)
                },
            )

    async def get_session_history(
        self,
        session_id: str
    ):
        """
        Return basic session information.

        The lightweight local version does not
        depend on Agno's old conversation storage.
        """

        try:

            session = SessionService.get_session(
                session_id
            )

            state = session.get(
                "state",
                {}
            )

            return {
                "session_id": session_id,
                "messages": [],
                "state": json.dumps(state),
                "is_processing": False,
                "process_type": None,
                "task_id": None,
            }

        except Exception as e:

            return JSONResponse(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content={
                    "error": str(e)
                },
            )

    async def get_supported_languages(self):
        return {
            "languages": AVAILABLE_LANGS
        }


podcast_agent_service = PodcastAgentService()