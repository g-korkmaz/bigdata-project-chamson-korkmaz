# Import libraries
import tweepy
from kafka import KafkaProducer
import logging

# Token to use to connect to twitter API
bearerToken = "AAAAAAAAAAAAAAAAAAAAAOhKjQEAAAAAEbWsHojF8OCltDxEIDNtHYFnxu8%3Dd7QNk6neSulbVUYDZ2FBTBq3MxnwUbnVieP6U0zHqsjDlwmAtz"

# Creating the kafka producer 
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# Specify topic and search term
search_term = 'Biden'
topic_name = 'twitter'

class TweetListener(tweepy.StreamingClient):

    # Sending every new data to the kafka broker under the defined topic
    def on_data(self, raw_data):
        logging.info(raw_data)
        producer.send(topic_name, value=raw_data)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    # Filter tweets containing the search term
    def start_streaming_tweets(self, search_term):
        self.add_rules(tweepy.StreamRule(search_term))
        self.filter()

if __name__ == '__main__':
    twitter_stream = TweetListener(bearerToken)
    twitter_stream.start_streaming_tweets(search_term)