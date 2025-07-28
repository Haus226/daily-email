import threading
import os
from scraper import fetch_apod, fetch_eo, fetch_hackernews, fetch_hf, format_images_of_the_day
import typing
from datetime import datetime
import logging
from logger import setup_logger


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
        <html>
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1000px;
                margin: auto;
                padding: 20px;
                background: #fafafa;
                color: #333;
            }}
            h1, h2 {{
                text-align: center;
            }}
            section.card {{
                background: #fff;
                padding: 16px;
                border-radius: 10px;
                box-shadow: 0 0 5px rgba(0,0,0,0.05);
                margin: 20px 0;
            }}
            .tag {{
                display: inline-block;
                background: #eee;
                border-radius: 4px;
                padding: 2px 6px;
                margin: 2px 6px 6px 0;
                font-size: 12px;
                color: #444;
            }}
            .hf-card {{
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 12px;
                background: #fff;
            }}
            .hf-card h3 {{
                font-size: 16px;
                margin-bottom: 6px;
            }}
            .hf-card .abstract {{
                font-size: 14px;
                color: #555;
                line-height: 1.5;
            }}
            button {{
                padding: 6px 12px;
                margin: 4px;
                border: none;
                border-radius: 5px;
                background: #ddd;
                cursor: pointer;
            }}
            button:hover {{
                background: #ccc;
            }}
            button.active {{
                background: #2b6cb0;
                color: white;
            }}

            @media (max-width: 600px) {{
                .images-row {{
                    flex-direction: column !important;
                }}
                .images-row > div:first-child {{
                    flex: none !important;
                    max-width: 150px;
                    margin: 0 auto 10px auto;
                }}
            }}
        </style>
        <script>
        function sortPapersByDateOnce() {{
            const container = document.getElementById('hf-grid');
            const cards = Array.from(document.querySelectorAll('.hf-card'));
            cards.sort((a, b) => {{
                const dateA = new Date(a.dataset.date);
                const dateB = new Date(b.dataset.date);
                return dateB - dateA;  // newest first
            }});

            // Clear and append in sorted order
            container.innerHTML = '';
            cards.forEach(card => container.appendChild(card));
        }}

        let currentFilterTag = 'ALL';
        window.onload = () => {{
            sortPapersByDateOnce();
            filterPapers('ALL');  // optional default
        }};

        function filterPapers(tag) {{
            currentFilterTag = tag;
            document.querySelectorAll('.hf-card').forEach(card => {{
                const tags = card.dataset.tags.split(" ");
                card.style.display = (tag === "ALL" || tags.includes(tag)) ? "block" : "none";
            }});
            updateFilterButtonStyles();
        }}


        function updateFilterButtonStyles() {{
            document.querySelectorAll('#hf-filters button[data-tag]').forEach(btn => {{
                    btn.classList.toggle('active', btn.dataset.tag === currentFilterTag);
            }});
        }}

        </script>
        </head>
        <body>
        <h1>📰 Daily Digest</h1>
        <section class="card">{results.get("apod", "")}</section>
        <section class="card">{results.get("eo", "")}</section>
        <section class="card">{results.get("hn", "")}</section>
        <section class="card">{results.get("hf", "")}</section>
        </body></html>
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
    logging.root.setLevel(main_logging.level)
    main()


