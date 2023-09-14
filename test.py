import sqlalchemy as db
from sqlalchemy import select, func, desc, or_

from db import Users

# from datetime import datetime
#
#
# engine = db.create_engine("sqlite:///data.db")
#
# con = engine.connect()
#
# metadata = db.MetaData()
#
# top = db.Table('top', metadata,
#                db.Column('user_id', db.Integer, primary_key=True),
#                db.Column('chat_id', db.Integer),
#                db.Column('username', db.String(250)),
#                db.Column('name', db.String(250)),
#                db.Column('length', db.Integer),
#                db.Column('date', db.String(250)),
#                db.Column('grows', db.Integer),
#                db.Column('attack', db.Integer),
#                db.Column('defence', db.Integer),
#                db.Column('try_', db.Integer),
#                db.Column('force', db.Integer)
#                )
#
# metadata.create_all(engine)
#
#
# insert_query = top.insert().values(user_id='123', chat_id = '235', username='жопа', name='polnaya', length=-5, date='12.06.2003', grows=1, attack=3, defence=3, try_=2, force=10)
# con.execute(insert_query)
# print(insert_query)
# select_query = db.select(top)
# selection = con.execute(select_query)
# print(selection.fetchall())
#
# con.commit()

# chat_id = 945469
# stmt1 = select(Users.id, Users.name, Users.length).where(Users.chat_id == user.chat_id).subquery()
#
# stmt2 = select(stmt1.c.user_id, stmt1.c.name, stmt1.c.length, func.row_number().over(order_by=desc(stmt1.c.length)).label('row_number')).subquery()
# stmt = select(stmt2.c.user_id, stmt2.c.name, stmt2.c.length, stmt2.c.row_number).where(or_(stmt2.c.row_number <= 10, stmt2.c.user_id == user.user_id))
#
# stmt1 = select(Users).count(0)

# stmt = select(Users.chat_id).distinct()
# print(stmt)
