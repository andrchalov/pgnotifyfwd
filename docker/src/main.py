
import os
import os.path
import sys
import select
import psycopg2
from psycopg2 import sql
import json
import select
import logging
import requests
from utils.config import get_config

CONFIG_TEMPLATE = (
    ("PG_HOST", "localhost", False),
    ("PG_PORT", "5432", False),
    ("PG_DATABASE", "postgres", False),
    ("PG_USER", "pgnotifyfwd", False),
    ("PG_PASSWORD", "empty", False),
    ("PG_CHANNEL", "pgnotifyfwd", False),
    ("PUBURL", None, True),
    ("LOGLEVEL", "INFO", False)
)

logger = logging.getLogger("main")

config = get_config(CONFIG_TEMPLATE)
logging.basicConfig(stream=sys.stdout, level=config["LOGLEVEL"])

### FUNCTIONS ###

conn = psycopg2.connect(
    host=config["PG_HOST"],
    port=config["PG_PORT"],
    dbname=config["PG_DATABASE"],
    user=config["PG_USER"],
    password=config["PG_PASSWORD"]
)

conn.autocommit = True

curs = conn.cursor()

logging.debug("Start listening channel %s" % config["PG_CHANNEL"])
curs.execute(sql.SQL('LISTEN {};').format(sql.Identifier(config["PG_CHANNEL"])))

logging.debug("Waiting for notifications on channel %s" % config["PG_CHANNEL"])

while True:
    if select.select([conn],[],[],30) == ([],[],[]):
        logging.debug("Timeout")
    else:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            logging.debug("Got NOTIFY: %s %s %s", notify.pid, notify.channel, notify.payload)
            try:
                payload = json.loads(notify.payload)
                r = requests.post(config["PUBURL"]+('?id=%s' % payload["channel"]), data=payload["data"]+"\r\n")

                if r.status_code != 200:
                    logging.error("Notification not published, server returns status code: %s", r.status_code)
            except json.JSONDecodeError as e:
                logging.error('JSON decode error: %s' % e)
            except Exception as e:
                logging.error('Exception: %s' % e)
