# **Big Data project**

## **Introduction**

The purpose of this project is to have a continuous stream of tweets filtered by one subject and apply some sentiment analysis to it.
For this, we'll use kafka, elasticsearch and kibana. 

We made a system that follows this architecture : 
![architecture of project](/pics/architecture.png "Schema of the architecture")

## **Kafka**

### ***Installation***

First, you'll need to download kafka

````bash
    wget https://dlcdn.apache.org/kafka/3.3.1/kafka_2.13-3.3.1.tgz
````

*Note : You can also clone our git repository and you will directly find the corresponding folder*

Then you need to work from the installed folder for the rest of kafka initialisation.

1. **Zookeeper**

Start Zookeeper with the following command : 

````bash
    bin/zookeeper-server-start.sh config/zookeeper.properties
````
2. **Kafka server**

Then start the kafka broker with : 

````bash
    bin/kafka-server-start.sh config/server.properties
````

### ***Producer***

The producer will retrive tweets from twitter and send them so the kafka broker using a specific topic. 

To connect to twitterAPI 2.0 we used the tweepy library wich is a python library developped by Twitter to allow some developper work. 

The chosen subject was Biden so we filtered the tweets to retrieve all those that containt "Biden". 

All the tweets will be published under the sopic *"twitter"*. 

Here's the most important part of the code where we define the filter, the topic and the streaming client : 

````python

producer = KafkaProducer(bootstrap_servers='localhost:9092')
search_term = 'Biden'
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
````

You can open a new terminal and run the code : 

````bash
    python3 kafka_producer.py
````

### ***Consumer***

If you want to visualize raw tweets directly in the terminal, you can run the consumer code. 

````bash
    python3 kafka_consumer.py
````
## **Streaming**

### **ELasticSearch**

Elasticsearch is a distributed, free and open search and analytics engine for all types of data, including textual, numerical, geospatial, structured, and unstructured. So we decided to use it to send our data to it and thn be able to visualize everything in Kibana.

***Installation***

*Windows*
Download ElasticSearch from this [link](https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.0-windows-x86_64.zip)
````bash
    cd C:/workspace(or replace by the path of the folder you created) 
    Expand-Archive elasticsearch-7.10.0-windows-x86_64.zip
````

*Linux/Unix*
Download ElasticSearch from this [link](https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.0-darwin-x86_64.tar.gz) if you're on Mac and this [one](https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.0-linux-x86_64.tar.gz) if you're on a Linux machine.
````bash
    cd /users/cflond/workspace (or replace by the path of the folder you created)
    tar -xvf elasticsearch-7.10.0-darwin-x86_64.tar.gz
````

Then in the */config/elasticsearch.yml* file, you can uncomment the cluster's name and change it. 
At the end you'll need to add those lines : 
````yaml
cluster.routing.allocation.disk.watermark.low: 1gb
cluster.routing.allocation.disk.watermark.high: 1gb
cluster.routing.allocation.disk.watermark.flood_stage: 1gb
````

***Starting it***

You are now ready to start ElasticSearch by going into you're ealsticsearch bin folder and executing the command : 

````bash
    ./elasticsearch.bat #Windows
    ./elasticsearch #Mac or Linux
````

If you go to (http://localhost:9200) , you should see something like that : 
![Screenshot of localhost 92000 ElasticSearch](/pics/elasticsearch.png "Screenshot of localhost 92000 ElasticSearch"


### **Consumer**

To stream the content, we use the *kafkaConsumer* function from the *kafka* library where we only need to indicate the topic from which to read. 

````python
    consumer = KafkaConsumer("twitter", auto_offset_reset='earliest')
````

*Note: We set the auto_offset_reset to earliest to get more tweets.*

Once the analysis done, we send the tweet and the corresponding sentiment to elasticSearch : 
````python
     es.index(
                    index="tweet_biden",
                    doc_type="test_doc",
                    body={
                    "message": dict_data["text"],
                    "sentiment": tweet_sentiment
                    }
                )
````

We also printed out in console the tweets and associated sentiment so you should be able to visualize the on-going flow.

To start the consumer you'll only need to start the code : 
````bash
    python3 stream.py
````

## **Visualize**

### **Kibana**
Finally, we wanted to add one last feature to visualize the tendancies of the sentiment regarding our filter. For this, we used Kibana.

***Installation***

*Windows*
Download Kibana from this [link](https://artifacts.elastic.co/downloads/kibana/kibana-7.10.0-windows-x86_64.zipp)
````bash
    cd C:/workspace(or replace by the path of the folder you created) 
    Expand-Archive kibana-7.10.0-windows-x86_64.zip
````

*Linux/Unix*
Download ElasticSearch from this [link](https://artifacts.elastic.co/downloads/kibana/kibana-7.10.0-darwin-x86_64.tar.gzz) if you're on Mac and this [one](https://artifacts.elastic.co/downloads/kibana/kibana-7.10.0-linux-x86_64.tar.gz) if you're on a Linux machine.
````bash
    cd /users/cflond/workspace (or replace by the path of the folder you created)
    tar -xvf kibana-7.10.0-*.zip

````

***Starting it***

You are now ready to start ElasticSearch by going into you're ealsticsearch bin folder and executing the command : 

````bash
    ./kibana.bat #Windows
    ./kibana #Mac or Linux
````

If you go to (http://localhost:5601) , you should be able to navigate through Kibana.

***Note*** : For the system to work, you need to make sure that you've started all those elements in the right order : 
1. Zookeeper
2. Kafka server
3. Kafka producer *kafka_producer.py*
4. (optional) Kafka consumer *kafka_consumer.py*
5. ElasticSearch
6. Kafka consumer *stream.py*
7. Kibana

### **Visualization**

Once in Kibana, create a new index pattern (http://localhost:5601/app/management/kibana/indexPatterns/create)

You should see an index named *tweet_biden*, then click on create pattern.
![Screenshot of index pattern creation](/pics/indexCreating.png "Screenshot of index pattern creation")

Now if you go under the visualization menu you should be able to create a new visualization. Here we chose Lens.
![Screenshot of visualization menu](/pics/visualization.png "Screenshot of visualization menu")

Finally, if you drag and drop the sentiment keyword and choose the donuts representation you should obtain something similar to that : 
![Donut visualization](/pics/donut1.png)

And if you wait a few seconds/ minuts and refresh, the value will change because they take into account new data.
![Donut visualization](/pics/donut2.png)

## **Personalization**

If you want to apply the same analysis to other subjects, you can simply change the *kafka_producer.py* line : 
````python
search_term = 'Biden' # Replace Biden by what you want
````

And change the index name in the *stream.py* code. 

Then you'll only need to restart both of these codes and redo the visualization manipulation on Kibana.

*Note : Once over, don't forget to shut down everything.*

## **Authors**

CHAMSON Yanis \
KORKMAZ Gabrielle

