# Create table and insert some data
from views import db
from models import Task
from datetime import date


try:
    db.create_all()
    db.session.add(Task('Finish this tutorial', due_date=date(2016, 9, 22), priority=10, status=1))
    db.session.add(Task('Finish Real Python', due_date=date(2016, 10, 13), priority=10, status=1))

    db.session.commit()

except Exception as e:
    print(e)
