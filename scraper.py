import requests
import threading
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
from dateutil import parser
import re
from utils import PaperInfo, setup_logger
from typing import Dict
import os

OPENROUTER_API = os.getenv("OPENROUTER_API")

def fetch_apod(results: Dict[str, str]):
    logger = setup_logger("apod")
    url = "https://apod.nasa.gov/apod/astropix.html"
    logger.info("🚀 [APOD] Starting to fetch Astronomy Picture of the Day")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title_tag = soup.find_all("center")[1].find("b")
        title = title_tag.text.strip() if title_tag else "No Title Found"
        media_tag = soup.find("img")
        is_video = False
        if not media_tag:
            media_tag = soup.find("video").find("source")
            is_video = True
        media_url = f"https://apod.nasa.gov/apod/{media_tag['src']}" if media_tag else ""
        if is_video:
            media_html = f'<video controls style="width: 100%; border-radius: 8px;"><source src="{media_url}"></video>'
        else:
            media_html = f'<img src="{media_url}" alt="APOD" style="width: 100%; border-radius: 8px;">'

        explanation_raw = soup.find_all("p")[2].decode_contents()
        explanation = explanation_raw.split("Tomorrow's picture:")[0].replace("<p> <center>\n<b>", "").strip()

        logger.info("📥 [APOD] Title: %s", title)
        logger.info("🖼️ [APOD] Media URL: %s", media_url)

        html = f"""
        <div style='display: flex; flex-direction: column; gap: 15px; margin-bottom: 30px;'>
            <!-- Centered: title + media + caption -->
            <div style='display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px;'>
                <h3 style='margin: 0; color: #2c5282;'>✨ {title}</h3>
                <div style="width: 100%; max-width: 600px;">
                    {media_html}
                </div>
                <p style='font-size: 15px; color: #444;'>📌 NASA's Astronomy Picture of the Day</p>
            </div>

            <!-- Left-aligned explanation that expands fully -->
            <div style="width: 100%;">
                <p style='font-size: 16px; line-height: 1.6; margin: 0; text-align: left;'>
                    {explanation}
                </p>
            </div>
        </div>
        """

        results["apod"] = html
        logger.info("✅ [APOD] Successfully fetched.\n")
    except Exception as e:
        logger.error("❌ [APOD] Failed to fetch: %s\n", e)
        results["apod"] = "<h2>🚫 Failed to load APOD</h2>"

