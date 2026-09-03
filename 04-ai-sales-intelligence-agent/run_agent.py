import requests
from pathlib import Path
from datetime import datetime


MODEL = "qwen2.5:0.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"

OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)


def ask_qwen(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()
    return response.json()["response"]


def main():
    competitor = "Salesforce"
    product = "HubSpot"

    results = {}

    print("\n=== AI SALES INTELLIGENCE ===\n")

    results["Competitor Research"] = ask_qwen(
        f"Give 3 short facts about {competitor} relevant to sales competition. "
        "Keep each fact short."
    )

    results["Product Features"] = ask_qwen(
        f"List 5 important features of {competitor} that customers may compare "
        f"with {product}. Keep each point short."
    )

    results["Positioning"] = ask_qwen(
        f"Compare {product} and {competitor} in 4 short points. "
        "Focus on positioning and customer value."
    )

    results["SWOT Analysis"] = ask_qwen(
        f"Give a simple SWOT analysis for competing with {competitor} using {product}. "
        "Give 2 points each for strengths, weaknesses, opportunities and threats."
    )

    results["Objection Handling"] = ask_qwen(
        f"Give 3 common customer objections when choosing {product} instead of "
        f"{competitor}, with a short response to each."
    )

    results["Sales Battle Card"] = ask_qwen(
        f"Create a short sales battle card for {product} vs {competitor}. "
        "Include Why We Win, Key Talking Points and Closing Tip."
    )

    results["Comparison Report"] = ask_qwen(
        f"Create a short comparison between {product} and {competitor}. "
        "Compare features, value, ease of use, target customers and sales pitch."
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_file = OUTPUTS_DIR / f"sales_analysis_{timestamp}.html"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{product} vs {competitor} - Sales Intelligence</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }}

        h1 {{
            text-align: center;
        }}

        h2 {{
            margin-top: 30px;
        }}

        .section {{
            padding: 20px;
            margin: 15px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}

        pre {{
            white-space: pre-wrap;
            font-family: Arial, sans-serif;
        }}
    </style>
</head>

<body>

<h1>AI Sales Intelligence Report</h1>

<p><strong>Product:</strong> {product}</p>
<p><strong>Competitor:</strong> {competitor}</p>

"""

    for title, content in results.items():
        html += f"""
<div class="section">
    <h2>{title}</h2>
    <pre>{content}</pre>
</div>
"""

    html += """
</body>
</html>
"""

    report_file.write_text(html, encoding="utf-8")

    print("\n=== ANALYSIS COMPLETE ===")
    print(f"\nReport saved to:")
    print(report_file)


if __name__ == "__main__":
    main()