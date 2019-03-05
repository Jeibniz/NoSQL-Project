# Gremlin Queries for Data Analysis:

A terminal run locally on a computer is used to connect to the Gremlin console on Google Cloud Platform. This is how to connect the terminal and run queries.

## Gremlin queries
### 1. Install JanusGraph 0.2.0
1. Navigate to https://github.com/JanusGraph/janusgraph/releases/ and download 0.2.0
2. Unzip the JanusGraph zipped file
3. Navigate to where the folder extracted (i.e. janusgraph-0.2.0-hadoop2) and navigate to subfolder conf
4. Edit file "remote.yaml"
5. Replace [localhost] with 35.238.47.90, e.g. hosts: [35.238.47.90]
6. Enter 8182 for port number, e.g. port: 8182


### 2. Connect to console
1. Open local terminal
2. Navigate to janusgraph-0.2.0-hadoop2
3. Run Gremlin shell script ./bin/gremlin.sh
4. Now run these two commands from the shell
    a. :remote connect tinkerpop.server conf/remote.yaml session
    b. :remote console

-You are now ready to run Gremlin queries

### 3. Run Gremlin query
1. Run the test query --> gremlin> g.V()
    -if successful, this will list vertex id's


-the console can be glitchy at times and commands will no longer be accepted. If this happens, enter :quit into the console to exit the shell. To reconnect, follow steps above starting with #2. Connect to console
