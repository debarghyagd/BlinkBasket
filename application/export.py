from flask import send_file
import pandas as pd
# from models import *
from celery import Celery
# from flask import current_app as app


celery = Celery("worker", 
                backend='redis://localhost:9736/2', 
                broker="redis://localhost:9736/2",
                # broker_connection_retry_on_startup=True
                )


@celery.task
def exporting_task(csv_list):
    df = pd.DataFrame(csv_list)
    df.to_csv('../collection/export.csv', index=False)
    return True
