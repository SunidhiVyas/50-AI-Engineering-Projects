import json
from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.firecrawl import FirecrawlTools


# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Life Insurance Advisor",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ AI Life Insurance Advisor")
st.caption(
    "A local AI assistant that estimates life insurance coverage "
    "and researches term-life options."
)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("Configuration")

    firecrawl_api_key = st.text_input(
        "Firecrawl API Key (Optional)",
        type="password",
        help="Used only for fresh insurance-product research.",
    )

    st.markdown("---")

    st.info(
        "🤖 Local Model\n\n"
        "Ollama + Qwen 2.5 0.5B\n\n"
        "No OpenAI API key is required."
    )

    st.markdown("---")

    st.caption(
        "Coverage calculations are performed locally. "
        "Firecrawl is optional and is used only for product research."
    )


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def safe_number(value: Any) -> float:
    """Convert a value into a number safely."""

    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        cleaned = value.strip()

        for token in [",", "$", "€", "£", "₹", "C$", "A$"]:
            cleaned = cleaned.replace(token, "")

        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    return 0.0


def format_currency(amount: float, currency_code: str) -> str:
    """Format an amount using a simple currency symbol."""

    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "CAD": "C$",
        "AUD": "A$",
        "INR": "₹",
    }

    code = (currency_code or "USD").upper()
    symbol = symbols.get(code, "")

    formatted = f"{amount:,.0f}"

    if symbol:
        return f"{symbol}{formatted}"

    return f"{formatted} {code}"


