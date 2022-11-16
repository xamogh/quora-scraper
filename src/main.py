import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


class Scraper:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=chrome_options)


class QuoraProfileScraper(Scraper):
    def __init__(self, url):
        self.url = url
        Scraper.__init__(self)

    def scrape(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        answerButton = self.__get_answer_button()
        if answerButton:
            answerButton.click()

        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "q-box.qu-pt--medium.qu-borderBottom")
            )
        )

        answerDivs = self.driver.find_elements(
            By.CLASS_NAME, "q-box.qu-pt--medium.qu-borderBottom"
        )

        for div in answerDivs:
            print(div.text)

    def __get_answer_button(self):
        answer_buttons = self.driver.find_elements(
            By.CLASS_NAME,
            "iyYUZT.ClickWrapper___StyledClickWrapperBox-zoqi4f-0.qu-cursor--pointer.qu-tapHighlight--white",
        )
        for button in answer_buttons:
            if button.text.__contains__("Answers"):
                innerContentArr = button.text.split()
                print(innerContentArr, innerContentArr[1])
                if innerContentArr[1] == "Answers":
                    return button


if __name__ == "__main__":
    amoghQuoraScraper = QuoraProfileScraper("https://www.quora.com/profile/Amogh-Rijal")
    amoghQuoraScraper.scrape()
