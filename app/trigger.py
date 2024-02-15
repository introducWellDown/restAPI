import time
from DB import *


def update_DB(conn,frequency):
        while True:
            if conn:
                top_100_repositories = get_top_repositories(git_token)
                insert_repositories(conn,top_100_repositories)
            time.sleep(frequency)