import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from enum import Enum
import typing

## @todo ->
## 2) Date parsing
## 3) Add previous question/answer recognization and stop scraping if data repeats (from server / db persist)
## 4) Server to run at times

class DatumType(typing.TypedDict):
    question: str
    answer: str
    date: str

class Collector:
    def __init__(self) -> None:
        self.data: list[DatumType] = []
        self.questionToAnswerMap: dict[str, str] = {}
        self.questionAnswerExists: dict[str, bool] = {}

    def append(self, datum: DatumType):
        self.data.append(datum)
        self.questionToAnswerMap[datum["question"]] = datum["answer"]
        self.questionAnswerExists[self.__createQuestionAnswerKey(datum)] = True

    def get_list(self):
        return self.data

    def hasDatum(self, datum: DatumType):
        doesExist = self.questionAnswerExists.get(self.__createQuestionAnswerKey(datum))
        return bool(doesExist)

    def __createQuestionAnswerKey(self, datum: DatumType):
        return datum["question"] + "_____" + datum["answer"]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f"Collection list data: {self.data}"

    def __repr__(self):
        return self.__str__()


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

    def create(self) -> typing.Union[DatumType, None]:
        if not self.date or not self.question or not self.answer:
            self.logger(self)
        else:
            return {"date": self.date, "question": self.question, "answer": self.answer}


class QuoraSelectors(Enum):
    # Div that contains each block of question answer
    Answer_Container_Div = "q-box.qu-pt--medium.qu-borderBottom"
    # Answer tab button in the main profile .. i.e 5 Answers
    Possible_Tab_Buttons = "iyYUZT.ClickWrapper___StyledClickWrapperBox-zoqi4f-0.qu-cursor--pointer.qu-tapHighlight--white"
    # Div that contains date, profile / info about the answerer (inside Answer_Container_Div)
    Answer_Date_Addr = (
        "q-text.qu-dynamicFontSize--small.qu-color--gray.qu-passColorToLinks"
    )
    # Div that contains Question only (inside Answer_Container_Div)
    Answer_Question = "q-text.qu-truncateLines--5.puppeteer_test_question_title"
    # Div that contains Answer only (inside Answer_Container_Div)
    Answer_Answer = "q-box.spacing_log_answer_content.puppeteer_test_answer_content"
    # See more button on long answers
    See_More_Button = "QTextTruncated__StyledReadMoreLink-sc-1pev100-2.bSoNWX"


class Scraper:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=chrome_options)


class QuoraProfileScraper(Scraper):
    def __init__(self, url: str, collector: Collector):
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

        next_scroll_pos: int = self.driver.execute_script("return window.pageYOffset")
        current_scroll_pos: int = -1  # because 0=0 stops loop immediately

        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, QuoraSelectors.Answer_Container_Div.value)
            )
        )

        while current_scroll_pos != next_scroll_pos:
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
                answer = div.find_element(
                    By.CLASS_NAME, QuoraSelectors.Answer_Answer.value
                )
                try:
                    see_more = div.find_element(
                        By.CLASS_NAME, QuoraSelectors.See_More_Button.value
                    )
                    if see_more:
                        see_more.click()
                except:
                    pass

                createdData = (
                    ScrapedAnswer(logger)
                    .setDate(date_addr.text)
                    .setAnswer(answer.text)
                    .setQuestion(question.text)
                    .create()
                )
                if createdData:
                    if not self.collector.hasDatum(createdData):
                        self.collector.append(createdData)

            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            current_scroll_pos = next_scroll_pos
            next_scroll_pos = self.driver.execute_script("return window.pageYOffset")

            waitLoopCount = 0
            while waitLoopCount < 10:
                waitLoopCount = waitLoopCount + 1
                time.sleep(3)
                newAnswerContainerDivs = self.driver.find_elements(
                    By.CLASS_NAME, QuoraSelectors.Answer_Container_Div.value
                )
                if len(newAnswerContainerDivs) > len(answerContainerDivs):
                    break


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
    answers = Collector()
    amoghQuoraScraper = QuoraProfileScraper(
        "https://www.quora.com/profile/Amogh-Rijal", answers
    )
    amoghQuoraScraper.scrape()
    print(answers)
    print(len(answers))
