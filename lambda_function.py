import json
import boto3
import logging
import psycopg2

def lambda_handler(event, context):
  # Json format to take user input.
  user_request = {
    'OPER_TYPE' : 'create', # CREATE/ GRANT
    'OPER_FOR' : 'user',
    'US_NAME' : 'suryatrial1',
    'GR_NAME' : 'trial',
    'GR_USERS' : ['surya'],
    'PASSWORD' : "",
    'OPTIONS' : {
      'DB_OPTN' : 'NOCREATEDB',       # CREATEDB/ NOCREATEDB
      'USER_OPTN' : '',
      'PASSWORD' : '',      # FOR ALTER QUERY
      'LOG_OPTN' : '',
      'GROUP' : [],
      'VALIDITY' : '',
      'NEW_NAME' : '',
      'CONN_LIMT' : ''
    }
  }
  obj_r_handler = RedshiftHandler()
  qy = obj_r_handler.create_query(user_request)
  store = obj_r_handler.get_temporary_creds()
  con_obj = obj_r_handler.connect_redshift(store)
  obj_r_handler.execute_query(con_obj, qy)

class RedshiftHandler:
  global client
  client = boto3.client('redshift',  region_name = 'us-west-2')

  # Module to create query for RS.
  def create_query(self, obj_input):
    interim_qry = ''
    # Create query for CREATE operation.
    if obj_input['OPER_TYPE'] == 'create':
      # Form query to create user.
      if obj_input['OPER_FOR'] == 'user':
        interim_qry = 'CREATE USER ' +  obj_input['US_NAME']
        # Check for password provided
        # by the user.
        if obj_input['PASSWORD'] != '':
          interim_qry = interim_qry + ' WITH PASSWORD ' + obj_input['PASSWORD'] + ' ;'
        return interim_qry
      
      # Form query to create group.
      elif obj_input['OPER_FOR'] == 'group':
        # Check for users to add to
        # a given group.
        interim_qry = 'CREATE GROUP ' +  obj_input['GR_NAME']
        if len(obj_input['GR_USERS']) != 0:
          urs_lsts = ''
          for usrs in obj_input['GR_USERS']:
            urs_lsts += ' '
            urs_lsts += usrs
          interim_qry = interim_qry + ' WITH USER' + urs_lsts
        return interim_qry

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
  
  # Module to execure query on the RS
  # database.
  def execute_query(self, con_obj, query):
    print(query)
    try:
      cur = con_obj.cursor()
      cur.execute(query)
      con_obj.commit()
      print(cur)
      print(cur.fetchall())
      # Close the connections.
      cur.close()
      con_obj.close()
    except psycopg2.Error as e:
      print(e)

# The driver code.
if __name__ == '__main__':
  lambda_handler('hello', 'moto')
