from sqlmodel import SQLModel, Field, Table, Column, String, Integer, Text
from typing import Optional
from datetime import datetime
from sqlalchemy import MetaData, Table as SA_Table

# Using simple Table definitions to allow quick inserts in demo
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
from sqlalchemy import Table, Text, DateTime
from sqlalchemy import Integer

metadata = SQLModel.metadata

DeviceUser = SA_Table(
    'device_user', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', String, unique=True),
    Column('device_id', String, unique=True),
    Column('display_name', String),
    Column('created_at', String)
)

ChatMessage = SA_Table(
    'chat_message', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sender', String),
    Column('receiver', String),
    Column('message', Text),
    Column('timestamp', String)
)
