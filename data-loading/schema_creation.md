# Schema Creation
This is run as a gremlin script in the console after login in to create our schema.  
```
mgmt = graph.openManagement()
comments = mgmt.makeEdgeLabel('comments').multiplicity(ONE2MANY).make()
contains = mgmt.makeEdgeLabel('contains').multiplicity(ONE2MANY).make()

comment = mgmt.makeVertexLabel('comment').make()
subreddit = mgmt.makeVertexLabel('subreddit').make()
user = mgmt.makeVertexLabel('user').make()

```


- [ ] This is the schema creation  for every property in our node.  This is how we can define the type that is saved in JanusGraph, as JanusGraph will default to strings. 
```
comment_id = mgmt.makePropertyKey('id').dataType(String.class).cardinality(Cardinality.SINGLE).make()
archived = mgmt.makePropertyKey('archived').dataType(Boolean.class).cardinality(Cardinality.SINGLE).make()
parent_id = mgmt.makePropertyKey('parent_id').dataType(String.class).cardinality(Cardinality.SINGLE).make()
score = mgmt.makePropertyKey('score').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
score_hidden = mgmt.makePropertyKey('score_hidden').dataType(Boolean.class).cardinality(Cardinality.SINGLE).make()
downs = mgmt.makePropertyKey('downs').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
sentiment_score = mgmt.makePropertyKey('sentiment_score').dataType(Float.class).cardinality(Cardinality.SINGLE).make()
created_utc = mgmt.makePropertyKey('created_utc').dataType(Long.class).cardinality(Cardinality.SINGLE).make()
ups = mgmt.makePropertyKey('ups').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
controversiality = mgmt.makePropertyKey('controversiality').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
gilded = mgmt.makePropertyKey('gilded').dataType(Integer.class).cardinality(Cardinality.SINGLE).make()
```

```
subreddit = mgmt.makePropertyKey('subreddit').dataType(String.class).cardinality(Cardinality.SINGLE).make()
subreddit_id = mgmt.makePropertyKey('subreddit_id').dataType(String.class).cardinality(Cardinality.SINGLE).make()

user_created_utc = mgmt.makePropertyKey('user_created_utc').dataType(Long.class).cardinality(Cardinality.SINGLE).make()
author_flair_text = mgmt.makePropertyKey('author_flair_text').dataType(String.class).cardinality(Cardinality.SINGLE).make()
author_flair_css_class = mgmt.makePropertyKey('author_flair_css_class').dataType(String.class).cardinality(Cardinality.SINGLE).make()
author = mgmt.makePropertyKey('author').dataType(String.class).cardinality(Cardinality.SINGLE).make()
mgmt.commit()
```

## Index Creation
JanusGraph supports two different kinds of indexing to speed up query processing: Graph Indexes and Vertex-Centric Indexes. Most graph queries start traversal from a list of vertices or edges that are identified by their properties. We did not utilize Vertex-Centric-Indexes but utilized the two types of Graph Indexes. 

### Setup to create Index
Creating an index requires that no other transactions exist. This is a script to shutdown instances in this graph.
```
# Close transactions for
size = graph.getOpenTransactions().size();
for(i=0;i<size;i++) {graph.getOpenTransactions().getAt(0).rollback()}

# close other mgmt instances
mgmt.getOpenInstances()
mgmt.forceCloseInstance('0a1c00091-janusgraph-7f9f5cff77-b7dst1')
```

### Composite Index

Composite Indexes retrieve vertices by one composition of (potentially) multiple keys.  An added benefit of composite indexes is that they can also be used to enforce property uniqueness in the graph. Because of these properties, we decided to create a separate index for each unique property key for our Vertex types. 
```
mgmt = graph.openManagement()
subreddit = mgmt.getVertexLabel('subreddit')
propkey = mgmt.getPropertyKey('subreddit_id');
name = mgmt.getPropertyKey('subreddit_id')
mgmt.buildIndex('bySubreddit_id', Vertex.class).addKey(name).indexOnly(subreddit).unique().buildCompositeIndex()
mgmt.commit()
mgmt.awaitGraphIndexStatus(graph, 'bySubreddit_id').call()
mgmt = graph.openManagement()
mgmt.updateIndex(mgmt.getGraphIndex("bySubreddit_id"), SchemaAction.REINDEX).get()
mgmt.commit()
```

### Mixed Index
Mixed indexes utilize our indexing backend, Elasticsearch, to perform more flexible  queries, such as fuzzy string matching and inequality constraints when querying for particular nodes in the graph.  This is useful if we wanted to search based on a group of subreddits or to group on comments that had positive or negative sentiments? 

```
mgmt = graph.openManagement()
subreddit = mgmt.getPropertyKey('subreddit')
mgmt.buildIndex('byScoreUtcSubSentiment', Vertex.class).addKey(subreddit).addKey(sentiment_score).addKey(score).addKey(created_utc).buildMixedIndex("search")
mgmt.commit()
mgmt.awaitGraphIndexStatus(graph, 'byScoreUtcSubSentiment').call()

mgmt = graph.openManagement()
mtgmt.updateIndex(mgmt.getGraphIndex("byScoreUtcSubSentiment"
```