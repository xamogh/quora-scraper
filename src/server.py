import datetime
import threading
import time
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import Collector, QuoraProfileScraper
import atexit


app = Flask(__name__)


@app.route("/")
def root():
    return "Quora Answers"


def initScraper():
    print("started init scraper")
    answers = Collector()
    # QuoraProfileScraper(
    #     "https://www.quora.com/profile/Amogh-Rijal", answers
    # ).scrape()
    # print(answers)
    return answers


scheduler = BackgroundScheduler()
scheduler.add_job(
    func=initScraper,
    trigger="interval",
    seconds=3,  # 10 hours
)
scheduler.start()

if __name__ == "__main__":
    # apschduler issue with running in thread in python 3.10
    # threading.Thread(
    #     target=lambda: app.run(
    #         host="0.0.0.0", port="5500", debug=True, use_reloader=False
    #     )
    # ).start()
    app.run(host="0.0.0.0", port="5500", debug=True, use_reloader=False)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
