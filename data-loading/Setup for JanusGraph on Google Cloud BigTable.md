# Setup for JanusGraph on Google Cloud BigTable

This setup is largely based on https://cloud.google.com/solutions/running-janusgraph-with-bigtable with a few modifications.

## GCP setup
Create a new GCP Project and enable billing on that project
Enable the Cloud Bigtable, Cloud Bigtable Admin, Compute Engine, and GKE APIs.
 [ENABLE THE APIS](https://console.cloud.google.com/flows/enableapi?apiid=bigtable,bigtableadmin.googleapis.com,compute.googleapis.com,container.googleapis.com) 



## Creating a Cloud Bigtable Instance
For JanusGraph backend, the tutorial used Cloud Bigtable. For this tutorial, we deployed a single-node development cluster, which is hopefully sufficient for this project. 

![](Setup%20for%20JanusGraph%20on%20Google%20Cloud%20BigTable/D8250AA7-FCBC-454F-BB51-E448D2126FDA.png)

## Configuring Cluster Access for kubectl
https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl

make sure the cloud SDK is installed (quickstart for macOS [Quickstart for macOS  |  Cloud SDK Documentation       |  Google Cloud](https://cloud.google.com/sdk/docs/quickstart-macos)

```
glcoud config set project [PROJECT_ID]
gcloud config set compute/zone us-central1-f
gcloud config set compute/region [COMPUTE_REGION]
gcloud components update
```

```
gcloud container clusters create janusgraph-tutorial --machine-type n1-standard-4 \
    --scopes "https://www.googleapis.com/auth/bigtable.admin","https://www.googleapis.com/auth/bigtable.data" --num-nodes 2
```

The current context after creating using GCP should be updated. Run `kubectl config current-context` to double check


## Helm 
Helm is a Kubernetes application manager, and helps install and manage complexity of some of the deployment for Janusgraph.. Helm “Charts” are application definitions for Helm that allows us to configure Janusgraph deployment. 

On MacOS
`brew install kubernetes-helm`

Or through curl
`curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash`

```
kubectl create serviceaccount tiller --namespace kube-system
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin \
    --serviceaccount=kube-system:tiller
helm init --service-account=tiller
```

## Using Helm to install JanusGraph and Elasticsearch
JanusGraph uses Elasticsearch as the indexing backend.  When the chart is deployed, Elasticsearch will also be included as a dependency.
1. Setup an environment variable to hold the value of Cloud Bigtable instance ID that you noted earlier

`export INSTANCE_ID=janusgraph`

```
cat > values.yaml << EOF
replicaCount: 3
service:
  type: LoadBalancer
elasticsearch:
  deploy: true
properties:
  storage.backend: hbase
  storage.directory: null
  storage.hbase.ext.google.bigtable.instance.id: $INSTANCE_ID
  storage.hbase.ext.google.bigtable.project.id: $GOOGLE_CLOUD_PROJECT
  storage.hbase.ext.hbase.client.connection.impl: com.google.cloud.bigtable.hbase1_x.BigtableConnection
  index.search.backend: elasticsearch
  index.search.directory: null
  cache.db-cache: true
  cache.db-cache-clean-wait: 20
  cache.db-cache-time: 180000
  cache.db-cache-size: 0.5
persistence:
  enabled: false
EOF
```

`helm install —wait —timeout 600 —name janusgraph stable/janusgraph -f values.yaml`


## Verify JanusGraph Deployment

Follow the `NOTES` section after the helm install command finishes

```
  To connect to JanusGraph using gremlin.sh from outside of your Kubernetes cluster:
  Determine your loadbalancer's IP:
  export SERVICE_IP=$(kubectl get svc --namespace default janusgraph -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
        You can watch the status of by running 'kubectl get svc -w janusgraph'

  Locate 'remote.yaml' in your local gremlin installation.
  Replace 'localhost' in remote.yaml with $SERVICE_IP:
  sed -i "s/localhost/$SERVICE_IP/" remote.yaml

  Run gremlin.sh and connect to the JanusGraph service running in your kubernetes cluster.

  Once you are situated at the gremlin console, connect to the tinkerpop server:
  gremlin> :remote connect tinkerpop.server conf/remote.yaml session
  gremlin> :remote console

  At this point, you can issue gremlin queries:
  gremlin> v1 = graph.addVertex( label, "hello")
  gremlin> v2 = graph.addVertex( label, "world")
  gremlin> v1.addEdge("followedBy", v2)
  gremlin> g.V().has(label,'hello').out('followedBy').label()

  You should expect to see:
  ==>world
```

Note you have to match the `gremlin.sh` bash script with the correct version that has the plugins already configured for JanusGraph 0.2.0. Easiest way I found is to install the Janusgraph 0.20. zip (https://github.com/JanusGraph/janusgraph/releases/download/v0.2.0/janusgraph-0.2.0-hadoop2.zip)

Should be able to issue gremlin queries. Will upload a python script 