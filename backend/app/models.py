from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Village(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Farmer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    village_id: int
    name: str
    role: str = "farmer"

class Plot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    farmer_id: int
    area_acre: float
    crop: str
    sown_on: Optional[datetime] = None
    health: float = 1.0
    expected_yield: float = 0.0
    feeder_id: Optional[int] = None
    polygon: str = ""

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    plot_id: Optional[int] = None
    farmer_id: Optional[int] = None
    mitra_id: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    ts: datetime = Field(default_factory=datetime.utcnow)
    payload: str = "{}"
    raw_text: Optional[str] = None
EOF