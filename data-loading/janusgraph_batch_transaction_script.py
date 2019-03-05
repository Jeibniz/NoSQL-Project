from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver import client
import json
import sys
import time

# Configuratios
JANUS_CONNECT = 'ws://35.238.47.90:8182/gremlin'
FILENAME = 'dataToDaniel_largeBatch_p1.json'    
EXECUTE = True

def import_json_file(filename: str):
    '''
    Imports the json file. Ignores dropped lines
    '''
    json_lists = []
    with open(filename) as f:
        for line in f:
            if line  != 'DROPPED\n':
                json_lists.append(json.loads(line))

    return json_lists

def define_schema():
    '''
    TODO: Refine this to create a modular schema function
    '''
    return f'''
    mgmt = graph.openManagement()
    comments = mgmt.makeEdgeLabel('comments').multiplicity(ONE2MANY).make()
    contains = mgmt.makeEdgeLabel('contains').multiplicity(ONE2MANY).make()

    comment = mgmt.makeVertexLabel('comment').make()
    subreddit = mgmt.makeVertexLabel('subreddit').make()
    user = mgmt.makeVertexLabel('user').make()
    sentiment = mgmt.makeVertexLabel('sentiment').make()
    mgmt.commit()
    '''

def create_indexes():
    return f"""
    graph.tx().rollback()
    mgmt = graph.openManagement()
    name = mgmt.getPropertyKey(')
    """

def check_existence_query(
    value: str,
    node_type: str,
    gremlin_client: client.Client,
    ):
    '''
    Helper function to check if node exists
    '''
    node_type_ids = {
        'subreddit': 'subreddit_id',
        'comment': 'id',
        'user': 'author'
    }

    existence_query = f"g.V().hasLabel('{node_type}').has('{node_type_ids[node_type]}', '{value}').hasNext()"

    return gremlin_client.submit(existence_query).all().result()[0]

def construct_gremlin_query(
    property_keys: list,
    json_values: dict,
    node_type: str
    ):
    '''
    Helper function to construct query to write to gremlin.
    '''
    gremlin_query = f"g.addV('{node_type}')"
    for prop in property_keys:
        if (prop in json_values.keys()) and (json_values[prop] is not None):
            if isinstance(json_values[prop], str):
                j_str = json_values[prop].replace("\\", "\\\\")
                j_str = j_str.replace("'", "\\'")
                gremlin_query += f".property('{prop}', '{j_str}')"
            elif json_values[prop] is False:
                gremlin_query += f".property('{prop}', false)"
            elif json_values[prop] is True:
                gremlin_query += f".property('{prop}', true)"
            else:
                gremlin_query += f".property('{prop}', {json_values[prop]})"
    gremlin_query += ".iterate()"

    return gremlin_query


def process_subreddit_node(
    property_keys: list,
    json_values: dict,
    gremlin_client: client.Client,
    execute=False,
    ):
    '''
    Constructs a gremlin query to create subreddit node (if it doesn't already exists)
    '''
    gremlin_query = construct_gremlin_query(property_keys, json_values, 'subreddit')

    if not check_existence_query(json_values['subreddit_id'], 'subreddit', gremlin_client) and execute:
        gremlin_client.submit(gremlin_query).all().result()
        gremlin_client.submit('g.tx().commit()').all().result()
        return gremlin_query  
    else:
        return f"Subreddit node w/ name {json_values['subreddit_id']} already exists"
 
    # try:
    #     print("test")
    # except:
    #     print('JSON must include "subreddit_id" as a unique identifier for the subreddit node')
    #     return ''

def process_comment_node(
    property_keys: list,
    json_values: dict,
    gremlin_client: client.Client,
    execute=False
    ):
    '''
    Constructs a gremlin query to create subreddit node (if it doesn't already exists)

    Executes if flag is set to True
    '''
    gremlin_query = construct_gremlin_query(property_keys, json_values, 'comment')

    if not check_existence_query(json_values['id'], 'comment', gremlin_client) and execute:
        gremlin_client.submit(gremlin_query).all().result()
        gremlin_client.submit('g.tx().commit()').all().result()
        return gremlin_query  
    else:
        return f"Comment node w/ unique id {json_values['id']} already exists"
 
    # try:
    #     print("test")
    # except:
    #     print('JSON must include "id" as a unique identifier for the comment node')
    #     return ''


def process_user_node(
    property_keys: list,
    json_values: dict,
    gremlin_client: client.Client,
    execute=False
    ):
    '''
    Constructs a gremlin query to create subreddit node (if it doesn't already exists)
    Executes if flag is set to True.
    '''

    gremlin_query = construct_gremlin_query(property_keys, json_values, 'user')

    if not check_existence_query(json_values['author'], 'user', gremlin_client) and execute:
        gremlin_client.submit(gremlin_query).all().result()
        gremlin_client.submit('g.tx().commit()').all().result()
        return gremlin_query
    else:
        return f"User node w/ unique id {json_values['author']} already exists"
    
    # try:
    #     print("test")
    # except:
    #     print('JSON must include "author" as a unique identifier for the user node')
    #     return ''
        
