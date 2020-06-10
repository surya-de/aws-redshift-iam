# Redshift-IAM

Configurations to query redshift cluster using IAM access.

### Issue-
Lambda runtime environment does not have provisions for psycopg2 library which we will require to connect to redshift cluster.

### Solution-
To solve this problem this is what we need to do-
#### Step-1
Install psycopg2 using pip. To do this step we need to use a **linux OS** as lambda's execution environment uses Linux. 
```bash
pip3 install psycopg2 -t ./
```
#### Step-2
Create a deployment package for lambda and upload it to the lambda.
 1. Grant access to the entire package folder.
```bash
chmod -R 755 .
```
 2. Zip the entire folder.
```bash
zip -r ../myDeploymentPackage.zip .
```
 3. Upload the zip to your lambda function.

### Implementation-
To implement the connection using python we need to do the following steps-
#### Step-1
Get temporary credentials using the the **get_cluster_credentials** API from BOTO3
```python
  # Module to fetch temporary creds.
  def get_temporary_creds(self):
    connection_params = {}
    # Configuration to connect.
    RS_PORT = 5439
    RS_USER = ''
    DATABASE = ''
    CLUSTER_ID = ''
    RS_HOST = ''
    
    # Get temporary credentials.
    cluster_creds = client.get_cluster_credentials(DbUser = RS_USER,
                                                    DbName = DATABASE,
                                                    ClusterIdentifier = CLUSTER_ID,
                                                    DurationSeconds = 3600,
                                                    AutoCreate = True,
                                                    DbGroups = ['trial']
                                                    )

    # Create a dictionary with parameters reqd
    # for connection to redshit cluster.
    connection_params['endpoint'] = RS_HOST
    connection_params['db'] = DATABASE
    connection_params['port_no'] = RS_PORT
    connection_params['user'] = cluster_creds['DbUser']
    connection_params['pwd'] = cluster_creds['DbPassword']

    return connection_params
```
#### Step-2
Once we have got the temporary connection credentials we can try to connect to the redshift cluster using the credentials.
```python
  # Module to connect to redshift cluster.
  def connect_redshift(self, obj_store):
    try:
      print('##Connecting')
      conn = psycopg2.connect(
        host = obj_store['endpoint'],
        port = obj_store['port_no'],
        user = obj_store['user'],
        password = obj_store['pwd'],
        database = obj_store['db']
      )
      return conn

    except psycopg2.Error:
      logger.exception('Failed to open database connection.')
```
