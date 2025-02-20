from functools import partial
import os

import configparser
from pymongo import errors, TEXT

from store import MongoStore
from config import Config

from agaveflask.logs import get_logger
logger = get_logger(__name__)

# Mongo is used for accounting, permissions and logging data for its scalability.
mongo_user = None
mongo_password = None
try:
    mongo_user = Config.get('store', 'mongo_user')
except configparser.NoOptionError:
    pass

mongo_password = os.environ.get('mongo_password', None)
if not mongo_password:
    # check in the config file:
    try:
        mongo_password = Config.get('store', 'mongo_password')
    except configparser.NoOptionError:
        pass

mongo_config_store = partial(
    MongoStore, Config.get('store', 'mongo_host'),
    Config.getint('store', 'mongo_port'),
    user=mongo_user,
    password=mongo_password)

logs_store = mongo_config_store(db='1')
# create an expiry index for the log store if we want logs to expire
log_ex = Config.get('web', 'log_ex')
#logger.debug(f"{log_ex}")
try:
    logger.debug("40")
    log_ex = int(log_ex)
    logger.debug("42")
    if not log_ex == -1:
        logger.debug("44")
        try:
            logger.debug(f"{logs_store._db.index_information()}")
            logs_store._db.create_index("exp", expireAfterSeconds=log_ex)
            logger.debug(f"{logs_store._db.index_information()}")
        except errors.OperationFailure:
            logger.debug("49")
            # this will happen if the index already exists.
            pass
except (ValueError, configparser.NoOptionError):
    logger.debug("53")
    pass

permissions_store = mongo_config_store(db='2')
executions_store = mongo_config_store(db='3')
clients_store = mongo_config_store(db='4')
actors_store = mongo_config_store(db='5')
workers_store = mongo_config_store(db='6')
nonce_store = mongo_config_store(db='7')
alias_store = mongo_config_store(db='8')
pregen_clients = mongo_config_store(db='9')
abaco_metrics_store = mongo_config_store(db='10')
configs_store = mongo_config_store(db='11')
configs_permissions_store = mongo_config_store(db='12')

# Indexing
logs_store.create_index([('$**', TEXT)])
executions_store.create_index([('$**', TEXT)])
actors_store.create_index([('$**', TEXT)])
workers_store.create_index([('$**', TEXT)])