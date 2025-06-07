from django.db import connection

class LocationMixin:

    def get_prep_value(self, value):
        """Convert (lat, lon) tuple to PostGIS-compatible WKT format"""
        lat, lon = value
        return f'SRID=4326;POINT({lon} {lat})'

    def distance(self, d_location):
        """Returns the distance between two LocationField points (in meters)"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ST_Distance(
                    ST_GeogFromText(%s),
                    ST_GeogFromText(%s)
                )
            """, [self.get_prep_value(self.location), self.get_prep_value(d_location)])
            distance_in_meters = cursor.fetchone()[0]
            return distance_in_meters/1000 #To return distance in km

    def nearest(self, table_name, limit=5):
        """Finds the nearest records in a given table to this location"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, ST_Distance(
                    location, ST_GeogFromText(%s)
                ) AS distance
                FROM {table_name}
                ORDER BY distance ASC
                LIMIT %s
            """, [self.get_prep_value(self.location), limit])
            return cursor.fetchall()

    def distance_to(self, other_instance):
        """Calculate distance to another instance that has a location field"""
        if not hasattr(other_instance, 'location'):
            raise AttributeError("Other instance must have a location field")
        return self.distance(other_instance.location)

    def find_nearest_instances(self, model_class, exclude_ids=None, limit=5):
        """
        Find nearest instances of a specific model class
        Args:
            model_class: The model class to search in (e.g., Driver, Client)
            exclude_ids: List of IDs to exclude from search
            limit: Maximum number of results to return
        Returns:
            List of tuples (instance, distance)
        """
        table_name = model_class._meta.db_table
        exclude_clause = ""
        params = [self.get_prep_value(self.location), limit]

        if exclude_ids:
            exclude_clause = "AND id NOT IN %s"
            params.insert(1, tuple(str(id) for id in exclude_ids))

        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, ST_Distance(
                    location, ST_GeogFromText(%s)
                ) AS distance
                FROM {table_name}
                WHERE location IS NOT NULL
                {exclude_clause}
                ORDER BY distance ASC
                LIMIT %s
            """, params)
            results = cursor.fetchall()
            
        # Convert results to model instances with distances
        instances_with_distances = []
        for id_, distance in results:
            instance = model_class.objects.get(id=id_)
            instances_with_distances.append((instance, distance))
        
        return instances_with_distances