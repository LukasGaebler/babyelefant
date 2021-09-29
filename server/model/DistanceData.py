from sqlalchemy import Column, DateTime, Integer, Numeric, Boolean
from . import db


class DistanceData(db.Model):
    __tablename__ = 'd_distancedata'
    __table_args__ = {'extend_existing': True}

    d_min = Column(Numeric)
    d_avg = Column(Numeric)
    d_numberofpeople = Column(Integer)
    d_c_id = Column(Integer, primary_key=True)
    d_datetime = Column(DateTime, primary_key=True)
    d_maskedpeople = Column(Numeric)

    def __init__(
            self,
            d_min=None,
            d_avg=None,
            d_numberofpeople=None,
            d_c_id=None,
            d_datetime=None,
            d_maskedpeople=None):
        self.d_min = d_min
        self.d_avg = d_avg
        self.d_numberofpeople = d_numberofpeople
        self.d_c_id = d_c_id
        self.d_datetime = d_datetime
        self.d_maskedpeople = d_maskedpeople

    def __repr__(self):
        return '<DistanceData %r>' % (self.d_avg)

    @property
    def serialize(self):
        return {
            'd_min': float(self.d_min),
            'd_avg': float(self.d_avg),
            'd_numberofpeople': self.d_numberofpeople,
            'd_c_id': self.d_c_id,
            'd_datetime': self.d_datetime,
            'd_maskedpeople': float(self.d_maskedpeople if self.d_maskedpeople else 0)
        }
