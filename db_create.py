# Create table and insert some data
from project import db
from project.models import Task, User
from datetime import date


# try:
db.create_all()
# Fill db with sample data
db.session.add(User("admin", "ad@min.com", "admin", "admin"))
db.session.add(Task(
    name="Finish this tutorial",
    due_date=date(2015, 3, 13),
    priority=10,
    posted_date=date(2015, 2, 13),
    user_id=1,
    status=1))
db.session.add(Task(
    name="Finish Real Python",
    due_date=date(2015, 3, 13),
    priority=10,
    posted_date=date(2015, 2, 13),
    user_id=1,
    status=1))
db.session.commit()

# except Exception as e:
#     print(e)
