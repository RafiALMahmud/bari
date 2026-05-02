from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, JSON, Enum
from sqlalchemy.sql import func
import enum
from database import Base


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    house = "house"
    office = "office"
    room = "room"


class ListingType(str, enum.Enum):
    rent = "rent"
    sale = "sale"
    sublet = "sublet"


class RentalType(str, enum.Enum):
    monthly = "monthly"
    daily = "daily"
    hourly = "hourly"


class Furnishing(str, enum.Enum):
    furnished = "furnished"
    semi_furnished = "semi_furnished"
    unfurnished = "unfurnished"


class ListingStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    inactive = "inactive"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    property_type = Column(Enum(PropertyType), nullable=False)
    listing_type = Column(Enum(ListingType), nullable=False)
    rental_type = Column(Enum(RentalType), nullable=True)
    furnishing = Column(Enum(Furnishing), nullable=False)

    price = Column(Float, nullable=False)
    bedrooms = Column(Integer, nullable=False, default=1)
    bathrooms = Column(Integer, nullable=False, default=1)
    area_sqft = Column(Float, nullable=True)

    address = Column(String(300), nullable=False)
    area = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False, default="Dhaka")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    nearby_university = Column(String(200), nullable=True)
    university_distance_km = Column(Float, nullable=True)

    is_female_only = Column(Boolean, default=False, nullable=False)
    safety_score = Column(Float, nullable=True)

    amenities = Column(JSON, default=list)
    photos = Column(JSON, default=list)
    documents = Column(JSON, default=list)
    has_furniture_for_sale = Column(Boolean, default=False)

    owner_name = Column(String(100), nullable=False)
    owner_phone = Column(String(20), nullable=False)
    owner_email = Column(String(150), nullable=True)

    status = Column(Enum(ListingStatus), default=ListingStatus.active, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
