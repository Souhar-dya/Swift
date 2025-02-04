from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from database import DeliveryRequest, Vehicle, TrafficData, WeatherData
from delivery_optimizer import DeliveryOptimizer
from database import DeliveryStatus


class OptimizationService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.optimizer = DeliveryOptimizer()
    
    def get_pending_deliveries(self) -> List[DeliveryRequest]:
        return (self.db_session.query(DeliveryRequest)
                .filter(DeliveryRequest.status == DeliveryStatus.PENDING)
                .all())
    
    def get_available_vehicles(self) -> List[Vehicle]:
        return (self.db_session.query(Vehicle)
                .filter(Vehicle.status == 'available')
                .all())
    
    def get_traffic_data(self) -> Dict[Tuple[float, float], float]:
        recent_traffic = (self.db_session.query(TrafficData)
                         .filter(TrafficData.timestamp >= datetime.now() - timedelta(minutes=15))
                         .all())
        
        return {(td.start_latitude, td.start_longitude): td.traffic_factor 
                for td in recent_traffic}
    
    def optimize_routes(self):
        # Get all required data
        deliveries = self.get_pending_deliveries()
        vehicles = self.get_available_vehicles()
        traffic_data = self.get_traffic_data()
        weather_data = self.get_weather_data()
        
        # Update optimizer with current data
        self.optimizer.update_real_time_data(traffic_data, weather_data, [])
        self.optimizer.vehicles = vehicles
        self.optimizer.requests = deliveries
        
        # Run optimization
        optimized_routes = self.optimizer.optimize_routes()
        
        # Update database with results
        self.update_routes_in_db(optimized_routes)
        
        return optimized_routes
    
    def update_routes_in_db(self, routes: Dict[str, List[DeliveryRequest]]):
        for vehicle_id, deliveries in routes.items():
            # Update vehicle assignments
            for delivery in deliveries:
                db_delivery = (self.db_session.query(DeliveryRequest)
                             .filter(DeliveryRequest.id == delivery.id)
                             .first())
                db_delivery.vehicle_id = vehicle_id
                db_delivery.status = DeliveryStatus.ASSIGNED
        
        self.db_session.commit()