import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re

async def fetch_news_finviz(ticker: str) -> list[str]:
    """
    Asynchronously fetches recent news headlines for a given ticker from Finviz.
    This provides a lightning-fast data pipeline for our arbitrage bot.
    """
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    # Use a standard user-agent to avoid basic blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status != 200:
                    print(f"Error: Received status code {response.status} for ticker {ticker}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Finviz stores news in a table with id 'news-table'
                news_table = soup.find(id='news-table')
                if not news_table:
                    return []
                
                headlines = []
                for row in news_table.find_all('tr'):
                    a_tag = row.find('a')
                    if a_tag:
                        headline_text = a_tag.text.strip()
                        # Clean up some common prefixes if necessary
                        headline_text = re.sub(r"^\s*-\s*", "", headline_text)
                        headlines.append(headline_text)
                        
                return headlines
        except asyncio.TimeoutError:
            print(f"Timeout while fetching news for {ticker}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching data for {ticker}: {e}")
            return []

async def get_headlines(ticker: str) -> list[str]:
    """
    Wrapper function to get headlines. 
    Can be expanded later to aggregate from multiple sources (Yahoo Finance, Bloomberg, etc.)
    """
    return await fetch_news_finviz(ticker)

# For testing the scraper independently
if __name__ == "__main__":
    test_ticker = "AAPL"
    headlines = asyncio.run(get_headlines(test_ticker))
    print(f"Fetched {len(headlines)} headlines for {test_ticker}:")
    for h in headlines[:5]:
        print(f"- {h}")
