from bs4 import BeautifulSoup;
from selenium import webdriver;
from selenium.webdriver.chrome.options import Options

class Scraper:
    def __init__(self):
        chrome_options = Options();
        chrome_options.add_argument("--headless");
        chrome_options.add_argument("--disable-extensions");
        chrome_options.add_argument("--disable-gpu");

        self.driver = webdriver.Chrome(options=chrome_options);

class QuoraProfileScraper(Scraper):
    def __init__(self, url):
        self.url = url;
        Scraper.__init__(self);

    def scrape(self): 
       self.driver.get(self.url); 
       print(self.driver.page_source.encode("utf-8"));

if __name__ == "__main__":
    amoghQuoraScraper = QuoraProfileScraper("https://www.quora.com/profile/Amogh-Rijal");
    amoghQuoraScraper.scrape();

