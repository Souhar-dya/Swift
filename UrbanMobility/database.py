from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

Base = declarative_base()

class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class DeliveryRequest(Base):
    __tablename__ = 'delivery_requests'
    
    id = Column(String(50), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    time_window_start = Column(DateTime, nullable=False)
    time_window_end = Column(DateTime, nullable=False)
    load_size = Column(Float, nullable=False)
    priority = Column(Integer, nullable=False)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    vehicle_id = Column(String(50), ForeignKey('vehicles.id'), nullable=True)

class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    id = Column(String(50), primary_key=True)
    capacity = Column(Float, nullable=False)
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    available_time = Column(DateTime, nullable=False)
    status = Column(String(20), default='available')
    deliveries = relationship('DeliveryRequest', backref='vehicle')

class TrafficData(Base):
    __tablename__ = 'traffic_data'
    
    id = Column(Integer, primary_key=True)
    start_latitude = Column(Float, nullable=False)
    start_longitude = Column(Float, nullable=False)
    end_latitude = Column(Float, nullable=False)
    end_longitude = Column(Float, nullable=False)
    traffic_factor = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class WeatherData(Base):
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weather_factor = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)