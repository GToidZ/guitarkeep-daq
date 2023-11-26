from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from decouple import config

class DBConnection:
    
    _init = False
    _instance = None
    _dbConnectionUrl: str = str(config("DB_URL", default=""))
    _engine: Optional[AsyncEngine] = None
    _session = None

    @classmethod
    def is_initialized(cls):
        return cls._init

    @classmethod
    def get(cls):
        if cls._instance == None:
            cls._engine = create_async_engine(cls._dbConnectionUrl, echo=True)
            cls._session = sessionmaker(cls._engine, class_=AsyncSession)
            cls._instance = cls.__new__(cls)
            cls._init = True
        return cls._instance
    
    def engine(self):
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session() as session:
            async with session.begin():
                try:
                    yield session
                finally:
                    await session.close()