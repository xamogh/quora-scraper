from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from enum import Enum
import typing

## @todo ->
## 1) Add scrolling to get more data
## 2) Date parsing
## 3) Add previous question/answer recognization and stop scraping if data repeats
## 4) Server to run at times


class ScrapedAnswer:
    def __init__(self, logger: typing.Callable[["ScrapedAnswer"], None]) -> None:
        self.logger = logger

    def setDate(self, date: str) -> "ScrapedAnswer":
        self.date = date
        return self

    def setQuestion(self, question: str) -> "ScrapedAnswer":
        self.question = question
        return self

    def setAnswer(self, answer: str) -> "ScrapedAnswer":
        self.answer = answer
        return self

    def create(self) -> dict[str, str]:
        if not self.date or not self.question or not self.answer:
            self.logger(self)
        return {"date": self.date, "question": self.question, "answer": self.answer}


class QuoraSelectors(Enum):
    Answer_Container_Div = "q-box.qu-pt--medium.qu-borderBottom"
    Possible_Tab_Buttons = "iyYUZT.ClickWrapper___StyledClickWrapperBox-zoqi4f-0.qu-cursor--pointer.qu-tapHighlight--white"
    Answer_Date_Addr = (
        "q-text.qu-dynamicFontSize--small.qu-color--gray.qu-passColorToLinks"
    )
    Answer_Question = "q-text.qu-truncateLines--5.puppeteer_test_question_title"
    Answer_Answer = "q-box.spacing_log_answer_content.puppeteer_test_answer_content"


class Scraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=chrome_options)


class QuoraProfileScraper(Scraper):
    def __init__(self, url: str, collector: list[dict[str, str]]):
        self.url = url
        self.collector = collector
        Scraper.__init__(self)

    def scrape(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        answer_button = get_answer_button(self.driver)
        if answer_button:
            answer_button.click()

        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, QuoraSelectors.Answer_Container_Div.value)
            )
        )
        answerContainerDivs = self.driver.find_elements(
            By.CLASS_NAME, QuoraSelectors.Answer_Container_Div.value
        )
        for div in answerContainerDivs:
            date_addr = div.find_element(
                By.CLASS_NAME, QuoraSelectors.Answer_Date_Addr.value
            )
            question = div.find_element(
                By.CLASS_NAME, QuoraSelectors.Answer_Question.value
            )
            answer = div.find_element(By.CLASS_NAME, QuoraSelectors.Answer_Answer.value)
            createdData = (
                ScrapedAnswer(logger)
                .setDate(date_addr.text)
                .setAnswer(answer.text)
                .setQuestion(question.text)
                .create()
            )
            self.collector.append(createdData)


def get_answer_button(driver: WebDriver):
    answer_buttons = driver.find_elements(
        By.CLASS_NAME,
        QuoraSelectors.Possible_Tab_Buttons.value,
    )
    for button in answer_buttons:
        if button.text.__contains__("Answers"):
            innerContentArr = button.text.split()
            if innerContentArr[1] == "Answers":
                return button


# extend to more
def logger(data: ScrapedAnswer):
    print(data)


if __name__ == "__main__":
    answers = []
    amoghQuoraScraper = QuoraProfileScraper(
        "https://www.quora.com/profile/Amogh-Rijal", answers
    )
    amoghQuoraScraper.scrape()
    print(answers)
