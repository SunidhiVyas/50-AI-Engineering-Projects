from typing import List
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def scrape_url(url: str) -> dict:
    """
    Scrape a single web page using requests and BeautifulSoup.
    """

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove unnecessary page elements
        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
            ]
        ):
            tag.decompose()

        # Get page title
        title = ""

        if soup.title:
            title = soup.title.get_text(
                strip=True
            )

        # Try to find publication date
        published_date = ""

        date_selectors = [
            "meta[property='article:published_time']",
            "meta[name='article:published_time']",
            "meta[property='og:published_time']",
            "meta[name='date']",
            "meta[itemprop='datePublished']",
            "time[datetime]",
        ]

        for selector in date_selectors:
            element = soup.select_one(selector)

            if element:

                published_date = (
                    element.get("content")
                    or element.get("datetime")
                    or element.get_text(strip=True)
                    or ""
                )

                if published_date:
                    break

        # Extract paragraph text
        paragraphs = []

        for paragraph in soup.find_all("p"):

            text = paragraph.get_text(
                " ",
                strip=True,
            )

            if len(text) >= 40:
                paragraphs.append(text)

        # Keep article text reasonably sized
        full_text = "\n".join(
            paragraphs[:80]
        )

        return {
            "success": True,
            "original_url": url,
            "final_url": response.url,
            "title": title,
            "full_text": full_text,
            "published_date": published_date,
        }

    except Exception as e:

        print(
            f"Scraping failed for {url}: {e}"
        )

        return {
            "success": False,
            "original_url": url,
            "final_url": url,
            "title": "",
            "full_text": "",
            "published_date": "",
        }


def crawl_urls_batch(
    search_results: List[dict],
):
    """
    Scrape all unique URLs from search results.
    """

    unique_urls = []
    seen_urls = set()

    for search_result in search_results:

        url = search_result.get(
            "url",
            "",
        )

        if not url:
            continue

        if not search_result.get(
            "is_scrapping_required",
            True,
        ):
            continue

        if url not in seen_urls:

            seen_urls.add(url)
            unique_urls.append(url)

    print(
        f"Scraping {len(unique_urls)} unique URLs..."
    )

    scraped_results = []

    for url in unique_urls:

        result = scrape_url(url)

        scraped_results.append(result)

    url_to_scraped = {
        result["original_url"]: result
        for result in scraped_results
    }

    updated_search_results = []

    successful_scrapes = 0
    failed_scrapes = 0

    for search_result in search_results:

        original_url = search_result.get(
            "url",
            "",
        )

        scraped = url_to_scraped.get(
            original_url,
            {},
        )

        updated_result = search_result.copy()

        updated_result["original_url"] = (
            original_url
        )

        if scraped.get(
            "success",
            False,
        ):

            updated_result["url"] = (
                scraped.get(
                    "final_url",
                    original_url,
                )
            )

            updated_result["full_text"] = (
                scraped.get(
                    "full_text",
                    "",
                )
                or search_result.get(
                    "description",
                    "",
                )
            )

            updated_result["published_date"] = (
                scraped.get(
                    "published_date",
                    "",
                )
            )

            if scraped.get("title"):
                updated_result["title"] = (
                    scraped["title"]
                )

            successful_scrapes += 1

        else:

            # Use search result description
            # if the website cannot be scraped.
            updated_result["url"] = (
                original_url
            )

            updated_result["full_text"] = (
                search_result.get(
                    "description",
                    "",
                )
            )

            updated_result["published_date"] = ""

            failed_scrapes += 1

        updated_search_results.append(
            updated_result
        )

    return (
        updated_search_results,
        successful_scrapes,
        failed_scrapes,
    )


def scrape_agent_run(
    agent,
    query: str,
) -> str:
    """
    Scrape URLs stored in the current session.
    """

    print(
        "Scrape Agent Input:",
        query,
    )

    from services.internal_session_service import (
        SessionService
    )

    session_id = agent.session_id

    session = SessionService.get_session(
        session_id
    )

    current_state = session["state"]

    search_results = current_state.get(
        "search_results",
        [],
    )

    if not search_results:

        return (
            "No search results available "
            "for scraping."
        )

    (
        updated_results,
        successful_scrapes,
        failed_scrapes,
    ) = crawl_urls_batch(
        search_results
    )

    current_state["search_results"] = (
        updated_results
    )

    current_state["stage"] = "scrape"

    SessionService.save_session(
        session_id,
        current_state,
    )

    return (
        f"Scraped {len(updated_results)} sources "
        f"for '{query}'. "
        f"Successful: {successful_scrapes}, "
        f"Failed: {failed_scrapes}."
    )