def calculate_coverage(
    annual_income: float,
    income_replacement_years: int,
    total_debt: float,
    savings: float,
    existing_cover: float,
    discount_rate: float = 0.02,
) -> Dict[str, float]:
    """
    Calculate estimated life insurance coverage locally.

    Formula:
    discounted income + debt - savings - existing coverage
    """

    annual_income = safe_number(annual_income)
    total_debt = safe_number(total_debt)
    savings = safe_number(savings)
    existing_cover = safe_number(existing_cover)

    years = max(0, int(income_replacement_years))

    if years == 0:
        annuity_factor = 0.0
        discounted_income = 0.0

    elif discount_rate <= 0:
        annuity_factor = float(years)
        discounted_income = annual_income * years

    else:
        annuity_factor = (
            (1 - (1 + discount_rate) ** (-years))
            / discount_rate
        )

        discounted_income = annual_income * annuity_factor

    assets_offset = savings + existing_cover

    recommended = max(
        0.0,
        discounted_income + total_debt - assets_offset,
    )

    return {
        "income": annual_income,
        "years": years,
        "discount_rate": discount_rate,
        "annuity_factor": annuity_factor,
        "discounted_income": discounted_income,
        "debt": total_debt,
        "savings": savings,
        "existing_cover": existing_cover,
        "assets_offset": assets_offset,
        "recommended": recommended,
    }


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from an LLM response."""

    if not text:
        return None

    text = text.strip()

    # Remove markdown code fences.
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        # Try to find the first JSON object.
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None

    return None


# -----------------------------------------------------------------------------
# Local Ollama Agent
# -----------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_agent(firecrawl_key: str) -> Agent:

    tools = []

    # Firecrawl is optional.
    if firecrawl_key:

        tools.append(
            FirecrawlTools(
                api_key=firecrawl_key,
                enable_search=True,
                enable_crawl=True,
                enable_scrape=False,
                search_params={
                    "limit": 5,
                    "lang": "en",
                },
            )
        )

    return Agent(
        name="AI Life Insurance Advisor",

        model=Ollama(
            id="qwen2.5:0.5b"
        ),

        tools=tools,

        instructions=[
            "You are a conservative life insurance research assistant.",

            "The application performs the coverage calculation locally.",

            "Use the supplied coverage calculation instead of inventing "
            "financial calculations.",

            "If Firecrawl search is available, research current term life "
            "insurance products relevant to the user's location.",

            "Do not claim that a product is the best product.",

            "Present products as research options only.",

            "Never provide licensed financial advice.",

            "Return ONLY valid JSON.",

            "The JSON must contain these keys:",
            "coverage_amount",
            "coverage_currency",
            "breakdown",
            "assumptions",
            "recommendations",
            "research_notes",
            "timestamp",

            "recommendations should contain at most three products.",

            "Each recommendation should contain:",
            "name",
            "summary",
            "link",
            "source",

            "Keep summaries short and factual.",

            "Do not include markdown inside the JSON.",
        ],

        markdown=False,
    )


# -----------------------------------------------------------------------------
# User input
# -----------------------------------------------------------------------------

st.subheader("Tell us about yourself")

with st.form("coverage_form"):

    col1, col2 = st.columns(2)

    with col1:

        age = st.number_input(
            "Age",
            min_value=18,
            max_value=85,
            value=35,
        )

        annual_income = st.number_input(
            "Annual Income",
            min_value=0.0,
            value=85000.0,
            step=5000.0,
        )

        dependents = st.number_input(
            "Dependents",
            min_value=0,
            max_value=10,
            value=2,
            step=1,
        )

        location = st.text_input(
            "Country / State",
            value="United States",
            help="Used for insurance-product research.",
        )

    with col2:

        total_debt = st.number_input(
            "Total Outstanding Debt",
            min_value=0.0,
            value=200000.0,
            step=5000.0,
        )

        savings = st.number_input(
            "Savings & Investments",
            min_value=0.0,
            value=50000.0,
            step=5000.0,
        )

        existing_cover = st.number_input(
            "Existing Life Insurance",
            min_value=0.0,
            value=100000.0,
            step=5000.0,
        )

        currency = st.selectbox(
            "Currency",
            options=[
                "USD",
                "CAD",
                "EUR",
                "GBP",
                "AUD",
                "INR",
            ],
            index=0,
        )

    income_replacement_years = st.selectbox(
        "Income Replacement Horizon",
        options=[5, 10, 15],
        index=1,
        help="Number of years of income to protect.",
    )

    submitted = st.form_submit_button(
        "Generate Coverage & Options"
    )


# -----------------------------------------------------------------------------
# Build client profile
# -----------------------------------------------------------------------------

def build_client_profile() -> Dict[str, Any]:

    return {
        "age": age,
        "annual_income": annual_income,
        "dependents": dependents,
        "location": location,
        "total_debt": total_debt,
        "available_savings": savings,
        "existing_life_insurance": existing_cover,
        "income_replacement_years": income_replacement_years,
        "currency": currency,
    }


# -----------------------------------------------------------------------------
# Render results
# -----------------------------------------------------------------------------

def render_results(
    calculation: Dict[str, float],
    ai_result: Dict[str, Any],
    profile: Dict[str, Any],
) -> None:

    currency_code = profile["currency"]

    coverage_amount = calculation["recommended"]

    st.success("Coverage estimate generated successfully.")

    st.subheader("Recommended Coverage")

    st.metric(
        "Estimated Coverage Needed",
        format_currency(
            coverage_amount,
            currency_code,
        ),
    )

    # -------------------------------------------------------------------------
    # Calculation inputs
    # -------------------------------------------------------------------------

    st.subheader("Calculation Inputs")

    st.table(
        {
            "Input": [
                "Age",
                "Annual income",
                "Dependents",
                "Income replacement horizon",
                "Total debt",
                "Savings & investments",
                "Existing life insurance",
                "Discount rate",
            ],
            "Value": [
                str(profile["age"]),
                format_currency(
                    profile["annual_income"],
                    currency_code,
                ),
                str(profile["dependents"]),
                f"{profile['income_replacement_years']} years",
                format_currency(
                    profile["total_debt"],
                    currency_code,
                ),
                format_currency(
                    profile["available_savings"],
                    currency_code,
                ),
                format_currency(
                    profile["existing_life_insurance"],
                    currency_code,
                ),
                "2%",
            ],
        }
    )

    # -------------------------------------------------------------------------
    # Coverage math
    # -------------------------------------------------------------------------

    st.subheader("Step-by-step Coverage Math")

    st.table(
        {
            "Step": [
                "Annuity factor",
                "Discounted income replacement",
                "+ Outstanding debt",
                "- Savings",
                "- Existing life insurance",
                "= Estimated coverage",
            ],
            "Amount": [
                f"{calculation['annuity_factor']:.3f}",
                format_currency(
                    calculation["discounted_income"],
                    currency_code,
                ),
                format_currency(
                    calculation["debt"],
                    currency_code,
                ),
                format_currency(
                    calculation["savings"],
                    currency_code,
                ),
                format_currency(
                    calculation["existing_cover"],
                    currency_code,
                ),
                format_currency(
                    calculation["recommended"],
                    currency_code,
                ),
            ],
        }
    )

    with st.expander(
        "How was this calculated?",
        expanded=True,
    ):

        st.write(
            "Estimated coverage = discounted income replacement "
            "+ outstanding debt - savings - existing life insurance."
        )

        st.write(
            f"Income replacement value: "
            f"{format_currency(calculation['discounted_income'], currency_code)}"
        )

        st.write(
            f"Debt: "
            f"{format_currency(calculation['debt'], currency_code)}"
        )

        st.write(
            f"Assets and existing cover: "
            f"{format_currency(calculation['assets_offset'], currency_code)}"
        )

    # -------------------------------------------------------------------------
    # AI research
    # -------------------------------------------------------------------------

    recommendations = ai_result.get(
        "recommendations",
        [],
    )

    if recommendations:

        st.subheader("Term Life Research Options")

        for index, option in enumerate(
            recommendations,
            start=1,
        ):

            name = option.get(
                "name",
                "Unnamed Product",
            )

            summary = option.get(
                "summary",
                "No summary available.",
            )

            st.markdown(
                f"### {index}. {name}"
            )

            st.write(summary)

            link = option.get("link")

            if link:
                st.markdown(
                    f"[View details]({link})"
                )

            source = option.get("source")

            if source:
                st.caption(
                    f"Source: {source}"
                )

            st.divider()

    else:

        st.info(
            "No product recommendations were returned. "
            "You can add a Firecrawl API key to enable fresh product research."
        )

    # -------------------------------------------------------------------------
    # Assumptions
    # -------------------------------------------------------------------------

    with st.expander("Assumptions & Disclaimer"):

        st.write(
            {
                "Income replacement years": profile[
                    "income_replacement_years"
                ],
                "Real discount rate": "2%",
                "Age": str(profile["age"]),
                "Dependents": str(profile["dependents"]),
                "Location": profile["location"],
            }
        )

        st.warning(
            "This is an educational estimate, not licensed financial advice. "
            "Actual insurance needs, eligibility, premiums and policy terms "
            "depend on the insurer and the applicant."
        )

    # -------------------------------------------------------------------------
    # Debug JSON
    # -------------------------------------------------------------------------

    with st.expander("Agent Response JSON"):

        st.json(ai_result)


# -----------------------------------------------------------------------------
# Run application
# -----------------------------------------------------------------------------

if submitted:

    client_profile = build_client_profile()

    # ---------------------------------------------------------
    # Local deterministic calculation
    # ---------------------------------------------------------

    calculation = calculate_coverage(
        annual_income=annual_income,
        income_replacement_years=income_replacement_years,
        total_debt=total_debt,
        savings=savings,
        existing_cover=existing_cover,
        discount_rate=0.02,
    )

    # ---------------------------------------------------------
    # AI research
    # ---------------------------------------------------------

    advisor_agent = get_agent(
        firecrawl_api_key
    )

    user_prompt = f"""
