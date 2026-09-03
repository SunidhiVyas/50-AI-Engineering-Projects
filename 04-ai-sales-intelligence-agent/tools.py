"""Custom tools for the Battle Card Pipeline.

Provides HTML battle card generation and comparison chart creation.
"""

import logging
import requests
from pathlib import Path
from datetime import datetime
from google.adk.tools import ToolContext
from google.genai import types
from litellm import completion

logger = logging.getLogger("BattleCardPipeline")

# Create outputs directory for generated files
OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


async def generate_battle_card_html(
    battle_card_data: str,
    tool_context: ToolContext
) -> dict:
    """Generate a professional HTML battle card for sales teams.

    Args:
        battle_card_data: Compiled competitive intelligence data
        tool_context: ADK tool context for artifact saving

    Returns:
        dict with status and artifact info
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""Generate a professional sales battle card in HTML format.

**DATE: {current_date}**

This is a competitive battle card for sales reps to use during deals.

Style it for SALES TEAMS with:
- Clean, scannable design (reps glance at this during calls)
- Color coding: GREEN for our advantages, RED for competitor strengths
- Collapsible sections for detailed content
- Quick-reference format at the top
- Dark blue (#1e3a5f) and orange (#f97316) color scheme
- Print-friendly layout

COMPETITIVE INTELLIGENCE DATA:
{battle_card_data}

**REQUIRED SECTIONS:**

1. **Header** - Competitor name, logo placeholder, last updated date
2. **Quick Stats** - 5-6 one-liner facts about the competitor
3. **At a Glance** - 3 columns: They Win | We Win | Toss-up
4. **Feature Comparison** - Table with checkmarks/X marks
5. **Positioning** - How to position against them (2-3 sentences)
6. **Their Strengths** - Honest list with red indicators
7. **Their Weaknesses** - List with green indicators (our opportunities)
8. **Objection Handling** - Top 5 objections with quick responses
9. **Killer Questions** - Questions to ask prospects
10. **Landmines** - Traps to set in competitive deals

Make it visually impressive but FAST TO SCAN. Sales reps have seconds, not minutes.

Generate complete, valid HTML with embedded CSS and JavaScript for collapsible sections."""

    try:
        response = completion(
            model="ollama/qwen2.5:0.5b",
            messages=[{"role": "user", "content": prompt}]
        )

        html_content = response.choices[0].message.content

        # Clean up markdown wrapping if present
        if "```html" in html_content:
            start = html_content.find("```html") + 7
            end = html_content.rfind("```")
            html_content = html_content[start:end].strip()
        elif "```" in html_content:
            start = html_content.find("```") + 3
            end = html_content.rfind("```")
            html_content = html_content[start:end].strip()

        # Save as ADK artifact
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_name = f"battle_card_{timestamp}.html"
        html_artifact = types.Part.from_bytes(
            data=html_content.encode('utf-8'),
            mime_type="text/html"
        )
        
        version = await tool_context.save_artifact(filename=artifact_name, artifact=html_artifact)
        logger.info(f"Saved battle card artifact: {artifact_name} (version {version})")

        # Also save to outputs folder
        filepath = OUTPUTS_DIR / artifact_name
        filepath.write_text(html_content, encoding='utf-8')
        
        return {
            "status": "success",
            "message": f"Battle card saved as '{artifact_name}' - view in Artifacts tab",
            "artifact": artifact_name,
            "version": version
        }

    except Exception as e:
        logger.error(f"Error generating battle card: {e}")
        return {"status": "error", "message": str(e)}
def web_search(query: str) -> str:
    """Search the web and return a short list of results."""
    try:
        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        response.raise_for_status()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result")[:5]:
            title = result.select_one(".result__title")
            snippet = result.select_one(".result__snippet")
            link = result.select_one(".result__a")

            if title and link:
                results.append(
                    f"Title: {title.get_text(' ', strip=True)}\n"
                    f"URL: {link.get('href', '')}\n"
                    f"Snippet: {snippet.get_text(' ', strip=True) if snippet else ''}"
                )

        return "\n\n".join(results) or "No search results found."

    except Exception as e:
        return f"Web search failed: {e}"


async def generate_comparison_chart(
    competitor_name: str,
    your_product_name: str,
    comparison_data: str,
    tool_context: ToolContext
) -> dict:
    """Create a text-based comparison report without requiring Gemini."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_name = f"comparison_{timestamp}.html"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{your_product_name} vs {competitor_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #1e3a5f;
        }}
        pre {{
            white-space: pre-wrap;
            background: #f4f4f4;
            padding: 20px;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <h1>{your_product_name} vs {competitor_name}</h1>
    <h2>Competitive Comparison</h2>
    <pre>{comparison_data}</pre>
</body>
</html>"""

    try:
        artifact = types.Part.from_bytes(
            data=html.encode("utf-8"),
            mime_type="text/html"
        )

        version = await tool_context.save_artifact(
            filename=artifact_name,
            artifact=artifact
        )

        (OUTPUTS_DIR / artifact_name).write_text(
            html,
            encoding="utf-8"
        )

        return {
            "status": "success",
            "message": f"Comparison report saved as {artifact_name}",
            "artifact": artifact_name,
            "version": version
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }