import threading
import os
from scraper import fetch_apod, fetch_eo, fetch_hackernews, fetch_hf
import typing
from datetime import datetime
import logging
from utils import setup_logger


def run() -> str:
    results: typing.Dict[str, str] = {}
    threads = [
        threading.Thread(target=fetch_apod, args=(results,), name="Astronomy"),
        threading.Thread(target=fetch_hackernews, args=(results,), name="HackerNews"),
        threading.Thread(target=fetch_eo, args=(results,), name="EarthObservatory")
    ]

    for t in threads:
        t.start()

    fetch_hf(results)

    for t in threads:
        t.join()

    content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Daily Digest</title>
        <link rel="stylesheet" href="static/style.css">
    </head>
    <body>
        <!-- Header -->
        <header class="header">
            <div class="container">
                <nav class="nav">
                    <div class="logo">📰 Daily Digest</div>
                    <ul class="nav-links">
                        <li><a href="#astronomy">Astronomy</a></li>
                        <li><a href="#earth">Earth</a></li>
                        <li><a href="#tech">Tech News</a></li>
                        <li><a href="#papers">Papers</a></li>
                    </ul>
                    <div class="date-badge">{datetime.now().strftime('%a, %b %d, %Y')}</div>
                </nav>
            </div>
        </header>

        <!-- Main Content -->
        <main class="main-content">
            <div class="container">
                <!-- Hero Section -->
                <section class="hero">
                    <h1>Your Daily Tech & Science Digest</h1>
                    <p>Stay updated with the latest in astronomy, earth sciences, technology news, and cutting-edge research papers</p>
                </section>

                <!-- Content Grid -->
                <div class="content-grid">
                    <!-- APOD and Earth Observatory Row -->
                    <div class="two-column">
                        <!-- APOD Section -->
                        <section id="astronomy" class="card apod-card">
                            <div class="card-header">
                                <div class="card-icon">✨</div>
                                <div>
                                    <h2 class="card-title">Astronomy Picture of the Day</h2>
                                    <p class="card-subtitle">NASA's daily cosmic wonder</p>
                                </div>
                            </div>
                            <div class="card-content">
                                {results.get("apod", "<div style='text-align: center; color: #666;'>Failed to load APOD content</div>")}
                            </div>
                        </section>

                        <!-- Earth Observatory -->
                        <section id="earth" class="card eo-card">
                            <div class="card-header">
                                <div class="card-icon">🌍</div>
                                <div>
                                    <h2 class="card-title">Earth Observatory</h2>
                                    <p class="card-subtitle">Our planet from above</p>
                                </div>
                            </div>
                            <div class="card-content">
                                {results.get("eo", "<div style='text-align: center; color: #666;'>Failed to load Earth Observatory content</div>")}
                            </div>
                        </section>
                    </div>

                    <!-- Hacker News Section -->
                    <section id="tech" class="card hn-card featured-section">
                        <div class="card-header">
                            <div class="card-icon">🔥</div>
                            <div>
                                <h2 class="card-title">Hacker News Top 10</h2>
                                <p class="card-subtitle">What's trending in tech</p>
                            </div>
                        </div>
                        <div class="card-content">
                            {results.get("hn", "<div style='text-align: center; color: #666;'>Failed to load Hacker News content</div>")}
                        </div>
                    </section>

                    <!-- Hugging Face Papers -->
                    <section id="papers" class="card hf-card-container featured-section">
                        <div class="card-header">
                            <div class="card-icon">📚</div>
                            <div>
                                <h2 class="card-title">Latest Research Papers</h2>
                                <p class="card-subtitle">Cutting-edge AI & ML research</p>
                            </div>
                        </div>
                        
                        <!-- Paper Filters -->
                        <div class="paper-filters" id="hf-filters">
                            <button class="filter-btn active" data-tag="ALL" onclick="filterPapers('ALL')">All Papers</button>
                            <button class="filter-btn" data-tag="DAILY" onclick="filterPapers('DAILY')">Daily</button>
                            <button class="filter-btn" data-tag="WEEKLY" onclick="filterPapers('WEEKLY')">Weekly</button>
                            <button class="filter-btn" data-tag="MONTHLY" onclick="filterPapers('MONTHLY')">Monthly</button>
                            <button class="filter-btn" data-tag="TRENDING" onclick="filterPapers('TRENDING')">Trending</button>
                        </div>

                        <!-- Papers Content -->
                        <div class="card-content">
                            {results.get("hf", "<div style='text-align: center; color: #666;'>Failed to load research papers</div>")}
                        </div>
                    </section>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="footer">
            <div class="container">
                <p>&copy; 2025 Daily Digest. Curated with ❤️ for the curious minds.</p>
            </div>
        </footer>
        <script src="static/script.js"></script>
    </body>
    </html>
    """

    logging.info("📄 Content generated successfully.")
    return content

def main():
    logging.info("🚀 Generating local preview...")
    content = run()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    with open(f"archive/{datetime.now().strftime('%Y-%m-%d')}.html", "w", encoding="utf-8") as f:
        f.write(content)
    logging.info(f"📄 Contents saved to 'index.html' and 'archive/{datetime.now().strftime('%Y-%m-%d')}.html'")

if __name__ == "__main__":
    os.makedirs("archive", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("logs/main", exist_ok=True)
    os.makedirs("logs/apod", exist_ok=True)
    os.makedirs("logs/earthobservatory", exist_ok=True)
    os.makedirs("logs/hackernews", exist_ok=True)
    os.makedirs("logs/huggingface", exist_ok=True)

    main_logging = setup_logger("main")
    # Redirect root logger to main_logging
    logging.root.handlers = main_logging.handlers
    logging.root.setLevel = main_logging.level
    main()