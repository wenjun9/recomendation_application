# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os

from newspaper import Article

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

import cnn_news_scraper
from cloudAMQP_client import CloudAMQPClient

DEDUPE_NEWS_TASK_QUEUE_URL = "amqp://kdwwvmdf:UEI50D5c6p6BQCLm-niiAis-y9kU-jc4@otter.rmq.cloudamqp.com/kdwwvmdf"
DEDUPE_NEWS_TASK_QUEUE_NAME = "tap_news_dedupe_news_task_queue"
SCRAPE_NEWS_TASK_QUEUE_URL = "amqp://lvfbknos:oRrV2mPmKiz0y6FWYbJ-Pf4pUZ8JFB6f@otter.rmq.cloudamqp.com/lvfbknos"
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap_news_scrape_news_task_queue"

SLEEP_TIME_IN_SECONDS = 5

dedupe_news_queue_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
scrape_news_queue_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)

def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        print 'message is broken'
        return

    task = msg
    ''' Below is using xPath'''
    # text = None
    #
    # #we support cnn only num_of_new_news
    # if task['source'] == 'cnn':
    #     print 'Scraping CNN news'
    #     text = cnn_news_scraper.extract_news(task['url'])
    # else:
    #     print 'News source [%s] is not supported.' % task['source']
    #
    # task['text'] = text
    # dedupe_news_queue_client.sendMessage(task)

    article = Article(task['url'])
    article.download()
    article.parse()

    print article.text

    task['text'] = article.text

    dedupe_news_queue_client.sendMessage(task)

while True:
    # fetch msg from queue
    if scrape_news_queue_client is not None:
        msg = scrape_news_queue_client.getMessage()
        if msg is not None:
            # Handle message
            try:
                handle_message(msg)
            except Exception as e:
                print e
                pass
        scrape_news_queue_client.sleep(SLEEP_TIME_IN_SECONDS)
