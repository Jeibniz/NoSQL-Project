""" AUTHOR: Jonathan Persgården (jpersgarden@gmail.com) """

import pulsar

class PulsarProducer:
    """
    A simple class that creates a pulsar producer.
    """
    def __init__(self, client = None):
        """
        Initializes a producer ny giving it the default topic and a given client.

        :param client: The location of the pulsar service that must be running in order
                       for this class to work properly.
                       Will be set to 'pulsar://localhost:6650' if no argument is given.
        """
        if client is None:
            'Set client to the default when running on local machine'
            client = 'pulsar://localhost:6650'
        self.pulsar_client =  pulsar.Client(client)
        self.set_topic()

    def set_topic(self, topic = "comments"):
        self.producer = self.pulsar_client.create_producer(topic)

    def send_data(self, data):
        """
        Sends data to the specified pulsar topic. Before the data is
        sent it is converted into binary. This is done by encoding it with utf-8.

        :param data: Tha dat that will be produced.
        """
        self.producer.send(data.encode('utf8'))

    def close_client(self):
        self.pulsar_client.close()