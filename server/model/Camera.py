from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, JSON
from sqlalchemy.sql.sqltypes import Boolean
from . import db
#from sqlalchemy.dialects.postgresql import JSONB
import numpy as np
import json


class Camera(db.Model):
    __tablename__ = 'c_cameras'
    __table_args__ = {'extend_existing': True}

    c_id = Column(Integer, primary_key=True, autoincrement=True)
    c_link = Column(String(100))
    c_e_event = Column(Integer, ForeignKey('e_events.e_id'))
    c_homography = Column(JSON)
    c_maxdistance = Column(Numeric)
    c_pixelpermeter = Column(Numeric)
    c_public = Column(Boolean)
    c_downtime_start = Column(String(5))
    c_downtime_end = Column(String(5))

    def __init__(
            self,
            c_link=None,
            c_e_event=None,
            c_homography=None,
            c_maxdistance=None,
            c_pixelpermeter=None,
            c_public=None,
            c_downtime_start=None,
            c_downtime_end=None):
        self.c_link = c_link
        self.c_e_event = c_e_event
        self.c_homography = {'matrix': c_homography.tolist()}
        self.c_maxdistance = c_maxdistance
        self.c_pixelpermeter = c_pixelpermeter
        self.c_public = c_public
        self.c_downtime_end = c_downtime_end
        self.c_downtime_start = c_downtime_start

    def __repr__(self):
        return '<Camera %r>' % (self.c_link)

    @property
    def serialize(self):
        return {
            'c_id': self.c_id,
            'c_link': self.c_link,
            'c_e_event': self.c_e_event,
            'c_maxdistance': float(self.c_maxdistance),
            'c_pixelpermeter': float(self.c_pixelpermeter),
            'c_public': self.c_public,
            'c_downtime_start': self.c_downtime_start,
            'c_downtime_end': self.c_downtime_end
        }

    @property
    def data(self):
        return {
            'c_id': self.c_id,
            'c_link': self.c_link,
            'c_e_event': self.c_e_event,
            'c_homography': np.array(self.c_homography['matrix']),
            'c_maxdistance': self.c_maxdistance,
            'c_pixelpermeter': self.c_pixelpermeter,
            'c_public': self.c_public,
            'c_downtime_start': self.c_downtime_start,
            'c_downtime_end': self.c_downtime_end
        }
