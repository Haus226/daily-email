import requests
import smtplib
import threading
import logging
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from typing import List, Dict, TypedDict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class PaperInfo(TypedDict):
    paper_link: str
    pdf_link: str
    github_link: str | None
    abstract: str
    tags: List[str]  # Only this field is a list

# ---------------------------------

def fetch_apod(results):
    url = "https://apod.nasa.gov/apod/astropix.html"
    logging.info("🚀 [APOD] Starting to fetch Astronomy Picture of the Day")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title_tag = soup.find_all("center")[1].find("b")
        title = title_tag.text.strip() if title_tag else "No Title Found"
        image_tag = soup.find("img")
        image_url = f"https://apod.nasa.gov/apod/{image_tag['src']}" if image_tag else ""

        explanation_raw = soup.find_all("p")[2].decode_contents()
        explanation = explanation_raw.split("Tomorrow's picture:")[0].replace("<p> <center>\n<b>", "").strip()

        logging.info("📥 [APOD] Title: %s", title)
        logging.info("🖼️ [APOD] Image URL: %s", image_url)

        html = f"<h2>✨ Astronomy Picture of the Day</h2><center><b>{title}</b><br><img src='{image_url}' width='500'></center><br>{explanation}</p>"
        results["apod"] = html
        logging.info("✅ [APOD] Successfully fetched.")
    except Exception as e:
        logging.error("❌ [APOD] Failed to fetch: %s", e)
        results["apod"] = "<h2>🚫 Failed to load APOD</h2>"


def fetch_eo(results):
    url = "https://earthobservatory.nasa.gov/topic/image-of-the-day"
    logging.info("🚀 [EO] Starting to fetch Earth Observatory Image of the Day")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Find first card under the landing section
        first_card = soup.select_one('.first-landing-cards .masonry-item')

        title_tag = first_card.select_one('h4 a')
        title = title_tag.text.strip() if title_tag else "No Title Found"
        link = f"https://earthobservatory.nasa.gov{title_tag['href']}" if title_tag else "#"

        image_tag = first_card.select_one('.thumbnail-image img')
        image_url = image_tag['src'] if image_tag else ""

        explanation = first_card.select_one('.caption p')
        explanation = explanation.text.strip() if explanation else "No Summary Found"

        logging.info("📥 [EO] Title: %s", title)
        logging.info("🖼️ [EO] Image URL: %s", image_url)

        html = (
            "<h2>🌍 NASA Earth Observatory - Image of the Day</h2>"
            f"<center><b>{title}</b><br>"
            f"<img src='{image_url}' width='500'></center><br>"
            f"{explanation}<a href='{link}' target='_blank'>[Read more]</a></p>"
        )

        results["eo"] = html
        logging.info("✅ [EO] Successfully fetched.")
    except Exception as e:
        logging.error("❌ [EO] Failed to fetch: %s", e)
        results["eo"] = "<h2>🚫 Failed to load EO Image of the Day</h2>"
        

def fetch_hackernews(results):
    logging.info("🚀 [HN] Starting to fetch Hacker News")
    try:
        res = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).json()
        top_stories = res[:10]
        html = "<h2>🔥 Hacker News Top 10</h2><ol>"
        for idx, sid in enumerate(top_stories, 1):
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
            title = story.get("title", "(no title)")
            url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
            logging.info("📥 [HN #%d] %s", idx, title)
            logging.info("🔗 [HN #%d] URL: %s", idx, url)

            html += f"<li><a href='{url}'>{title}</a></li>"
            logging.info("✅ [HN #%d] Done ✅", idx)

        html += "</ol>"
        results["hn"] = html
        logging.info("🎉 [HN] All done.")
    except Exception as e:
        logging.error(f"❌ [HN] Failed: {e}")
        results["hn"] = "<h2>🚫 Failed to load Hacker News</h2>"

# # Deprecated: fetch_paperswithcode is now using the new URL
# def fetch_paperswithcode(results):
#     logging.info("🚀 [PwC] Starting to fetch Papers with Code")
#     try:
#         url = "https://paperswithcode.com/"
#         res = requests.get(url, timeout=10)
#         soup = BeautifulSoup(res.text, "html.parser")
#         papers = soup.find_all('div', class_='col-lg-9 item-content')

