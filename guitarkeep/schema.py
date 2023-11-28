from .db import models
from .db.connection import DBConnection
from sqlalchemy import select, or_, func

from typing import Optional
from datetime import datetime
from enum import Enum
from decouple import config, Csv
import strawberry as sb

# Declaring Enums
RoomType = Enum('RoomType', {
    (
        ''.join((str(v)[0].lower(), str(v).title().replace(" ", "")[1:])),
        str(v)
    ) for v in config(
        "ROOM_TYPES", default="Kitchen, Living Room, Bedroom", cast=Csv()
    )
})

DataType = Enum('DataType', {
    (
        ''.join((str(v)[0].lower(), str(v).title().replace(" ", "")[1:])),
        str(v)
    ) for v in config(
        "DATA_TYPES", default="Humidity, Light, Temperature, Rainfall", cast=Csv()
    )
})

# Registering Enums
sb.enum(RoomType)
sb.enum(DataType)

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

    @sb.field
    def tip(self) -> Optional[str]:
        compare = {
            "humidity": [45, 55],
            "temperature": [18, 28],
            "light": [0, 100],
            "rainfall": [0, 0.5]
        }

        if self.data_type not in compare.keys():
            return "NA"
        
        # Additional check for room_type when it is 'outside'
        if self.room_type == 'outside':
            if self.data_type == 'rainfall' and self.value > compare['rainfall'][1]:
                    return "High rainfall, consider closing window"
            if self.data_type == 'temperature' and self.value > compare['temperature'][1]:
                    return "High temperature outside, consider lowering temperature inside your rooms"

        # Existing checks for humidity, temperature, light, and rainfall
        if self.value > compare[self.data_type][1]:
            return self.data_type + " should be lower"
        if self.value < compare[self.data_type][0]:
            return self.data_type + " should be higher"
        return self.data_type + " is in the right range"

@sb.type
class AveragedData:
    room_type: str
    data_type: str
    value: float
    
    @classmethod
    def from_sql(cls, row) -> "AveragedData":
        return cls(
            room_type=row.roomType,
            data_type=row.dataType,
            value=row.averaged
        )

    @sb.field
    def tip(self) -> Optional[str]:
        compare = {
            "humidity": [45, 55],
            "temperature": [18, 28],
            "light": [0, 100],
            "rainfall": [0, 0.5]
        }

        if self.data_type not in compare.keys():
            return "NA"

        # Additional check for room_type when it is 'outside'
        if self.room_type == 'outside':
            if self.data_type == 'rainfall' and self.value > compare['rainfall'][1]:
                return "High rainfall, consider closing window"
            if self.data_type == 'temperature' and self.value > compare['temperature'][1]:
                return "High temperature outside, consider lowering temperature inside your rooms"

        # Existing checks for humidity, temperature, light, and rainfall
        if self.value > compare[self.data_type][1]:
            return self.data_type + " should be lower"
        if self.value < compare[self.data_type][0]:
            return self.data_type + " should be higher"
        return self.data_type + " is in the right range"

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
        room_type: RoomType, 
        start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None
        ) -> list[DataEntry]:
        async with DBConnection.get().session() as s:
            sql = select(models.DataEntry).filter(
                or_(models.DataEntry.roomType == room_type.value, models.DataEntry.roomType == "Outside")
            ).order_by(models.DataEntry.ts)

            if start_time:
                sql = sql.filter(models.DataEntry.ts >= start_time)
            
            if end_time:
                sql = sql.filter(models.DataEntry.ts <= end_time)

            res = (await s.execute(sql)).scalars().all()
        return [DataEntry.from_sql(entry) for entry in res]
    
    @sb.field
    async def data_entries_by_data_type(
        self, 
        data_type: DataType, 
        start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None
        ) -> list[DataEntry]:
        async with DBConnection.get().session() as s:
            sql = select(models.DataEntry).filter(models.DataEntry.dataType == str(data_type)).order_by(models.DataEntry.ts)

            if start_time:
                sql = sql.filter(models.DataEntry.ts >= start_time)
            
            if end_time:
                sql = sql.filter(models.DataEntry.ts <= end_time)

            res = (await s.execute(sql)).scalars().all()
        return [DataEntry.from_sql(entry) for entry in res]
    
    @sb.field
    async def avg_room_data(
        self,
        room_type: RoomType
    ) -> list[AveragedData]:
        async with DBConnection.get().session() as s:
            sql = select(
                    models.DataEntry.roomType,
                    models.DataEntry.dataType,
                    func.avg(models.DataEntry.value).label('averaged')
                ).filter(or_(models.DataEntry.roomType == room_type.value, models.DataEntry.roomType == "Outside")
                ).group_by(models.DataEntry.roomType, models.DataEntry.dataType)
            
            res = (await s.execute(sql)).all()
        return [AveragedData.from_sql(row) for row in res]

    @sb.field
    async def all_avg_data(self) -> list[AveragedData]:
        async with DBConnection.get().session() as s:
            sql = select(
                models.DataEntry.roomType,
                models.DataEntry.dataType,
                func.avg(models.DataEntry.value).label('averaged')
                ).group_by(models.DataEntry.roomType, models.DataEntry.dataType)
            res = (await s.execute(sql)).all()
        return [AveragedData.from_sql(row) for row in res]
    
schema = sb.Schema(query=Query)
