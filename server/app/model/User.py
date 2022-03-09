from sqlalchemy import Boolean, Column, Integer, String
from . import db


class User(db.Model):
    __tablename__ = 'u_users'
    __table_args__ = {'extend_existing': True}

    u_id = Column(Integer, primary_key=True, autoincrement=True)
    u_name = Column(String(50), unique=True)
    u_pwd = Column(String(120), unique=True)
    u_isadmin = Column(Boolean, default=False)

    def __init__(self, u_name=None, u_pwd=None, u_isadmin=None):
        self.u_name = u_name
        self.u_pwd = u_pwd
        self.u_isadmin = u_isadmin
        self.id = self.u_id

    def __repr__(self):
        return '<User %r>' % (self.u_name)

    @property
    def serialize(self):
        return {
            'u_id': self.u_id,
            'u_name': self.u_name,
            'u_isadmin': self.u_isadmin
        }
