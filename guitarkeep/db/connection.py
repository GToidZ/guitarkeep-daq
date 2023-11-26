from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from decouple import config

class DBConnection:
    
    _instance = None
    _dbConnectionUrl: str = str(config("DB_URL", default=""))
    _engine = None
    _session = None
    
    @classmethod
    def get(cls):
        if cls._instance == None:
            cls._engine = create_async_engine(cls._dbConnectionUrl, echo=True)
            cls._session = sessionmaker(cls._engine)
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    @asynccontextmanager
    async def session(self):
        async with self._session() as session:
            async with session.begin():
                try:
                    yield session
                finally:
                    await session.close()