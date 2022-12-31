# Import libraries
from elasticsearch6 import Elasticsearch
from kafka import KafkaConsumer
import json
from textblob import TextBlob

# Connect to elasticSearch
es = Elasticsearch('http://localhost:9200')

def main():

    # Create kafka consumer of the topic "twitter"
    consumer = KafkaConsumer("twitter", auto_offset_reset='earliest')

    # For every new tweet
    for msg in consumer:
        dict_data = json.loads(msg.value)["data"]
        tweet = TextBlob(dict_data["text"])
        # Use textBlob integrated sentiment analyzer
        polarity = tweet.sentiment.polarity
        tweet_sentiment = ""
        if polarity > 0:
            tweet_sentiment = 'positive'
        elif polarity < 0:
            tweet_sentiment = 'negative'
        elif polarity == 0:
            tweet_sentiment = 'neutral'

        # add text & sentiment to ElasticSearch
        es.index(
                    index="tweet_biden",
                    doc_type="test_doc",
                    body={
                    "message": dict_data["text"],
                    "sentiment": tweet_sentiment
                    }
                )
                # Print tweet and its associated sentiment in console
        print(str(tweet))
        print(tweet_sentiment)
        print('\n')

if __name__ == "__main__":
    main()