#         html = "<h2>📚 Daily Papers With Code Trending</h2><ul>"
#         if not papers:
#             logging.warning("⚠️ [PwC] No papers found.")
#             results["pwc"] = "<h2>🚫 No papers found</h2>"
#             return
#         for idx, paper in enumerate(papers, 1):
#             title_tag = paper.find('h1').find('a')
#             title = title_tag.text.strip() if title_tag else "Untitled"
#             paper_link = f"https://paperswithcode.com{title_tag['href']}" if title_tag else "#"
#             logging.info("📥 [PwC #%d] %s", idx, title)
#             logging.info("🔗 [PwC #%d] Page URL: %s", idx, paper_link)

#             github_link_tag = paper.find('span', class_='item-github-link')
#             github_link = github_link_tag.find('a')['href'] if github_link_tag and github_link_tag.find('a') else None
#             if github_link:
#                 logging.info("🔗 [PwC #%d] GitHub: %s", idx, github_link)

#             abstract_tag = paper.find('p', class_='item-strip-abstract')
#             abstract = abstract_tag.text.strip() if abstract_tag else "(No abstract available)"

#             html += "<li style='margin-bottom: 1em;'>"
#             html += f"<b><a href='{paper_link}' target='_blank'>{title}</a>"
#             if github_link:
#                 html += f" &nbsp; <a href='{github_link}' target='_blank'>[GitHub]</a>"
#             html += "</b><br>"
#             html += f"<p style='margin: 0.2em 0;'>{abstract}</p>"
#             html += "</li>"

#             logging.info("📄 [PwC #%d] Done 🧾", idx)

#         html += "</ul>"
#         results["pwc"] = html
#         logging.info("🎉 [PwC] All done.")
#     except Exception as e:
#         logging.error(f"❌ [PwC] Failed: {e}")
#         results["pwc"] = "<h2>🚫 Failed to load Papers With Code</h2>"

def run_hf(results: dict):
    urls = [
        f"https://huggingface.co/papers/date/{datetime.now().strftime('%Y-%m-%d')}",
        f"https://huggingface.co/papers/week/{datetime.now().strftime('%G-W%V')}",
        f"https://huggingface.co/papers/month/{datetime.now().strftime('%Y-%m')}",
        "https://huggingface.co/papers/trending"
    ]

    visited_links = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda url: fetch_hf_papers(url, visited_links), urls)

    # Build HTML
    html = f"<h2>📚 Hugging Face ({len(visited_links.keys())} Papers)</h2><br>"
    for title, info in visited_links.items():
        tags_html = "".join([
            f'<span style="background-color:#eee;border-radius:4px;padding:2px 6px;margin-right:6px;font-size:12px;color:#444;">{tag}</span>'
            for tag in sorted(info["tags"])
        ])
        github_html = f'<span><a href="{info["github_link"]}" target="_blank" style="color: #28a745;">[GitHub]</a></span>' if info.get("github_link") else ''
        html += f"""
        <div style="border: 1px solid #ccc; border-radius: 8px; padding: 12px; margin-bottom: 16px; font-family: sans-serif;">
            <div style="font-size: 16px; font-weight: bold; color: #333; margin-bottom: 8px;">
                <a href="{info['paper_link']}" target="_blank" style="text-decoration: none; color: #1a0dab;">{title}</a>
                <br>
                {tags_html}
                <hr>
                {github_html}
                <span style="margin-left: 5px;"><a href="{info['pdf_link']}" target="_blank" style="color: #007bff;">[PDF]</a></span>
            </div>
            <div style="font-size: 14px; color: #555; line-height: 1.5;">
                {info['abstract']}
            </div>
        </div>
        """
    results["hf"] = html

