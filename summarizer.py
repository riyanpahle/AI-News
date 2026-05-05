import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def summarize_news(news_items):
    """
    Curates and ranks AI news items using the daily curation prompt.
    """
    # Limit to top 20 articles to stay within Groq free tier token limits
    news_items = news_items[:20]

    if not news_items:
        return "No new AI news found for the last 24 hours."

    # Prepare the articles for the prompt
    articles_text = ""
    for item in news_items:
        articles_text += f"Sumber: {item.get('source', 'Unknown')}\n"
        articles_text += f"Judul: {item.get('title', 'No Title')}\n"
        # Truncate summary to 200 chars to conserve tokens
        raw = item.get('raw_summary', 'No summary available')
        articles_text += f"Ringkasan: {raw[:200]}\n"
        articles_text += f"Link: {item.get('url', '#')}\n"
        articles_text += "-------------------\n"

    prompt = (
        "Kamu adalah kurator berita AI harian yang tajam dan selektif.\n\n"
        "Berikut adalah artikel-artikel yang dikumpulkan hari ini dari RSS feed terpercaya:\n\n"
        f"{articles_text}\n\n"
        "Tugasmu:\n"
        "- Pilih TEPAT 5 artikel paling penting\n"
        "- Urutkan dari yang paling prioritas ke paling rendah menggunakan hierarki ini:\n\n"
        "  P1 -> Rilis atau pengumuman model AI baru dari lab besar (OpenAI, Anthropic, Google, Meta, Mistral, xAI)\n"
        "  P2 -> Riset atau breakthrough teknikal yang signifikan\n"
        "  P3 -> Bisnis, funding besar (>$50M), atau akuisisi terkait AI\n"
        "  P4 -> Regulasi dan kebijakan AI dari pemerintah\n"
        "  P5 -> Tren, laporan industri, atau analisis dari tokoh berpengaruh\n\n"
        "Aturan seleksi:\n"
        "- Jika ada 2 artikel tentang topik yang sama, pilih yang paling lengkap dan buang yang lain\n"
        "- Utamakan berita dari sumber resmi lab AI dibanding media pihak ketiga\n"
        "- Abaikan artikel yang hanya opini tanpa data atau fakta baru\n\n"
        "Tulis output dalam format ini untuk setiap artikel:\n\n"
        "[Urutan N] P[1-5] | [Nama Sumber]\n"
        "Judul: ...\n"
        "Ringkasan: (2-3 kalimat, langsung ke inti, bahasa Indonesia)\n"
        "Kenapa penting: (1 kalimat)\n"
        "Link: ...\n\n"
        "Setelah 5 artikel, tambahkan:\n\n"
        "TREND HARI INI:\n"
        "(1 paragraf singkat tentang pola atau tema besar yang muncul dari berita hari ini)"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional AI news curator delivering high-quality summaries in Indonesian."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during Groq summarization: {e}")
        return "Gagal mengkurasi berita hari ini. Mohon coba lagi nanti."


def summarize_leaderboard(current_data, previous_data):
    """
    Updates AI model leaderboard ranking and highlights changes.
    """
    if not current_data:
        return "<p>Leaderboard update currently unavailable.</p>"

    prompt = (
        "Tandai model yang posisinya naik, turun, atau baru masuk dibanding data sebelumnya:\n\n"
        f"Data Leaderboard Sekarang: {current_data}\n\n"
        f"Data Leaderboard Kemarin: {previous_data}\n\n"
        "1. Tulis 2-3 kalimat highlight: model mana yang paling menarik perhatian hari ini dan mengapa\n"
        "2. Jika tidak ada perubahan signifikan, cukup tulis 'Tidak ada perubahan ranking signifikan hari ini'\n"
        "Format output: HTML siap embed di email, gunakan tabel sederhana."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an AI leaderboard analyst providing concise updates in HTML format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during leaderboard update: {e}")
        return "<p>Leaderboard update currently unavailable.</p>"
