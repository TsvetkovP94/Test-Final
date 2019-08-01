from pony.orm import *
from datetime import datetime

db = Database()


class Event(db.Entity):
    event = Required(str)
    repo = Required(str)
    branch = Required(str)
    time = Required(datetime, default=datetime.now)
