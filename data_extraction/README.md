# Data extraction

This package will extracts data from the dataset fh-bigquery.reddit_comments.2015_05 that is stored in Googles BigQuery. The data can ether be sent to a pulsar topic or extracted into an JSON file.


### Getting Started

Examples on how to use the package can be found in the extract_to_file_app.py and extract_to_pulsar_app.py files. For BigQuery to work right away a key JSON file to Google Cloud Platform need to be added to this directory with the name key.json since that is what the files above uses. If you wish to store the file elsewhere just specify the path to the file in the BigQueryClient contructor.

### Prerequisites

To be able to use this packade two things are needed:

* A Google Cloud Platform JSON key
* A Running Pulsar instance

The key can be generated from https://console.cloud.google.com/apis/credentials/serviceaccountkey. 

The easiest way to run pulsar is to run it in standalone mode. Here is a guide on how to do it https://pulsar.apache.org/docs/en/standalone/.



### Authors

* **Jonathan Persgården**

See also the list of [contributors](https://github.umn.edu/garbu007/5980-noSQL-phase2/graphs/contributors) who participated in this project.

