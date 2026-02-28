import math

class LocationMixin:

    def distance(self, d_location):
        """Returns the distance between two LocationField points (in kilometers)"""
        # Use the haversine_distance method instead of direct database query
        distance_in_km = self.haversine_distance(self.location, d_location)
        return distance_in_km  # Return in kilometers

    def haversine_distance(self, coord1, coord2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        Returns distance in kilometers
        """
        # Helper to extract lat/lon from either dict or tuple/list
        def extract_lat_lon(coord):
            if isinstance(coord, dict):
                return float(coord['lat']), float(coord['lon'])
            return float(coord[0]), float(coord[1])
            
        # Convert decimal degrees to radians
        lat1, lon1 = extract_lat_lon(coord1)
        lat2, lon2 = extract_lat_lon(coord2)
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1 
        dlon = lon2 - lon1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r

    def distance_to(self, other_instance):
        """Calculate distance to another instance that has a location field"""
        if not hasattr(other_instance, 'location'):
            raise AttributeError("Other instance must have a location field")
        return self.distance(other_instance.location)

    def find_nearest_instances(self, model_class, limit=5, max_distance_km=50):
        """
        Find nearest instances of a model class that have a location field.
        For models with availability_status (e.g. Driver), filters to ONLINE only.
        
        Args:
            model_class: The Django model class to search (e.g. Driver).
            limit: Maximum number of results to return.
            max_distance_km: Maximum distance in km to include in results.
        
        Returns:
            List of (instance, distance_km) tuples sorted by distance ascending.
        """
        if not self.location:
            return []

        instances = model_class.objects.all()

        # Filter to only ONLINE instances for models with availability_status
        if hasattr(model_class, 'availability_status'):
            instances = instances.filter(availability_status='ONLINE')

        results = []
        for instance in instances:
            # Skip instances without a location or self
            if not instance.location:
                continue
            if hasattr(instance, 'pk') and hasattr(self, 'pk') and instance.pk == self.pk:
                continue

            dist = self.haversine_distance(self.location, instance.location)
            if dist <= max_distance_km:
                results.append((instance, round(dist, 2)))

        results.sort(key=lambda x: x[1])
        return results[:limit]