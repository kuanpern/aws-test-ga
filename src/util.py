import os
import sys
import json
import hashlib
import base64
import datetime
from collections import OrderedDict

import boto3
from botocore.exceptions import ClientError

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

import logging
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def fetch_secret(secret_name, region_name="ap-southeast-1"):
    '''Fetch secret from AWS secret manager'''

    # Create a Secrets Manager client
    session = boto3.session.Session()
    logger.info('initiate a secret manager client')
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # sample code copied from aws secret manager ...

    logger.info('getting secret ...')
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return secret
    # end if
# end def

def ensure_deduplication(msg, engine, table_name='queue_msg_hash', queue_name=None, schema=None):
    '''Ensure the message has not been processed before

    Args:
        msg (dict): The message to test. Must be of dict type.
        engine (sqlalchemy engine): Sqlalchemy engine to the database.
        table_name (str): Table name in the database to record the event's hash
        queue_name (str): The name of queue the msg originates from. For book-keeping only.
        schema (int): Postgres schema

    Returns:
        bool: True if the message has not been processed before, otherwise False
    '''
    ans = None

    # make hash-key of the msg
    hashkey = hashlib.md5(repr(OrderedDict(msg)).encode('utf-8')).hexdigest()

    # connect to the database
    meta = MetaData(bind=engine, schema=schema)
    Base = automap_base(metadata=meta)
    Base.prepare(engine, reflect=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    # create the new row
    table = Base.classes[table_name]
    row = table(
        queue_name = queue_name, 
        timestamp  = datetime.datetime.now(), 
        hashkey    = hashkey
    ) # end row

    # insert into the table
    session.add(row)
    try:
        session.commit()
        session.close()
        ans = True
    except sqlalchemy.exc.IntegrityError as e:
        session.rollback()
        m = session.query(table).filter(
            table.hashkey == hashkey
        ).first()
        session.close()
        if m is None:
            raise e
        else:
            ans = False
        # end if
    except Exception as e:
        session.close()
        raise e
    # end try

    return ans
# end def

def get_db_engine(credential=None, env_var_name='DB_SECRET_NAME'):
    '''Build SQLAlchemy engine

    Args:
        credential (dict): Dictionaty contains the database credential. Must contain (username, password, host, port, dbClusterIdentifier) as keys.
        env_var_name (str): Environment variable name for the secret_name to fetch from AWS secret manager

    Returns:
        engine: SQLAlchemy engine
    '''

    # fetch database secret
    if credential is None:
        credential = json.loads(
            fetch_secret(secret_name=os.environ[env_var_name])
        ) # end fetch_secret
    # end if

    # build connection string
    logger.info('build connection string')
    _engine = credential.get('engine', '').lower()
    if _engine == 'postgres':
        protocol = 'postgresql'
    elif _engine == 'mysql':
        protocol = 'mysql'
    else:
        raise ValueError('engine not supported: %s' % ())
    # end if
    conn_str = '{protocol}://{username}:{password}@{host}:{port}/{database}'.format(
        protocol=protocol, **credential
    ) # end conn_str
    logger.info(conn_str)

    # connect to database
    engine = sqlalchemy.create_engine(conn_str)

    return engine
# end def