# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import hashlib
import os
import redis

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import news_api_client
from cloudAMQP_client import CloudAMQPClient

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

NEWS_TIME_OUT_IN_SECONDS = 3600 * 24
SLEEP_TIME_IN_SECONDS = 10

SCRAPE_NEWS_TASK_QUEUE_URL = "amqp://lvfbknos:oRrV2mPmKiz0y6FWYbJ-Pf4pUZ8JFB6f@otter.rmq.cloudamqp.com/lvfbknos"
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap_news_scrape_news_task_queue"

NEWS_SOURCES = [
    'abc-news',
    'bbc-news',
    'bbc-sport',
    'bloomberg',
    'cnn',
    'cbs-news',
    'entertainment-weekly',
    'espn',
    'fox-news',
    'fox-sports',
    'ign',
    'nfl-news',
    'techcrunch',
    'the-new-york-times',
    'the-wall-street-journal',
    'the-washington-post'
]

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
cloudAMQP_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)

while True:
    news_list = news_api_client.getNewsFromSource(NEWS_SOURCES)

    num_of_new_news = 0

    for news in news_list:
        news_digest = hashlib.md5(news['title'].encode('utf-8')).digest().encode('base64')

        if redis_client.get(news_digest) is None:
            num_of_new_news += 1
            news['digest'] = news_digest

            if news['publishedAt'] is None:
                # format: YYYY-MM-DDTHH:MM:SSZ in UTC
                news['publishedAt'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            redis_client.set(news_digest, news)
            redis_client.expire(news_digest, NEWS_TIME_OUT_IN_SECONDS)

            cloudAMQP_client.sendMessage(news)

    print "Fetched %d new news." % num_of_new_news

    cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)