def fetch_hf_papers(url: str, visited_links: Dict[str, PaperInfo]):
    total_papers = 0
    url_type = url.split("/")[4]
    match url_type:
        case "date":
            papers_type = "DAILY"
            logging.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Daily Papers")
        case "week":
            papers_type = "WEEKLY"
            logging.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Weekly Papers")
        case "month":
            papers_type = "MONTHLY"
            logging.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Monthly Papers")
        case "trending":
            papers_type = "TRENDING"
            logging.info(f"🚀 [HF_{papers_type}] Starting to fetch Hugging Face Trending Papers")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        papers = soup.find_all('article', class_='relative overflow-hidden rounded-xl border' if papers_type == "TRENDING" 
                               else "relative flex flex-col overflow-hidden rounded-xl border")[:9]

        if not papers:
            logging.warning(f"⚠️ [HF_{papers_type}] No papers found.")
            return
        for idx, paper in enumerate(papers, 1):
            title_tag = paper.find('h3').find('a')
            title = title_tag.text.strip() if title_tag else "Untitled"
            if title != "Untitled" and title in visited_links.keys():
                visited_links[title]["tags"].append(papers_type)
                logging.info(f"🔁 [HF_{papers_type} #%d] Skipping already visited paper: %s", idx, title)
                continue
            total_papers += 1
            paper_link = f"https://huggingface.co{title_tag['href']}" if title_tag else "#"
            
            logging.info(f"📥 [HF_{papers_type} #%d] %s", idx, title)
            logging.info(f"🔗 [HF_{papers_type} #%d] Page URL: %s", idx, paper_link)
            res = requests.get(paper_link, timeout=10)
            paper_soup = BeautifulSoup(res.text, "html.parser")
            logging.info(f"🔗 [HF_{papers_type} #%d] Fetching paper details...", idx)
            github_link_tag = paper_soup.find('a', class_='btn inline-flex h-9 items-center', href=lambda href: href.startswith("https://github.com"))
            github_link = github_link_tag['href'] if github_link_tag else None
            if github_link:
                logging.info(f"🔗 [HF_{papers_type} #%d] GitHub: %s", idx, github_link)
            pdf_link = "https://arxiv.org/" + title_tag["href"].replace("papers/", "pdf/")

            abstract_tag = paper_soup.find('p', class_='text-blue-700 dark:text-blue-400')
            abstract = abstract_tag.text.strip() if abstract_tag else "(No abstract available)"
            
            visited_links[title] = {"paper_link": paper_link,
                                    "pdf_link": pdf_link,
                                    "abstract": abstract,
                                    "tags": [papers_type],
                                    "github_link": github_link}
            logging.info(f"📄 [HF_{papers_type} #%d] Done🧾", idx)
        logging.info(f"🎉 [HF_{papers_type}] All done, {total_papers} papers found.")
    except Exception as e:
        logging.error(f"❌ [HF_{papers_type}] Failed: {e}")

def send_email(subject, body):
    logging.info("📧 Sending email")
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    recipient = os.getenv("DIGEST_EMAIL")

    if not all([sender, password, recipient]):
        raise EnvironmentError("Missing SENDER_EMAIL, SENDER_PASSWORD, or RECIPIENT_EMAIL in environment variables.")

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

        logging.info("✅ Email sent successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")

def run():
    results = {}

    # Run all fetches concurrently
    threads = [
        threading.Thread(target=fetch_apod, args=(results,), name="Astronomy"),
        threading.Thread(target=fetch_hackernews, args=(results,), name="HackerNews"),
        threading.Thread(target=fetch_eo, args=(results,), name="EarthObservatory")
    ]

    for t in threads:
        t.start()

    run_hf(results)

    for t in threads:
        t.join()

    content = '<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px"> \
    <h1 style="text-align:center">📰 Daily Digest</h1> \
    <hr>' + "<hr>".join([
        results.get("apod", ""),
        results.get("eo", ""),
        results.get("hn", ""),
        results.get("hf", "")
    ]) + "</body></html>"
    logging.info("📄 Digest content generated successfully.")
    return content


def demo():
    logging.info("Generating local preview...")
    content = run()
    with open("digest_preview.html", "w", encoding="utf-8") as f:
        f.write(content)
    logging.info("📄 Preview saved to 'preview.html'")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, 
                        format="%(levelname)s   %(asctime)s [%(filename)s:%(lineno)d:%(funcName)s:%(threadName)s] %(message)s")
    # content = run()
    # send_email("📅 Daily Digest", content)
    demo()