def fetch_llm_summary(article_text: str, logger: logging.Logger) -> str:
    try:
        res = requests.post(
        url = "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API}",
        },
        data = json.dumps({
            "model": "qwen/qwen3-235b-a22b:free",
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                        You are a strict scientific paper summarizer. Output only the summary. No explanations, no intros, no markdown, no HTML, no links, no emojis, no bullet points, no lists.
                        Summarize the following article in a concise manner and ignore unrelevant information:\n{article_text}
                        """
                }
            ],
            })
        )
        llm_summary = res.json().get("choices", [{}])[0].get("message", {}).get("content", "No summary available").strip()
        logger.info(f"🤖 [EO] LLM summary: {llm_summary}")
    except Exception as e:
        logger.error("❌ [EO] LLM Summary failed: %s", e)
        llm_summary = "No summary available"
    return llm_summary

def fetch_eo(results: Dict[str, str]):
    logger = setup_logger("earthobservatory")
    url = "https://earthobservatory.nasa.gov/topic/image-of-the-day"
    logger.info("🚀 [EO] Starting to fetch Earth Observatory Image of the Day")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        first_card = soup.select_one('.first-landing-cards .masonry-item')

        title_tag = first_card.select_one('h4 a')
        title = title_tag.text.strip() if title_tag else "No Title Found"
        link = f"https://earthobservatory.nasa.gov{title_tag['href']}" if title_tag else "#"

        res = requests.get(link, timeout=10)
        article_soup = BeautifulSoup(res.text, "html.parser")
        article = article_soup.find("div", class_="col-lg-8 col-md-8 col-sm-8 col-xs-12 col-md-right-space col-md-bottom-space").find_all("p")
        article_text = " ".join(p.text.strip() for p in article)
        llm_summary = fetch_llm_summary(article_text, logger)

        media_tag = first_card.select_one('.thumbnail-image img')
        media_url = media_tag['src'] if media_tag else ""

        caption_tag = first_card.select_one('.caption p')
        caption = caption_tag.text.strip() if caption_tag else "No Summary Found"

        logger.info("📥 [EO] Title: %s", title)
        logger.info("🖼️ [EO] Image URL: %s", media_url)

        html = f"""
        <div style='display: flex; flex-direction: column; gap: 15px;'>
            <!-- Centered block -->
            <div style='display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px;'>
                <h3 style='margin: 0; color: #2d5016;'>🌍 {title}</h3>
                <div style='width: 100%; max-width: 600px;'>
                    <img src='{media_url}' alt='Earth Observatory' style='width: 100%; border-radius: 8px;'>
                </div>
                <p style='font-size: 15px; color: #444; margin: 0;'>📌 {caption} <a href='{link}' target='_blank'>[Read more]</a></p>
            </div>

            <!-- Full-width summary block (NOT inside centered container) -->
            <div style='width: 100%; display: flex; justify-content: center;'>
                <div style='background: #f0f8f0; padding: 12px; border-radius: 6px; border-left: 4px solid #2d5016; text-align: left; width: 100%;'>
                    <p style='font-size: 15px; line-height: 1.5; margin: 0; color: #1a3a0d;'>
                        🤖 <span style='font-style: italic;'>{llm_summary}</span>
                    </p>
                </div>
            </div>
        </div>
        """

        results["eo"] = html
        logger.info("✅ [EO] Successfully fetched.\n")
    except Exception as e:
        logger.error("❌ [EO] Failed to fetch: %s\n", e)
        results["eo"] = "<h2>🚫 Failed to load EO Image of the Day</h2>"

def fetch_hackernews(results: Dict[str, str]):
    logger = setup_logger("hackernews")
    logger.info("🚀 [HN] Starting to fetch Hacker News")
    try:
        res = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).json()
        top_stories = res[:10]
        html = "<h2>🔥 Hacker News Top 10</h2><ol>"
        for idx, sid in enumerate(top_stories, 1):
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
            title = story.get("title", "(no title)")
            url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
            logger.info("📥 [HN #%d] %s", idx, title)
            logger.info("🔗 [HN #%d] URL: %s", idx, url)

            html += f"<li><a href='{url}'>{title}</a></li>"
            logger.info("✅ [HN #%d] Done ✅", idx)

        html += "</ol>"
        results["hn"] = html
        logger.info("🎉 [HN] All done.\n")
    except Exception as e:
        logger.error(f"❌ [HN] Failed: {e}\n")
        results["hn"] = "<h2>🚫 Failed to load Hacker News</h2>"

def fetch_hf_papers(url: str, visited_links: Dict[str, PaperInfo], 
                    visited_links_lock: threading.Lock,
                    logger: logging.Logger):
    total_papers = 0
    url_type = url.split("/")[4]
    match url_type:
        case "date":
            papers_type = "DAILY"
            logger.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Daily Papers")
        case "week":
            papers_type = "WEEKLY"
            logger.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Weekly Papers")
        case "month":
            papers_type = "MONTHLY"
            logger.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Monthly Papers")
        case "trending":
            papers_type = "TRENDING"
            logger.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Trending Papers")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        papers = soup.find_all('article', class_='relative overflow-hidden rounded-xl border' if papers_type == "TRENDING" 
                               else "relative flex flex-col overflow-hidden rounded-xl border")[:15]

        if not papers:
            logger.warning(f"⚠️ [HF_{papers_type}] No papers found.")
            return
        for idx, paper in enumerate(papers, 1):
            title_tag = paper.find('h3').find('a')
            title = title_tag.text.strip() if title_tag else "Untitled"
            paper_link = f"https://huggingface.co{title_tag['href']}" if title_tag else "#"
            with visited_links_lock:
                if title in visited_links:
                    if papers_type not in visited_links[title]["tags"]:
                        visited_links[title]["tags"].append(papers_type)
                    logger.info(f"🔁 [HF_{papers_type} #{idx}] Skipping already visited paper: {title}")
                    continue
                else:
                    visited_links[title] = {
                        "paper_link": paper_link,
                        "pdf_link": None,
                        "abstract": None,
                        "tags": [papers_type],
                        "github_link": None,
                        "published_date": None,
                        "star_cnt":None,
                        "upvote_cnt":None
                    }
            total_papers += 1
            
            logger.info(f"📥 [HF_{papers_type} #%d] %s", idx, title)
            logger.info(f"🔗 [HF_{papers_type} #%d] Page URL: %s", idx, paper_link)
            res = requests.get(paper_link, timeout=10)
            paper_soup = BeautifulSoup(res.text, "html.parser")
            logger.info(f"🔗 [HF_{papers_type} #%d] Fetching paper details...", idx)

            published_date_tag = paper_soup.find("div", class_="mb-6 flex flex-wrap gap-2 text-sm text-gray-500 max-sm:flex-col sm:items-center sm:text-base md:mb-8")
            published_date_raw = published_date_tag.find("div").text.strip().replace("Published on ", "") if published_date_tag else "Unknown date"

            # Ensure date string ends with a year; if not, add current year
            try:
                if re.search(r'\d{4}$', published_date_raw):
                    date_obj = parser.parse(published_date_raw)
                else:
                    date_obj = parser.parse(f"{published_date_raw}, {datetime.now().year}")
                published_date = date_obj.strftime("%Y-%m-%d")
            except Exception as e:
                logger.error(f"❌ [HF_{papers_type} #%d] Date parsing failed: %s", idx, e)
                published_date = "Unknown date"

            github_link_tag = paper_soup.find('a', class_='btn inline-flex h-9 items-center', href=lambda href: href.startswith("https://github.com"))
            github_link = github_link_tag['href'] if github_link_tag else None
            upvote_tag = paper_soup.find("div", class_="shadow-alternate group flex h-9 cursor-pointer select-none items-center gap-2 rounded-lg border pl-3 pr-3.5 border-gray-300 bg-white dark:bg-gray-850")
            upvote_cnt = upvote_tag.find("div", class_="font-semibold text-orange-500").text.strip()
            star_cnt = ""
            if github_link:
                star_cnt = github_link_tag.find("span").text.strip()
                logger.info(f"🔗 [HF_{papers_type} #%d] GitHub: %s", idx, github_link)
            pdf_link = "https://arxiv.org/" + title_tag["href"].replace("papers/", "pdf/")

            abstract_tag = paper_soup.find('p', class_='text-blue-700 dark:text-blue-400')
            abstract = abstract_tag.text.strip() if abstract_tag else "(No abstract available)"
            
            with visited_links_lock:
                visited_links[title].update({
                    "pdf_link": pdf_link,
                    "abstract": abstract,
                    "github_link": github_link,
                    "published_date": published_date,
                    "upvote_cnt": upvote_cnt,
                    "star_cnt": star_cnt
                })
        logger.info(f"📄 [HF_{papers_type} #%d] Done🧾", idx)
        logger.info(f"🎉 [HF_{papers_type}] All done - {total_papers} papers found.")
    except Exception as e:
        logger.error(f"❌ [HF_{papers_type}] Failed: {e}")

def fetch_hf(results: Dict[str, str]):
    logger = setup_logger("huggingface")
    urls = [
        f"https://huggingface.co/papers/date/{datetime.now().strftime('%Y-%m-%d')}",
        f"https://huggingface.co/papers/week/{datetime.now().strftime('%G-W%V')}",
        f"https://huggingface.co/papers/month/{datetime.now().strftime('%Y-%m')}",
        "https://huggingface.co/papers/trending"
    ]

    visited_links = {}
    visited_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda url: fetch_hf_papers(url, visited_links, visited_lock, logger), urls)

    html = """
        <h2>📚 Hugging Face Papers</h2>
        <div id="hf-filters" style="text-align:center; margin-bottom: 20px;">
            <button data-tag="ALL" onclick="filterPapers('ALL')">All</button>
            <button data-tag="DAILY" onclick="filterPapers('DAILY')">Daily</button>
            <button data-tag="WEEKLY" onclick="filterPapers('WEEKLY')">Weekly</button>
            <button data-tag="MONTHLY" onclick="filterPapers('MONTHLY')">Monthly</button>
            <button data-tag="TRENDING" onclick="filterPapers('TRENDING')">Trending</button>
        </div>


        <div id="hf-grid" style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-top: 20px;
        ">
        """

    for title, info in visited_links.items():
        tags_html = "".join([
            f'<span class="tag">{tag}</span>'
            for tag in sorted(info["tags"])
        ])
        github_html = f'<span>🐙<a href="{info["github_link"]}" target="_blank" style="color: #28a745;">GitHub</a></span>' if info.get("github_link") else ''
        published_html = f'<div style="font-size: 12px; color: #999;">Published on:{info.get("published_date", "N/A")}</div>'
        data_tags = " ".join(info["tags"])
        html += f"""
        <div class="hf-card" data-tags="{data_tags}" data-date="{info['published_date']}" style="padding: 12px; border: 1px solid #ccc; border-radius: 8px; background: #fff;">
            <h3><a href="{info['paper_link']}" target="_blank">{title}</a></h3>
            {published_html}
            <div class="tags">{tags_html}</div>
            <div style="display: flex; flex-direction: column; gap: 6px; margin: 6px 0;">
            <!-- First row -->
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>📄<a href="{info['pdf_link']}" target="_blank">PDF</a></span>
                <span style="color: #ff6b35;">🔥{info.get('upvote_cnt', '0')} Upvote</span>
            </div>
            
            <!-- Second row -->
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>{github_html}</div>
                {f'<span style="color: #ffd700;">⭐{info.get("star_cnt", "0")} Star</span>' if info.get('star_cnt') else ''}
            </div>
            </div>
            <div class="abstract">
                {info['abstract']}
            </div>
        </div>
        """
    html += "</div>"

    results["hf"] = html
    if len(visited_links.keys()):
        logger.info(f"✅ [HF] Successfully fetched ({len(visited_links.keys())}) Hugging Face papers.")
    else:
        logger.info("❌ [HF] Something wrong, no papers fetched...")

