import asyncio
from dotenv import load_dotenv
from scrapers.rss_scraper import fetch_rss_news
from scrapers.arena_scraper import fetch_arena_leaderboard
from summarizer import summarize_news, summarize_leaderboard
from emailer import send_email_newsletter

# Load environment variables from .env file
load_dotenv()

async def main():
    print("Starting AI News Bot...")
    
    # 1. Scrape news from RSS feeds
    print("Scraping RSS feeds...")
    rss_news = fetch_rss_news()
    
    # 2. Scrape Arena Leaderboard
    print("Scraping Arena leaderboard...")
    arena_news = await fetch_arena_leaderboard()
    
    if not rss_news and not arena_news:
        print("No news found. Skipping summarization and email.")
        return


    # 3. Summarize news using AI (Curation logic)
    print("Curating RSS news...")
    news_summary = summarize_news(rss_news)
    
    # 4. Update Leaderboard (Current only for now)
    print("Generating leaderboard update...")
    # Passing current data, and None for previous data as requested
    arena_summary = summarize_leaderboard(arena_news, previous_data=None)
    
    # Combine everything for the email
    full_content = f"{news_summary}\n\n<hr>\n\n<h2>🏆 LMSYS Chatbot Arena Top 10 Leaderboard</h2>\n<span class=\"source\"><b>Source:</b> LMSYS Arena | <b>Published:</b> Update Terbaru</span>\n{arena_summary}"
    
    # 5. Send the summary via email
    print("Sending email...")
    success = send_email_newsletter(full_content)
    
    if success:
        print("AI News Bot completed successfully!")
    else:
        print("AI News Bot failed to send email.")


if __name__ == "__main__":
    asyncio.run(main())
