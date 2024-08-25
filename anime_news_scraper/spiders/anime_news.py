import scrapy
from bs4 import BeautifulSoup
import requests
import os
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector


class AnimeNewsSpider(scrapy.Spider):
    name = "anime_news"
    allowed_domains = ["www.animenewsnetwork.com"]
    # start_urls = ["https://www.animenewsnetwork.com/news/"]
    base_url = "https://www.animenewsnetwork.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    data_dir = os.path.join("data")
    custom_settings = {
        "FEEDS": {
            os.path.join(data_dir, "anime_details.json"): {
                "format": "json",
                "encoding": "utf-8",
                "overwrite": True,
            },
        },
        "LOG_FILE": os.path.join(data_dir, "anime_details.log"),
    }

    def get_soup(self, url: str):
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "lxml")
        return soup

    def get_urls(self):
        anime_news_url = f"{self.base_url}/news/"
        soup = self.get_soup(anime_news_url)
        all_a = soup.select("div.herald div.wrap div h3 a")
        all_urls = [f"{self.base_url}{a.get('href')}" for a in all_a]
        return all_urls

    def start_requests(self):
        anime_urls = self.get_urls()
        for anime_url in anime_urls:
            print("anime_url: ", anime_url)
            yield scrapy.Request(url=anime_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        file = os.path.join("data", "index.html")
        html = ""
        with open(file, "r", encoding="utf-8") as html_file:
            # html_file.write(response.text)
            for line in html_file.read():
                html += line

        response = Selector(text=html)
        title = response.css("#page_header::text").getall()[-1].strip()
        time = response.css('#page-title small time::attr("datetime")').get()
        post_by = (
            response.css("#page-title::text").getall()[-1].strip().replace("by ", "")
        )
        intro_list = response.css("div.text-zone div.intro *::text").getall()
        intro = "".join([text.strip() for text in intro_list])
        content_list = response.css("div.text-zone div.meat *::text").getall()
        content = " ".join([text.strip() for text in content_list])

        items = {
            "title": title,
            "time": time,
            "post_by": post_by,
            "intro": intro,
            "content": content,
        }
        yield items


if __name__ == "__main__":
    # process = AnimeNewsSpider()
    # process.parse("")
    # print(process.page_urls)

    process = CrawlerProcess()
    process.crawl(AnimeNewsSpider)
    process.start()
