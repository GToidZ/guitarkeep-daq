from sqlalchemy import Column
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TIMESTAMP, String, Integer, Float

Base = declarative_base()

class DataEntry(Base):
    __tablename__ = "datawarehouse"
    Id: int = Column(Integer, primary_key=True, index=True)
    ts: TIMESTAMP = Column(TIMESTAMP, index=True)
    roomType: str = Column(String)
    dataType: str = Column(String)
    value: float = Column(Float)
    source: str = Column(String)
