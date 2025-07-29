import requests
from bs4 import BeautifulSoup

def crawl_quote(page_num):
    quotes_lst = []
    base_url = "https://www.goodreads.com/quotes?{page_num}".format(page_num=str(page_num))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find_all('div', class_='quoteText')
        for quote in quotes:
            q = quote.get_text(strip=True)
            quotes_lst.append(q)
        with open('quotes.txt', 'a', encoding='utf-8') as file:
            for quote in quotes_lst:
                file.write(quote + '\n')
    else:
        print("Failed to retrieve quotes.")


if __name__ == "__main__":
    for i in range(1, 101):
        print(f"Crawling page {i}...")
        crawl_quote(i)