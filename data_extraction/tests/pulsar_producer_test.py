from ..pulsar_producer import PulsarProducer
import pulsar

def test_sednJsonDataTest():
    #Set up producer and send message
    message = "Hello"
    topic = "testTopic"
    producer = PulsarProducer()
    producer.set_topic(topic)
    producer.send_data(('Hello').encode('utf-8'))
    producer.close_client()

    #Set up consumer
    client = pulsar.Client('pulsar://localhost:6650')
    consumer = client.subscribe(topic, 'testSubscription')

    # Consume message
    result = consumer.receive()
    consumer.acknowledge(result)
    client.close()

    #Assert
    assert message == result.data().decode()


def flush_topic():
    """A consumer that will read everything from the pulsar topic to 'reset it.'"""
    topic = "testTopic"
    client = pulsar.Client('pulsar://localhost:6650')
    consumer = client.subscribe(topic, 'testSubscription')
    while True:
        msg = consumer.receive()
        print("Received message '{}' id='{}'".format(msg.data(), msg.message_id()))
        consumer.acknowledge(msg)