def check_edge_existence(
    in_node,
    out_node,
    gremlin_client
    ):
    '''
    Helper function to check if the edge exists between two nodes.
    Assumes that the nodes exist
    '''
    
    query = f"g.V({in_node}).outE().where(otherV().is({out_node})).hasNext()"
    print(gremlin_client.submit(query).all().result()[0])
    return gremlin_client.submit(query).all().result()[0]


def find_node(
    unique_id: str,
    node_type: str,
    gremlin_client: client.Client
    ):
    '''
    Construct the query to find the node with the specified property. Assumes
    that the specified property is unique to that node type
    '''
    node_type_ids = {
        'subreddit': 'subreddit_id',
        'comment': 'id',
        'user': 'author'
    }

    query = f"g.V().hasLabel('{node_type}').has('{node_type_ids[node_type]}', '{unique_id}').next()"
    
    try:
        node = gremlin_client.submit(query).all().result()
        return query
    except:
        "Node doesn't exist! Cannot create edge"

        # Not sure if this is needed, but noticed that when Gremlin client throws an error
        # it will disconnect and hang..
        gremlin_client = client.Client(JANUS_CONNECT, 'g')
        return None


def create_user_comment_edge(
    user_id: str,
    comment_id:str,
    gremlin_client,
    execute=False
    ):
    '''
    Creates the 'comments' edge between a user and the comment.
    
    Also performs sanity checks to make sure both nodes exist and the edge doesn't already exists.
    '''

    user_node = find_node(user_id, 'user', gremlin_client)
    comment_node = find_node(comment_id, 'comment', gremlin_client)

    if (user_node is not None) and (comment_node is not None):
        query = f"{user_node}.addEdge('commented', {comment_node})"
        #print(check_edge_existence(user_node, comment_node, gremlin_client))
        if execute and not check_edge_existence(user_node, comment_node, gremlin_client):
            gremlin_client.submit(query).all().result()
            gremlin_client.submit('g.tx().commit()').all().result()
            return query
        else:
            return "Edge already exists"

    else:
        return "Can't create Edge, one or more nodes does not exist"


def create_comment_subreddit_edge(
    subreddit_id: str,
    comment_id:str,
    gremlin_client,
    execute=False
    ):
    '''
    Creates the 'contains' edge between a user and the comment.
    
    Also performs sanity checks to make sure both nodes exist and the edge doesn't already exists.
    '''

    subreddit_node = find_node(subreddit_id, 'subreddit', gremlin_client)
    comment_node = find_node(comment_id, 'comment', gremlin_client)
    if (subreddit_node is not None) and (comment_node is not None):
        query = f"{comment_node}.addEdge('part_of', {subreddit_node})"
        #print(check_edge_existence(subreddit_node, comment_node, gremlin_client))
        if execute and not check_edge_existence(comment_node, subreddit_node, gremlin_client):
            gremlin_client.submit(query).all().result()
            gremlin_client.submit('g.tx().commit()').all().result()
            return query
        else:
            return "Edge already exists"
        
    else:
        return "Can't create Edge, one or more nodes does not exist"


if __name__ == "__main__":
    filename = str(sys.argv[2]) if len(sys.argv) == 3 else FILENAME
    raw_json = import_json_file(filename)
    gremlin_client = client.Client(JANUS_CONNECT, 'g')

    # Take the keys from each dictionary and split them up. 
    user_props = [
        'author',
        'author_flair_css_class',
        'author_flair_text',
        'user_created_utc']

    subreddit_props = [
        'subreddit_id',
        'subreddit',
    ]

    comment_props = [
        'id',
        'score',
        'created_utc',
        'sentiment_score'
    ]

    # specify past offset
    offset = int(sys.argv[1]) if len(sys.argv) >= 2 else 0
    # graph = Graph()
    # g = graph.traversal().withRemote(DriverRemoteConnection(JANUS_CONNECT,'g'))

    for i in range(offset, len(raw_json)):
        json = raw_json[i]
        print('--------------')
        print('Iteration: ' + str(i))
        print('--------------')
        #time.sleep(1)
        print('Creating Nodes...')
        print('--------------')
        print(process_comment_node(comment_props, json, gremlin_client, EXECUTE))
        print(process_user_node(user_props, json, gremlin_client, EXECUTE))
        #time.sleep(1)
        print(process_subreddit_node(subreddit_props, json, gremlin_client, EXECUTE))
        time.sleep(.25)
        print("\n")
        print('Creating Edges...')
        print('--------------')
        
        print(create_user_comment_edge(json['author'], json['id'], gremlin_client, EXECUTE))
        
        print(create_comment_subreddit_edge(json['subreddit_id'], json['id'], gremlin_client, EXECUTE))
        time.sleep(.25)