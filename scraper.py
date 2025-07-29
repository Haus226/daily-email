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
        hr_pos = explanation_raw.find("<hr/>")
        explanation_raw = explanation_raw[:hr_pos] if hr_pos != -1 else explanation_raw
        
        # Fix relative links in explanation
        explanation = explanation_raw.replace("<p> <center>\n", "<br>").replace("\n\n<p>", "").strip()
        # Convert relative links to absolute URLs for APOD
        explanation = re.sub(
            r'href="(?!https?://)([^"]*)"', 
            r'href="https://apod.nasa.gov/apod/\1"', 
            explanation
        )
        
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
        results["apod"] = "<div style='text-align: center; color: #e74c3c; padding: 2rem;'>🚫 Failed to load Astronomy Picture of the Day</div>"


def fetch_llm_summary(article_text: str, logger: logging.Logger) -> str:
    logger.info("🚀 [EO] Starting to fetch LLM Summary")
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
        logging.info("🤖 [EO] LLM Summary fetched successfully: {}".format(llm_summary.replace('\n', '')))
        if "<think>" in llm_summary:
            logger.info("🤖 [EO] LLM summary contains <think> tags, cleaning up...")
            llm_summary = re.sub(r"^(<think>){1,2}(.*?)(</think>){1,2}", "", llm_summary, flags=re.DOTALL).strip()
            logger.info(f"🤖 [EO] Cleaned LLM summary: {llm_summary}")

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
                    <p style='font-size: 18px; line-height: 1.5; margin: 0; color: #1a3a0d;'>
                        <span style='font-weight: bold;'>🤖 AI summary:</span>
                        <br>
                        <span style='font-style: italic; font-size: 18px;'>{llm_summary}</span>
                    </p>
                </div>
            </div>
        </div>
        """

        results["eo"] = html
        logger.info("✅ [EO] Successfully fetched.\n")
    except Exception as e:
        logger.error("❌ [EO] Failed to fetch: %s\n", e)
        results["eo"] = "<div style='text-align: center; color: #e74c3c; padding: 2rem;'>🚫 Failed to load Earth Observatory</div>"

def fetch_hackernews(results: Dict[str, str]):
    logger = setup_logger("hackernews")
    logger.info("🚀 [HN] Starting to fetch Hacker News")
    try:
        res = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).json()
        top_stories = res[:10]
        html = "<ol class='hn-list'>"
        for idx, sid in enumerate(top_stories, 1):
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
            title = story.get("title", "(no title)")
            url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
            logger.info("📥 [HN #%d] %s", idx, title)
            logger.info("🔗 [HN #%d] URL: %s", idx, url)

            html += f"<li><a href='{url}' target='_blank'>{title}</a></li>"
            logger.info("✅ [HN #%d] Done ✅", idx)

        html += "</ol>"
        results["hn"] = html
        logger.info("🎉 [HN] All done.\n")
    except Exception as e:
        logger.error(f"❌ [HN] Failed: {e}\n")
        results["hn"] = "<div style='text-align: center; color: #e74c3c; padding: 2rem;'>🚫 Failed to load Hacker News</div>"

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

            llm_summary_tag = paper_soup.find('p', class_='text-blue-700 dark:text-blue-400')
            llm_summary = llm_summary_tag.text.strip() if llm_summary_tag else "(No summary available)"
            abstract_tag = paper_soup.find('div', class_="flex flex-col gap-y-2.5")
            if abstract_tag:
                abstract_p = abstract_tag.find("p", class_="text-gray-600")
                if abstract_p:
                    # Get the HTML content to preserve links
                    abstract_html = str(abstract_p.decode_contents()).strip()
                    # Convert relative links to absolute URLs
                    abstract = re.sub(
                        r'href="(/[^"]*)"', 
                        r'href="https://huggingface.co\1"', 
                        abstract_html
                    )
                else:
                    abstract = "(No abstract available)"
            else:
                abstract = "(No abstract available)"
            with visited_links_lock:
                visited_links[title].update({
                    "pdf_link": pdf_link,
                    "abstract": abstract,
                    "llm_summary": llm_summary,
                    "github_link": github_link,
                    "published_date": published_date,
                    "upvote_cnt": upvote_cnt,
                    "star_cnt": star_cnt
                })
        logger.info(f"📄 [HF_{papers_type} #%d] Done🧾", idx)
        logger.info(f"🎉 [HF_{papers_type}] All done - {total_papers} papers found.")
    except Exception as e:
        logger.error(f"❌ [HF_{papers_type} #%d] Failed: {e}")

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
        <div id="hf-grid" class="papers-grid">
        """
    if len(visited_links.keys()):
        for title, info in visited_links.items():
            tags_html = "".join([
                f'<span class="tag">{tag}</span>'
                for tag in sorted(info["tags"])
            ])
            data_tags = " ".join(info["tags"])
            html += f"""
                <div class="paper-card hf-card flip-card" data-tags="{data_tags}" data-date="{info['published_date']}" onclick="flipCard(this)">
                    <div class="flip-card-inner">
                        <!-- Front of card -->
                        <div class="flip-card-front">
                            <div class="paper-header">
                                <div class="paper-title-date">
                                    <h3 class="paper-title">
                                        <a href="{info['paper_link']}" target="_blank" onclick="event.stopPropagation()">{title}</a>
                                    </h3>
                                    <div class="paper-date-tags">
                                        <div class="paper-date">Published: {info.get("published_date", "N/A")}</div>
                                        <div class="tags">{tags_html}</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="paper-content">
                                <div class="paper-links-grid">
                                    <a href="{info['pdf_link']}" target="_blank" class="link-item pdf-link" onclick="event.stopPropagation()">📄 PDF</a>
                                    {f'<a href="{info["github_link"]}" target="_blank" class="link-item github-link" onclick="event.stopPropagation()">🐙 GitHub</a>' if info.get("github_link") else '<div class="link-item" style="background: #f5f5f5; color: #999;">No GitHub</div>'}
                                    <div class="link-item upvote-item">🔥 {info.get('upvote_cnt', '0')}</div>
                                    <div class="link-item stars-item">⭐ {info.get('star_cnt', '0') if info.get('star_cnt') else '0'}</div>
                                </div>
                                
                                <div class="llm-summary-box">
                                    <p>
                                        <strong>🤖 AI Summary:</strong>
                                        <em style="color: #2d5016;">{info.get('llm_summary', 'No summary available')}</em>
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Back of card -->
                        <div class="flip-card-back">
                            <h4>📄 Abstract</h4>
                            <div class="abstract-text">
                                {info['abstract']}
                            </div>
                        </div>
                    </div>
                </div>
                """
        html += "</div>"
        logger.info("✅ [HF] Successfully fetched (%d) Hugging Face papers.\n", len(visited_links.keys()))
    else:
        html += "<div style='text-align: center; color: #e74c3c; padding: 2rem;'>🚫 No Hugging Face papers found</div></div>"
        logger.info("❌ [HF] Something wrong, no papers fetched...\n")

    results["hf"] = html