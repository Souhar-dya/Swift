import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
import heapq

@dataclass
class DeliveryRequest:
    id: str
    location: Tuple[float, float]
    time_window: Tuple[datetime, datetime]
    load_size: float
    priority: int

@dataclass
class Vehicle:
    id: str
    capacity: float
    current_location: Tuple[float, float]
    available_time: datetime

class DeliveryOptimizer:
    def __init__(self):
        self.traffic_data: Dict[Tuple[float, float], float] = {}  # (location1, location2) -> traffic_factor
        self.weather_data: Dict[Tuple[float, float], float] = {}  # location -> weather_factor
        self.road_closures: List[Tuple[float, float]] = []  # List of closed road segments
        self.vehicles: List[Vehicle] = []
        self.requests: List[DeliveryRequest] = []

    def update_real_time_data(self, traffic_data: Dict, weather_data: Dict, road_closures: List):
        """Update real-time conditions."""
        self.traffic_data = traffic_data
        self.weather_data = weather_data
        self.road_closures = road_closures

    def _calculate_base_time(self, start: Tuple[float, float], end: Tuple[float, float]) -> float:
        """Calculate base travel time using the Haversine formula."""
        R = 6371  # Earth radius in km
        AVERAGE_SPEED = 40  # Average vehicle speed in km/h

        lat1, lon1 = start
        lat2, lon2 = end

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        base_time = (distance / AVERAGE_SPEED) * 60  # Convert hours to minutes
        return base_time

    def calculate_travel_time(self, start: Tuple[float, float], end: Tuple[float, float], current_time: datetime) -> float:
        """Calculate travel time considering traffic, weather, and road closures."""
        base_time = self._calculate_base_time(start, end)

        traffic_factor = self.traffic_data.get((start, end), 1.0)
        weather_factor = max(self.weather_data.get(start, 1.0), self.weather_data.get(end, 1.0))

        if (start, end) in self.road_closures:
            return float('inf')

        return base_time * traffic_factor * weather_factor

    def optimize_routes(self) -> Dict[str, List[DeliveryRequest]]:
        """Optimize delivery routes using Adaptive Large Neighborhood Search (ALNS) with Simulated Annealing."""
        current_solution = self._generate_initial_solution()
        best_solution = current_solution.copy()
        best_cost = self._evaluate_solution(best_solution)

        temperature = 100
        cooling_rate = 0.95
        iterations = 1000

        for i in range(iterations):
            removed_requests = self._remove_random_requests(current_solution)
            new_solution = self._reinsert_requests(current_solution, removed_requests)

            new_cost = self._evaluate_solution(new_solution)

            if new_cost < best_cost or np.random.random() < np.exp((best_cost - new_cost) / temperature):
                current_solution = new_solution
                if new_cost < best_cost:
                    best_solution = new_solution
                    best_cost = new_cost

            temperature *= cooling_rate

            if i % 10 == 0:
                self._check_and_update_real_time_conditions()

        return best_solution

    def _evaluate_solution(self, solution: Dict[str, List[DeliveryRequest]]) -> float:
        """Evaluate solution cost considering constraints like time window and capacity."""
        total_cost = 0

        for vehicle_id, route in solution.items():
            vehicle = next(v for v in self.vehicles if v.id == vehicle_id)
            current_time = vehicle.available_time
            current_location = vehicle.current_location
            current_load = 0

            for delivery in route:
                travel_time = self.calculate_travel_time(current_location, delivery.location, current_time)
                current_time += timedelta(minutes=travel_time)

                if current_time < delivery.time_window[0]:
                    current_time = delivery.time_window[0]
                elif current_time > delivery.time_window[1]:
                    total_cost += 1000  # Penalty for time window violation

                current_load += delivery.load_size
                if current_load > vehicle.capacity:
                    total_cost += 500  # Penalty for overloading

                total_cost += travel_time * (1 + (5 - delivery.priority) * 0.2)
                current_location = delivery.location

        return total_cost

    def _check_and_update_real_time_conditions(self):
        """Fetch and update real-time data (placeholder for real API integration)."""
        new_traffic = self._fetch_traffic_data()
        new_weather = self._fetch_weather_data()
        new_closures = self._fetch_road_closures()

        significant_change = self._detect_significant_changes(new_traffic, new_weather, new_closures)

        if significant_change:
            self.update_real_time_data(new_traffic, new_weather, new_closures)

    def reoptimize_if_needed(self, current_routes: Dict[str, List[DeliveryRequest]]) -> Dict[str, List[DeliveryRequest]]:
        """Reoptimize routes if real-time conditions change significantly."""
        if self._detect_significant_changes():
            return self.optimize_routes()
        return current_routes
