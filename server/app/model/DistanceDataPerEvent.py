from sqlalchemy import Column, DateTime, Integer, Numeric
from . import db


class DistanceDataPerEvent(db.Model):
    __tablename__ = 'd_distancedataperevent'
    __table_args__ = {'extend_existing': True}

    d_min = Column(Numeric)
    d_avg = Column(Numeric)
    d_numberofpeople = Column(Integer)
    d_e_event = Column(Integer, primary_key=True)
    d_datetime = Column(DateTime, primary_key=True)
    d_maskedpeople = Column(Numeric)

    def __init__(
            self,
            d_min=None,
            d_avg=None,
            d_numberofpeople=None,
            d_e_event=None,
            d_datetime=None,
            d_maskedpeople=None):
        self.d_min = d_min
        self.d_avg = d_avg
        self.d_numberofpeople = d_numberofpeople
        self.d_e_event = d_e_event
        self.d_datetime = d_datetime
        self.d_maskedpeople = d_maskedpeople

    def __repr__(self):
        return '<DistanceData %r>' % (self.d_avg)

    @property
    def serialize(self):
        return {
            'd_min': self.d_min,
            'd_avg': self.d_avg,
            'd_numberofpeople': self.d_numberofpeople,
            'd_e_event': self.d_e_event,
            'd_datetime': self.d_datetime,
            'd_maskedpeople': float(self.d_maskedpeople if self.d_maskedpeople else 0)
        }
