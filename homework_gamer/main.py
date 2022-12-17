import os
import time
from datetime import datetime, timedelta


next_exec_time = datetime.now().hour
while True:
    if datetime.now().hour == next_exec_time:
        os.system('echo start')
        next_exec_time = (datetime.now() + timedelta(hours=1)).hour
        os.system("scrapy crawl forum_gamer -a forum_id=23805 -a forum_title=神魔之塔 -a total_pages=0")
        os.system('echo finish')
    else:
        time.sleep(600)
