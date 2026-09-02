from textwrap import dedent
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.tools.serpapi import SerpApiTools
import streamlit as st
import re
from agno.models.ollama import Ollama
from icalendar import Calendar, Event
from datetime import datetime, timedelta


def generate_ics_content(plan_text: str, start_date: datetime = None) -> bytes:
    """
    Generate an ICS calendar file from a travel itinerary.
    """

    cal = Calendar()
    cal.add("prodid", "-//AI Travel Planner//github.com//")
    cal.add("version", "2.0")

    if start_date is None:
        start_date = datetime.today()

    # Split the itinerary into days
    day_pattern = re.compile(
        r"Day (\d+)[:\s]+(.*?)(?=Day \d+|$)",
        re.DOTALL
    )

    days = day_pattern.findall(plan_text)

    if not days:
        event = Event()
        event.add("summary", "Travel Itinerary")
        event.add("description", plan_text)
        event.add("dtstart", start_date.date())
        event.add("dtend", start_date.date())
        event.add("dtstamp", datetime.now())
        cal.add_component(event)

    else:
        for day_num, day_content in days:
            day_num = int(day_num)

            current_date = start_date + timedelta(days=day_num - 1)

            event = Event()
            event.add(
                "summary",
                f"Day {day_num} Itinerary"
            )
            event.add(
                "description",
                day_content.strip()
            )

            event.add("dtstart", current_date.date())
            event.add("dtend", current_date.date())
            event.add("dtstamp", datetime.now())

            cal.add_component(event)

    return cal.to_ical()


# ---------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------

st.title("🌍 AI Smart Travel Planner")

st.caption(
    "Plan your trip using a local AI model with web research."
)


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None


# ---------------------------------------------------------
# SerpAPI Key
# ---------------------------------------------------------

serp_api_key = st.text_input(
    "Enter SerpAPI Key for search functionality",
    type="password"
)


# ---------------------------------------------------------
# AI Agents
# ---------------------------------------------------------

if serp_api_key:

    researcher = Agent(
        name="Researcher",

        role=(
            "Searches for travel destinations, activities, "
            "food, and accommodations based on user preferences."
        ),

        model=Ollama(
            id="qwen2.5:0.5b"
        ),

        description=dedent(
            """
            You are a travel research assistant.

            Research the destination using web search and
            find useful information about activities,
            attractions, accommodations and food.
            """
        ),

        instructions=[
            "Generate 3 useful search terms for the destination.",
            "Search the web using the available search tool.",
            "Find relevant activities and attractions.",
            "Find suitable accommodations.",
            "Find useful food and restaurant information.",
            "Consider the user's budget and interests.",
            "Return the most useful research results.",
        ],

        tools=[
            SerpApiTools(api_key=serp_api_key)
        ],

        add_datetime_to_context=True,
    )


    planner = Agent(
        name="Planner",

        role=(
            "Creates personalized travel itineraries "
            "using research results."
        ),

        model=Ollama(
            id="qwen2.5:0.5b"
        ),

        description=dedent(
            """
            You are an expert travel planner.

            Create a practical and personalized
            day-by-day travel itinerary.
            """
        ),

        instructions=[
            "Create a day-by-day itinerary.",
            "Prioritize the user's interests.",
            "Respect the user's budget.",
            "Include morning, afternoon and evening activities.",
            "Suggest suitable accommodations.",
            "Suggest local food.",
            "Include estimated costs where possible.",
            "Keep the itinerary practical.",
            "Do not invent facts.",
        ],

        add_datetime_to_context=True,
    )


    # -----------------------------------------------------
    # User Inputs
    # -----------------------------------------------------

    destination = st.text_input(
        "🌍 Where do you want to go?"
    )

    num_days = st.number_input(
        "📅 How many days do you want to travel for?",
        min_value=1,
        max_value=30,
        value=7
    )

    budget = st.number_input(
        "💰 What is your total budget (₹)?",
        min_value=1000,
        max_value=10000000,
        value=50000,
        step=5000
    )

    interests = st.multiselect(
        "🎯 What are your interests?",

        [
            "Beaches",
            "Adventure",
            "Food",
            "Culture",
            "Nature",
            "Shopping",
            "Nightlife",
            "History"
        ],

        default=[
            "Food",
            "Nature"
        ]
    )


    # -----------------------------------------------------
    # Buttons
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


    # -----------------------------------------------------
    # Generate Itinerary
    # -----------------------------------------------------

    with col1:

        if st.button("Generate Itinerary"):

            if not destination:
                st.warning(
                    "Please enter a destination."
                )

            elif not interests:
                st.warning(
                    "Please select at least one interest."
                )

            else:

                # -----------------------------------------
                # Research
                # -----------------------------------------

                with st.spinner(
                    "🔎 Researching your destination..."
                ):

                    research_results: RunOutput = (
                        researcher.run(
                            f"""
                            Research {destination} for
                            a {num_days} day trip.

                            Traveler's budget:
                            ₹{budget}

                            Traveler's interests:
                            {", ".join(interests)}

                            Find useful information about:

                            - Attractions
                            - Activities
                            - Food
                            - Restaurants
                            - Accommodations
                            - Experiences

                            Focus on options suitable for
                            the traveler's interests and budget.
                            """,

                            stream=False
                        )
                    )

                    st.success(
                        "Research completed!"
                    )


                # -----------------------------------------
                # Planning
                # -----------------------------------------

                with st.spinner(
                    "🤖 Creating your personalized itinerary..."
                ):

                    prompt = f"""
                    Destination: {destination}

                    Duration: {num_days} days

                    Total Budget: ₹{budget}

                    Interests:
                    {", ".join(interests)}

                    Research Results:

                    {research_results.content}


                    Create a detailed day-by-day itinerary.

                    Requirements:

                    1. Stay within the total budget
                       of ₹{budget}.

                    2. Prioritize the traveler's interests.

                    3. Include morning, afternoon and
                       evening activities.

                    4. Suggest suitable accommodations.

                    5. Suggest local food and restaurants.

                    6. Include estimated costs where possible.

                    7. Make the itinerary practical and realistic.

                    8. Explain important recommendations.

                    9. Do not invent facts.

                    10. Clearly organize the itinerary as:

                        Day 1
                        Morning:
                        Afternoon:
                        Evening:

                        Day 2
                        Morning:
                        Afternoon:
                        Evening:

                        Continue for all days.
                    """


                    response: RunOutput = planner.run(
                        prompt,
                        stream=False
                    )


                    # Store itinerary
                    st.session_state.itinerary = (
                        response.content
                    )

                    st.write(
                        response.content
                    )


    # -----------------------------------------------------
    # Calendar Download
    # -----------------------------------------------------

    with col2:

        if st.session_state.itinerary:

            ics_content = generate_ics_content(
                st.session_state.itinerary
            )

            st.download_button(
                label="📅 Download Itinerary (.ics)",

                data=ics_content,

                file_name="travel_itinerary.ics",

                mime="text/calendar"
            )