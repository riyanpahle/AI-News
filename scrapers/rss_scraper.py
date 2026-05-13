import feedparser
import logging
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

RSS_SOURCES = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/news/rss.xml",
        "badge": "openai",
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml",
        "badge": "deepmind",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "badge": "hf",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "badge": "verge",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "badge": "venturebeat",
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "badge": "techcrunch",
    },
    {
        "name": "ArXiv CS.AI",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "badge": "arxiv",
    },
    {
        "name": "Import AI",
        "url": "https://importai.substack.com/feed",
        "badge": "importai",
    },
]

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "large language model", "gpt", "claude", "gemini", "mistral",
    "neural network", "transformer", "diffusion", "generative", "openai",
    "anthropic", "deepmind", "model", "chatbot", "inference", "fine-tuning",
    "benchmark", "multimodal", "reasoning", "agent", "deepseek"
]


def _parse_published(entry) -> datetime:
    """Parse published date from feed entry, fallback to now."""
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def _is_ai_related(title: str, summary: str) -> bool:
    """Return True if article is AI-related based on keywords."""
    text = (title + " " + summary).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def _get_raw_summary(entry) -> str:
    """Extract best available summary text from entry."""
    for attr in ("summary", "description", "content"):
        val = getattr(entry, attr, None)
        if val:
            if isinstance(val, list) and val:
                return val[0].get("value", "")
            if isinstance(val, str):
                return val
    return ""


def fetch_rss_news(hours_back: int = 24) -> list[dict]:
    """
    Fetch articles from all RSS sources published in the last `hours_back` hours.
    Returns list of article dicts sorted newest-first.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    articles = []

    for source in RSS_SOURCES:
        logger.info(f"Fetching RSS: {source['name']}")
        try:
            feed = feedparser.parse(source["url"])
            if feed.bozo and not feed.entries:
                logger.warning(f"Failed to parse {source['name']}: {feed.bozo_exception}")
                continue

            for entry in feed.entries:
                published = _parse_published(entry)
                if published < cutoff:
                    continue

                title = getattr(entry, "title", "").strip()
                raw_summary = _get_raw_summary(entry)
                url = getattr(entry, "link", "")

                # For MIT Tech Review, only include AI-related articles
                if source["name"] == "MIT Technology Review AI":
                    if not _is_ai_related(title, raw_summary):
                        continue

                articles.append({
                    "source": source["name"],
                    "badge": source["badge"],
                    "title": title,
                    "raw_summary": raw_summary[:1000],
                    "url": url,
                    "published": published.strftime("%d %b %Y, %H:%M UTC"),
                    "summary": "",  # filled later by summarizer
                    "is_claude": "claude" in title.lower() or "claude" in raw_summary.lower(),
                    "is_new_model": False,  # filled later
                })

        except Exception as e:
            logger.error(f"Error fetching {source['name']}: {e}")

    articles.sort(key=lambda x: x["published"], reverse=True)
    logger.info(f"Fetched {len(articles)} articles total")
    return articles