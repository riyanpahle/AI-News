import os
import json
import asyncio
import requests
from dotenv import load_dotenv

load_dotenv()

# Primary domain (moved from arena.lmsys.org)
ARENA_URL = "https://arena.ai/leaderboard/text/overall"


async def fetch_arena_leaderboard():
    """
    Fetches the current top models from the LMSYS Chatbot Arena leaderboard.
    Uses HuggingFace Spaces API as primary, with Playwright fallback.
    """
    print("Attempting to fetch Arena leaderboard via HTTP API...")

    # --- Strategy 1: Playwright (primary, handles JS rendering) ---
    try:
        result = await _fetch_via_playwright()
        if result:
            print("Arena leaderboard fetched via Playwright.")
            return result
    except Exception as e:
        print(f"Playwright fetch failed: {e}")

    # --- Strategy 2: Cached snapshot fallback ---
    print("Live fetch failed. Using cached leaderboard snapshot.")
    return _get_cached_top10()





def _get_cached_top10():
    """
    Returns a recently cached snapshot of the Arena top 10.
    This is used as fallback when live scraping fails.
    Update this periodically.
    """
    # Last updated: May 2025 (approximate public rankings)
    top10 = [
        {"rank": 1, "model": "Gemini-2.5-Pro", "score": "~1380"},
        {"rank": 2, "model": "GPT-4o (2024-11)", "score": "~1365"},
        {"rank": 3, "model": "Claude 3.7 Sonnet", "score": "~1358"},
        {"rank": 4, "model": "Gemini-2.0-Flash", "score": "~1340"},
        {"rank": 5, "model": "GPT-4.1", "score": "~1335"},
        {"rank": 6, "model": "Claude 3.5 Sonnet", "score": "~1320"},
        {"rank": 7, "model": "Llama-3.3-70B", "score": "~1278"},
        {"rank": 8, "model": "Mistral Large 2", "score": "~1254"},
        {"rank": 9, "model": "Qwen2.5-72B", "score": "~1248"},
        {"rank": 10, "model": "DeepSeek-V3", "score": "~1240"},
    ]

    table_md = "| Rank | Model Name | Elo Rating |\n|---|---|---|\n"
    for item in top10:
        table_md += f"| #{item['rank']} | **{item['model']}** | {item['score']} |\n"

    table_md += "\n*⚠️ Note: Live leaderboard unavailable. Showing recent cached rankings.*"

    return [{
        "title": "🏆 LMSYS Chatbot Arena Top 10 Leaderboard",
        "url": "https://arena.lmsys.org",
        "source": "LMSYS Arena (cached)",
        "raw_summary": table_md
    }]


async def _fetch_via_playwright():
    """Scrape the Arena leaderboard using Playwright."""
    from playwright.async_api import async_playwright

    url = ARENA_URL  # https://arena.ai/leaderboard/text

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=45000)
            # Wait for table to render
            await page.wait_for_selector("table tr", timeout=30000)

            rows = await page.query_selector_all("table tr")
            table_md = "| Rank | Model Name | Elo Rating |\n|---|---|---|\n"

            count = 0
            for row in rows[1:]:  # Skip header
                cols = await row.query_selector_all("td")
                if len(cols) >= 3 and count < 10:
                    rank = (await cols[0].inner_text()).strip()
                    # In the new table structure:
                    # cols[0] = Rank
                    # cols[1] = Rank Spread
                    # cols[2] = Model Name
                    # cols[3] = Elo Rating
                    model_name = (await cols[2].inner_text()).split('\n')[0].strip()
                    score = (await cols[3].inner_text()).split('\n')[0].strip()

                    if rank and model_name:
                        table_md += f"| #{rank} | **{model_name}** | {score} |\n"
                        count += 1

            await browser.close()

            if count > 0:
                return [{
                    "title": "🏆 LMSYS Chatbot Arena Top 10 Leaderboard",
                    "url": url,
                    "source": "LMSYS Arena",
                    "raw_summary": table_md
                }]
            else:
                # Table found but no rows parsed — use cached
                await browser.close()
                return []
        except Exception as e:
            print(f"Playwright scraping error: {e}")
            await browser.close()

    return []
