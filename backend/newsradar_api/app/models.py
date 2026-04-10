from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(120))
    last_name = Column(String(120))
    organization = Column(String(180))
    password = Column(String(128))
    role_ids = Column(JSON, default=[])   # lista de IDs
    alerts = relationship("Alert", back_populates="user", cascade="all, delete")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    descriptors = Column(JSON, default=[])
    categories = Column(JSON, default=[])
    cron_expression = Column(String(120))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="alerts")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    source = Column(String(10), default="IPTC")

class InformationSource(Base):
    __tablename__ = "information_sources"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    url = Column(String(500))
    channels = relationship("RSSChannel", back_populates="source", cascade="all, delete")

class RSSChannel(Base):
    __tablename__ = "rss_channels"
    id = Column(Integer, primary_key=True)
    url = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    information_source_id = Column(Integer, ForeignKey("information_sources.id"))
    source = relationship("InformationSource", back_populates="channels")