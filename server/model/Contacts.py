from sqlalchemy import Column, Integer, Numeric, Boolean
from . import db
from sqlalchemy.dialects.postgresql import TIMESTAMP


class Contacts(db.Model):
    __tablename__ = 'co_contacts'
    __table_args__ = {'extend_existing': True}

    co_id = Column(Integer, primary_key=True, autoincrement=True)
    co_p_person1 = Column(Integer, unique=False)
    co_p_person2 = Column(Integer, unique=False)
    co_distance = Column(Numeric, unique=False)
    co_datetime = Column(TIMESTAMP, nullable=False)
    co_camera = Column(Integer, unique=False)
    co_p_person2_mask = Column(Boolean)
    co_p_person1_mask = Column(Boolean)

    def __init__(
            self,
            co_p_person1=None,
            co_p_person2=None,
            co_distance=None,
            co_datetime=None,
            co_camera=None,
            co_p_person2_mask=None,
            co_p_person1_mask=None):
        self.co_p_person1 = co_p_person1
        self.co_p_person2 = co_p_person2
        self.co_distance = co_distance
        self.co_datetime = co_datetime
        self.co_camera = co_camera
        self.co_p_person2_mask = co_p_person2_mask
        self.co_p_person1_mask = co_p_person1_mask

    def __repr__(self):
        return '<Contact %r>' % (self.co_distance)
