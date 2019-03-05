# Cory Koster

# this file is used to retrieve a message from pulsar, process it using sentiment analysis,
# put the comment back together in a json object, and send to a different pulsar topic
# downstream for enrichment

# steps:
# 1. receive data
# 2. clean/standardize data (remove punctuation, all lower case, remove numbers, spaces, etc.)
# 3. load sentiment lexicon
# 4. perform sentiment analysis
# 5. load score into json record with previous data from object and send to Julia for enrichment

import pulsar
import json
import re
import decimal

# pulsar producer class
class PulsarProducer:
    
    # Initializes a producer ny giving it the default topic and a given client.
    def __init__(self, client, topic):
        # client: The location of the pulsar service that must be running in order
        # for this class to work properly.
        # Will be set to 'pulsar://localhost:6650' if no argument is given.

        if client is None:
            #'Set client to the default when running on local machine'
            client = 'pulsar://localhost:6650'
        self.pulsar_client =  pulsar.Client(client)
        self.set_topic(topic)
    
    def set_topic(self, topic):
        self.producer = self.pulsar_client.create_producer(topic)
    
    
    # Sends data to the specified pulsar topic.
    # data: Has to be in a binary format
    def send_data(self, data):
        self.producer.send(data)
    
    # closes client connection
    def close_client(self):
        self.pulsar_client.close()

    # sends data to pulsar
    def produce_data(self, producer, json, limit):
        producer.send_data(json)



def open_lexicon():

    # for tracking through the narrowed down lexicon list
    line_count = 0
    
    # list to hold the sentiment word and value (pos/neg)
    word = [[0 for i in range(2)] for j in range(48412)]
    
    # open the sentiment file
    #file = open("/Users/cory/Desktop/sentiment_analysis/sentiment/NRC-Emotion-Lexicon-Senselevel-v0.92.txt", "r")
    file = open("/Users/cory/Desktop/sentiment_analysis/sentiment/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt", "r")
    
    # remove the first blank line
    file.readline()
    # line 6 & 7 are postive/negative for each word
    for line in file:
        clean_line = line.replace('--', '\t').rstrip()
        split_line = clean_line.split('\t')
        
        if(split_line[1] == "negative"):
            word[line_count][0] = split_line[0]              # the sentiment word
            word[line_count][1] = int(split_line[2]) * -1    # negative sentiment value
            line_count = line_count + 1                      # move to the next row
        
        elif(split_line[1] == "positive"):
            word[line_count][0] = split_line[0]             # the sentiment word
            word[line_count][1] = int(split_line[2])        # positive sentiment value
            line_count = line_count + 1                     # move to the next row

    file.close()
    return word


# ** see note at bottom of page regarding this code snippet
def preprocess_comment(comment):
 
    # compile the regular expression to remove special characters, punctuation, digits, etc.
    REPLACE_NO_SPACE = re.compile("(\.)|(\$)|(\d)|(\;)|(\!)|(\')|(\?)|(\,)|(\()|(\))|(\[)|(\])")
    REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")
    
    comment = REPLACE_NO_SPACE.sub("", comment.lower())
    comment = REPLACE_WITH_SPACE.sub(" ", str(comment))
    
    return comment
# **


# find the sentiment of the comment
# and returns the score total
# lexicon = list; comment = string
def determine_sentiment(lexicon, comment):

    score = 0.0
    
    # split the comment into an iterable list
    # and remove any empty spaces from the split
    comment_words = comment.split(' ')
    comment_words = [x for x in comment_words if x != ""]
    
    # outer loop --> iterate through each row of the lexicon, only once
    # inner loop --> iterate through each word of the comment, multiple times
    # this speeds up performance as the comment will be smaller than the lexicon
    # if there is a match, add the pos/neg value of the word to the score
    for i, row in enumerate(lexicon):
        for k in comment_words:
            if(k == row[0]):
                score = score + lexicon[i][1]

    # prevent divide by 0 error if the comment doesn't have words (picture, gif, etc.)
    if(len(comment_words) == 0):
        return 0.0

    # score is divide by number of words in the comment
    # to provide more emphasis to the sentiment
    else:
        return score/len(comment_words)


# main
if __name__ == '__main__':
    
    #pulsar_server = 'pulsar://35.188.130.50:6650'
    #pulsar_server = 'pulsar://localhost:6650'
    #pulsar_server = 'pulsar://pulsar-elb-1485389051.us-west-2.elb.amazonaws.com:6650'
    pulsar_server = 'pulsar://35.224.69.216:6650'
    
    # initialize the client, consumer, and topic
    consumer_topic = "topic"
    consumer_topic = "comments"
    producer_topic = "sentiment_comments"
    client = pulsar.Client(pulsar_server)
    consumer = client.subscribe(consumer_topic, 'comment_sub')

    # initialize the producer for after sentiment processing
    producer = PulsarProducer(pulsar_server, producer_topic)

    # creates a list of pos/neg words and their values from lexicon
    lexicon = open_lexicon()

    while True:
        result = consumer.receive()
        consumer.acknowledge(result)
        consume_data()
        
        record = consumer.receive()  # get comment record (in binary)
        consumer.acknowledge(record) # acknowledge receipt
        
        # testing/validation #
        print()
        print("Received message '{}' id='{}'".format(record.data(), record.message_id()))
        print()
        print(record.data().decode())
        print()
        # testing/validation #

        # check if the record/message is empty. if not, process. otherwise wait.
        if(record is not None):
            # decode the binary to json string
            json_text = record.data().decode('utf8')
            
            # load the record into json object, removing special text characters
            json_record = json.loads(json_text.replace('\n', '').replace('\r', ''))
            
            # preprocess the comment to remove punctuation, lower case, etc.
            json_body = preprocess_comment(json_record['body'])
            
            # reassign the processed comment back to the json record
            json_record['body'] = json_body

            # call the sentiment function to find the score
            # pass the lexicon and comment
            # score is returned
            score = determine_sentiment(lexicon, json_record['body'])

            # store the comment data and sentiment
            # score in a new json object
            # remove the actual comment (reduce storage footprint)
            analyzed_record = {}
            analyzed_record = json_record
            del analyzed_record['body']
            analyzed_record['sentiment'] = score
            print (analyzed_record)

            # send data to pulsar topic
            # producer.send_data(json.dumps(analyzed_record).encode('utf-8'))
            
            # set record/message to null to prepare for next check
            record = None



############ ** = code used/modified from https://towardsdatascience.com/sentiment-analysis-with-python-part-1-5ce197074184
