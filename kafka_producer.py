import tweepy
from kafka import KafkaProducer
import logging

bearerToken = "AAAAAAAAAAAAAAAAAAAAAOhKjQEAAAAAEbWsHojF8OCltDxEIDNtHYFnxu8%3Dd7QNk6neSulbVUYDZ2FBTBq3MxnwUbnVieP6U0zHqsjDlwmAtz"


producer = KafkaProducer(bootstrap_servers='localhost:9092')
search_term = 'Bitcoin'
topic_name = 'twitter'

class TweetListener(tweepy.StreamingClient):

    def on_data(self, raw_data):
        logging.info(raw_data)
        producer.send(topic_name, value=raw_data)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def start_streaming_tweets(self, search_term):
        self.add_rules(tweepy.StreamRule(search_term))
        self.filter()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    twitter_stream = TweetListener(bearerToken)
    twitter_stream.start_streaming_tweets(search_term)