You are helping research life insurance options.

Client profile:

{json.dumps(client_profile, indent=2)}

The application has already calculated the estimated coverage.

Estimated coverage:
{calculation["recommended"]}

Currency:
{currency}

Discounted income replacement:
{calculation["discounted_income"]}

Debt:
{calculation["debt"]}

Savings:
{calculation["savings"]}

Existing insurance:
{calculation["existing_cover"]}

If product research tools are available, find up to three
term-life insurance research options relevant to:

{location}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "coverage_amount": {round(calculation["recommended"])},
    "coverage_currency": "{currency}",
    "breakdown": {{
        "income_replacement": {round(calculation["discounted_income"])},
        "debt_obligations": {round(calculation["debt"])},
        "assets_offset": {round(calculation["assets_offset"])},
        "methodology": "Discounted income replacement plus debt minus savings and existing coverage."
    }},
    "assumptions": {{
        "income_replacement_years": {income_replacement_years},
        "real_discount_rate": "2%",
        "additional_notes": "Educational estimate only."
    }},
    "recommendations": [],
    "research_notes": "Research results are informational only.",
    "timestamp": "{datetime.now().astimezone().isoformat()}"
}}

Do not invent insurer details.
Do not invent URLs.
"""

    with st.spinner(
        "Consulting local AI advisor..."
    ):

        try:

            response = advisor_agent.run(
                user_prompt,
                stream=False,
            )

            raw_response = (
                response.content
                if response
                else ""
            )

            ai_result = extract_json(
                raw_response
            )

            if ai_result is None:

                # Even if the small local model fails to produce JSON,
                # the deterministic calculation remains available.
                ai_result = {
                    "coverage_amount": round(
                        calculation["recommended"]
                    ),
                    "coverage_currency": currency,
                    "breakdown": {
                        "income_replacement": round(
                            calculation["discounted_income"]
                        ),
                        "debt_obligations": round(
                            calculation["debt"]
                        ),
                        "assets_offset": round(
                            calculation["assets_offset"]
                        ),
                        "methodology": (
                            "Discounted income replacement "
                            "plus debt minus savings "
                            "and existing coverage."
                        ),
                    },
                    "assumptions": {
                        "income_replacement_years": (
                            income_replacement_years
                        ),
                        "real_discount_rate": "2%",
                        "additional_notes": (
                            "AI response could not be parsed. "
                            "Coverage calculation was performed locally."
                        ),
                    },
                    "recommendations": [],
                    "research_notes": (
                        "Local coverage calculation completed."
                    ),
                    "timestamp": datetime.now().astimezone().isoformat(),
                }

                with st.expander(
                    "Raw AI Response"
                ):
                    st.write(
                        raw_response
                        if raw_response
                        else "<empty>"
                    )

            render_results(
                calculation,
                ai_result,
                client_profile,
            )

        except Exception as exc:

            st.error(
                "The local AI advisor could not complete "
                "the research step."
            )

            st.write(
                f"Error: {exc}"
            )

            # Still show the local calculation.
            fallback_result = {
                "coverage_amount": round(
                    calculation["recommended"]
                ),
                "coverage_currency": currency,
                "recommendations": [],
                "assumptions": {
                    "income_replacement_years": (
                        income_replacement_years
                    ),
                    "real_discount_rate": "2%",
                },
                "research_notes": (
                    "AI research was unavailable. "
                    "The coverage estimate was calculated locally."
                ),
                "timestamp": datetime.now().astimezone().isoformat(),
            }

            render_results(
                calculation,
                fallback_result,
                client_profile,
            )


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------

st.divider()

st.caption(
    "AI Life Insurance Advisor • "
    "Ollama + Qwen 2.5 0.5B • "
    "Educational prototype only"
)