import threading
import os
from scraper import fetch_apod, fetch_eo, fetch_hackernews, fetch_hf, fetch_tarot
import typing
from datetime import datetime
import logging
from utils import setup_logger


def run() -> str:
    results: typing.Dict[str, str] = {}
    threads = [
        threading.Thread(target=fetch_apod, args=(results,), name="Astronomy"),
        threading.Thread(target=fetch_hackernews, args=(results,), name="HackerNews"),
        threading.Thread(target=fetch_eo, args=(results,), name="EarthObservatory"),
        threading.Thread(target=fetch_tarot, args=(results,), name="Tarot")
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
                        <li><a href="#tarot">Tarot</a></li>
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
                    <!-- APOD, Earth Observatory, and Tarot Row -->
                    <div class="three-column">
                        <!-- APOD Section -->
                        <section id="astronomy" class="card apod-card">
                            <div class="card-media" id="apod-media"></div>
                            <div class="card-content-wrapper">
                                <div class="card-header">
                                    <div class="card-icon">✨</div>
                                    <div>
                                        <h2 class="card-title">Astronomy Picture</h2>
                                        <p class="card-subtitle">NASA's daily cosmic wonder</p>
                                    </div>
                                </div>
                                <div class="card-content" id="apod-content">
                                    {results.get("apod", "<div style='text-align: center; color: #666;'>Failed to load APOD content</div>")}
                                </div>
                            </div>
                        </section>

                        <!-- Earth Observatory -->
                        <section id="earth" class="card eo-card">
                            <div class="card-media" id="eo-media"></div>
                            <div class="card-content-wrapper">
                                <div class="card-header">
                                    <div class="card-icon">🌍</div>
                                    <div>
                                        <h2 class="card-title">Earth Observatory</h2>
                                        <p class="card-subtitle">Our planet from above</p>
                                    </div>
                                </div>
                                <div class="card-content" id="eo-content">
                                    {results.get("eo", "<div style='text-align: center; color: #666;'>Failed to load Earth Observatory content</div>")}
                                </div>
                            </div>
                        </section>

                        <!-- Tarot Section -->
                        <section id="tarot" class="card tarot-card">
                            <div class="card-media" id="tarot-media"></div>
                            <div class="card-content-wrapper">
                                <div class="card-header">
                                    <div class="card-icon">🔮</div>
                                    <div>
                                        <h2 class="card-title">Daily Tarot</h2>
                                        <p class="card-subtitle">Your mystical guidance</p>
                                    </div>
                                </div>
                                <div class="card-content" id="tarot-content">
                                    {results.get("tarot", "<div style='text-align: center; color: #666;'>Failed to load Tarot content</div>")}
                                </div>
                            </div>
                        </section>
                        
                        <!-- Navigation Arrows -->
                        <button class="card-nav prev" onclick="prevCard()" aria-label="Previous card">‹</button>
                        <button class="card-nav next" onclick="nextCard()" aria-label="Next card">›</button>
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
    # Setup main logger first before any other logging
    main_logger = setup_logger("main")
    main_logger.info("🚀 Generating local preview...")
    
    content = run()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    with open(f"archive/{datetime.now().strftime('%Y-%m-%d')}.html", "w", encoding="utf-8") as f:
        f.write(content)
    main_logger.info(f"📄 Contents saved to 'index.html' and 'archive/{datetime.now().strftime('%Y-%m-%d')}.html'")

if __name__ == "__main__":
    os.makedirs("archive", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("logs/main", exist_ok=True)
    os.makedirs("logs/apod", exist_ok=True)
    os.makedirs("logs/earthobservatory", exist_ok=True)
    os.makedirs("logs/hackernews", exist_ok=True)
    os.makedirs("logs/tarot", exist_ok=True)
    os.makedirs("logs/huggingface", exist_ok=True)

    main()