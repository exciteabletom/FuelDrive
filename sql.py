"""
SQL ORM setup
"""

import sqlalchemy as db
from sqlalchemy import Column, String, Numeric, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

engine = db.create_engine("sqlite:///prices.sqlite", future=True)
metadata = db.MetaData(bind=engine)
Base = declarative_base(metadata=metadata)
Session = sessionmaker(engine)


class Station(Base):
    __tablename__ = "station"
    latitude = Column(
        "latitude", Numeric(asdecimal=False), nullable=False, primary_key=True
    )
    longitude = Column(
        "longitude", Numeric(asdecimal=False), nullable=False, primary_key=True
    )
    name = Column("name", String(), nullable=False)
    brand = Column("brand", String(), nullable=False)
    description = Column("description", String())
    suburb = Column("suburb", String(), nullable=False)
    address = Column("address", String(), nullable=False)
    last_update = Column("last_update", Integer(), nullable=False)
    unleaded_91 = Column("unleaded_91", Numeric(asdecimal=False))
    unleaded_95 = Column("unleaded_95", Numeric(asdecimal=False))
    unleaded_98 = Column("unleaded_98", Numeric(asdecimal=False))
    diesel = Column("diesel", Numeric(asdecimal=False))
    premium_diesel = Column("premium_diesel", Numeric(asdecimal=False))
    lpg = Column("lpg", Numeric(asdecimal=False))
    e85 = Column("e85", Numeric(asdecimal=False))

    def __repr__(self):
        return f"Station {self.name} at {self.address}"


fuel_types = {
    "unleaded_91": Station.unleaded_91,
    "unleaded_95": Station.unleaded_95,
    "unleaded_98": Station.unleaded_98,
    "diesel": Station.diesel,
    "premium_diesel": Station.premium_diesel,
    "lpg": Station.lpg,
    "e85": Station.e85,
}
