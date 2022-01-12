from sqlalchemy import Column, Integer, String
from . import db


class Event(db.Model):
    __tablename__ = 'e_events'
    __table_args__ = {'extend_existing': True}

    e_id = Column(Integer, primary_key=True, autoincrement=True)
    e_name = Column(String(50), unique=True)
    e_u_user = Column(Integer, unique=True)
    e_adress = Column(String(100), unique=True)

    def __init__(self, e_name=None, e_u_user=None, e_adress=None):
        self.e_name = e_name
        self.e_u_user = e_u_user
        self.e_adress = e_adress

    def __repr__(self):
        return '<Event %r>' % (self.e_name)

    @property
    def serialize(self):
        return{
            'e_id': self.e_id,
            'e_name': self.e_name,
            'e_u_user': self.e_u_user,
            'e_adress': self.e_adress
        }
