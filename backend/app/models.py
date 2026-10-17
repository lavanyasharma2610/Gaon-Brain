from datetime import datetime

from sqlmodel import Field, SQLModel


class Village(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Farmer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    village_id: int
    name: str
    role: str = "farmer"

class Plot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    farmer_id: int
    area_acre: float
    crop: str
    sown_on: datetime | None = None
    health: float = 1.0
    expected_yield: float = 0.0
    feeder_id: int | None = None
    polygon: str = ""

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: str
    plot_id: int | None = None
    farmer_id: int | None = None
    mitra_id: int | None = None
    lat: float | None = None
    lon: float | None = None
    ts: datetime = Field(default_factory=datetime.utcnow)
    payload: str = "{}"
    raw_text: str | None = None

class Sale(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    farmer_id: int
    qty_kg: float
    rate: float
    ts: datetime = Field(default_factory=datetime.utcnow)

class Buyer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Lot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    crop: str
    week: int
    expected_qty: float

class Commitment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lot_id: int
    buyer_id: int
    qty: float

class TractorRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    farmer_id: int
    want_date: str
    prev_served_count: int = 0

class PowerLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    feeder_id: int
    hour: int
    on_days: int
    total_days: int

class WaterSlot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plot_id: int
    slot: str

class Plan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class PlanItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plan_id: int
    plot_id: int
    crop: str
    week: int

class Report(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: str
    payload: str = "{}"

class Claim(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    farmer_id: int
    event_type: str
    event_at: datetime
    policy_no: str | None = None
    status: str = "unknown"

class ClaimPhoto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    claim_id: int
    sha256: str
    lat: float | None = None
    lon: float | None = None
    ts: datetime = Field(default_factory=datetime.utcnow)

class Purchase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    farmer_id: int
    product: str
    mrp: float
    paid: float
    bill_received: bool = False

class Consent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    farmer_id: int
    code: str
    expires_at: datetime

class MitraAudit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mitra_id: int
    farmer_id: int
    action: str
    ts: datetime = Field(default_factory=datetime.utcnow)

class Upload(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sha256: str
    path: str
