# Cory Koster

# this file is used to retrieve a the comment json object from a json file, process it using
# sentiment analysis, compile the comments and load them into a new json file, and pass this
# file downstream for enrichment

# steps:
# 1. receive data
# 2. clean/standardize data (remove punctuation, all lower case, remove numbers, spaces, etc.)
# 3. load sentiment lexicon
# 4. perform sentiment analysis
# 5. load score into json record with previous data from object and send to Julia for enrichment

#import pulsar
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
    
    # j holds the compiled list of processed json objects
    # analyzed record temporarily holds the currently processed record
    j = []
    analyzed_record = {}
    
    # creates a list of pos/neg words and their values from lexicon
    lexicon = open_lexicon()
    
    # open the local json file
    json_file = open("/Users/cory/Desktop/sentiment_analysis/dataToCory.json","r")
    
    # loop through the file, processing each record by extracting the comment body,
    # running it through the sentiment analysis, putting it back together without
    # the comment body, and holding it until ready to write to file
    for line in json_file:
        if(line != '\n' and line != '' and line != None):      # check for end of line, null values
            record = json.loads(line)
            json_body = preprocess_comment(record['body'])     # remove extra and special chars
            score = determine_sentiment(lexicon, json_body)    # calculate sentiment score
            analyzed_record = record
            del analyzed_record['body']
            analyzed_record['sentiment_score'] = score
            j.append(analyzed_record)
            #print(analyzed_record)


# write the json objects to a new json file for downstream enrichment
with open('/Users/cory/Desktop/sentiment_analysis/dataToJulia.json', 'w') as outfile:
    for i in j:
        json.dump(i, outfile)
        outfile.write('\n')





#12:40am

############ ** = code used/modified from https://towardsdatascience.com/sentiment-analysis-with-python-part-1-5ce197074184
