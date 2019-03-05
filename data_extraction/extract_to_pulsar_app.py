""" AUTHOR: Jonathan Persgården (jpersgarden@gmail.com) """

from .big_query_client import BigQueryClient
from .pulsar_producer import PulsarProducer

def main():
    """
    This will use the classes defined in DataFetcher to fetch the data from
    BigQuery and send it to a Pulsar topic.
    """

    #Set up objects
    client = BigQueryClient()
    producer = PulsarProducer()

    #Send data from big query to a given pulsar topic.
    # 500 is the limit of data points fetched.
    client.produce_json_data(producer, 500)


    producer.close_client()
    #Send data to a pulsar topic


if __name__ == "__main__": main()