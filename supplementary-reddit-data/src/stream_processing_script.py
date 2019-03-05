"""
NAME:   SUPPLEMENTARY REDDIT DATA STREAM PROCESSING SCRIPT

ABOUT:  Script subscribes to Pulsar topic to collect Reddit Comment JSON data
        (post Sentiment Analysis), acquires additional Reddit information
        (via RedditClient), and publishes data to new Pulsar topic.


AUTHOR: Julia Garbuz (garbu007@umn.edu)
"""

import pulsar

from supplementary_reddit_data_service.supplementary_reddit_data_service \
    import SupplementaryRedditDataService

class PulsarProducer:
    """
    A simple class that creates a pulsar producer.
    """

    def __init__(self, client, topic):
        """
        Initializes a producer ny giving it the default topic and a given client.
        :param client: The location of the pulsar supplementary_reddit_data_service that must be running in order
        for this class to work properly.
        Will be set to 'pulsar://localhost:6650' if no argument is given.
        """
        if client is None:
            # 'Set client to the default when running on local machine'
            client = 'pulsar://pulsar-elb-1485389051.us-west-2.elb.amazonaws.com:6650'

        self.pulsar_client = pulsar.Client(client)
        self.set_topic(topic)

    def set_topic(self, topic):
        self.producer = self.pulsar_client.create_producer(topic)

    def send_data(self, data):
        """
        Sends data to the specified pulsar topic.
        :param data: Has to be in a binary format
        """
        self.producer.send(data)

    def close_client(self):
        self.pulsar_client.close()

    def produce_data(self, producer, json, limit):
        """
        This produces all the data in the table fh-bigquery.reddit_comments.2015_05
        using a PulsarProducer.
        :param producer: A PulsarProducer that will produce the data.
        :param limit: Limits the number of rows that will be produced.
        """
        producer.send_data(json)


if __name__ == '__main__':

    service = SupplementaryRedditDataService()

    pulsar_server = 'pulsar://35.188.130.50:6650'

    # Initialize the client, consumer, and topic
    consumer_topic = "sentiment_comments"
    producer_topic = "supplement_reddit_data"
    client = pulsar.Client(pulsar_server)
    consumer = client.subscribe(consumer_topic, 'comment_sub')

    # Initialize the producer for after sentiment processing
    producer = PulsarProducer(pulsar_server, producer_topic)

    while True:

        record = consumer.receive()  # get comment record (in binary)
        consumer.acknowledge(record)  # acknowledge receipt

        if record is not None:

            # Decode the binary to json string
            data_before_processing = record.data().decode('utf8')

            data_after_processing = service.add_supplementary_reddit_data(data_before_processing)

            producer.send_data(data_after_processing.encode('utf-8'))

            record = None
