from .db import models
from .db.connection import DBConnection
from sqlalchemy import select

from typing import Optional
from datetime import datetime
import strawberry as sb

@sb.type
class DataEntry:
    id: sb.ID
    ts: datetime
    room_type: str
    data_type: str
    value: float
    source: str

    @classmethod
    def from_sql(cls, model: models.DataEntry) -> "DataEntry":
        return cls(
            id=sb.ID(model.Id),
            ts=model.ts,
            room_type=model.roomType,
            data_type=model.dataType,
            value=model.value,
            source=model.source
        )


@sb.type
class Query:
    @sb.field
    async def data_entries(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        # Add additional filters here
        ) -> list[DataEntry]:

        async with DBConnection.get().session() as s:
            sql = select(models.DataEntry).order_by(models.DataEntry.ts)

            if start_time:
                sql = sql.filter(models.DataEntry.ts >= start_time)
            
            if end_time:
                sql = sql.filter(models.DataEntry.ts <= end_time)

            res = (await s.execute(sql)).scalars().all()
        return [DataEntry.from_sql(entry) for entry in res]
    
    @sb.field
    async def data_entries_by_room_type(
        self, 
        room_type: str, 
        start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None
        ) -> list[DataEntry]:
        async with DBConnection.get().session() as s:
            sql = select(models.DataEntry).filter(models.DataEntry.roomType == room_type).order_by(models.DataEntry.ts)

            if start_time:
                sql = sql.filter(models.DataEntry.ts >= start_time)
            
            if end_time:
                sql = sql.filter(models.DataEntry.ts <= end_time)

            res = (await s.execute(sql)).scalars().all()
        return [DataEntry.from_sql(entry) for entry in res]
    
    
schema = sb.Schema(query=Query)
