from django.db import models
from django.core.exceptions import ValidationError
import json

class LocationField(models.Field):
    description = "A geographical point (latitude, longitude) stored as JSON"

    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['null']
        del kwargs['blank']
        return name, path, args, kwargs
    
    def db_type(self, connection):
        # Use JSONB to store location data to avoid PostGIS dependency
        return 'jsonb' if connection.vendor == 'postgresql' else 'text'

    def from_db_value(self, value, expression, connection):
        """Convert stored value to a tuple (lat, lon) when reading from the DB"""
        if value is None:
            return None
        if isinstance(value, str):
            # For non-PostgreSQL databases that store as text
            try:
                parsed = json.loads(value)
                return tuple(parsed) if isinstance(parsed, list) else parsed
            except json.JSONDecodeError:
                # If it's a string format like "lat,lon", parse it
                lat, lon = map(float, value.split(','))
                return (lat, lon)
        elif isinstance(value, dict) and 'lat' in value and 'lon' in value:
            # Dictionary format
            return (value['lat'], value['lon'])
        elif isinstance(value, list) and len(value) == 2:
            # List format
            return tuple(value)
        return value

    def to_python(self, value):
        """Ensure values are stored as (lat, lon) tuples"""
        if value is None:
            return None
        if isinstance(value, (list, tuple)) and len(value) == 2:
            lat, lon = value
            return (float(lat), float(lon))
        if isinstance(value, str):
            try:
                # Try parsing as JSON first
                parsed = json.loads(value)
                if isinstance(parsed, dict) and 'lat' in parsed and 'lon' in parsed:
                    return (float(parsed['lat']), float(parsed['lon']))
                elif isinstance(parsed, list) and len(parsed) == 2:
                    return (float(parsed[0]), float(parsed[1]))
                else:
                    # Try parsing as "lat,lon" string
                    lat, lon = map(float, value.split(','))
                    return (lat, lon)
            except (json.JSONDecodeError, ValueError):
                raise ValidationError('Invalid location format. Use [lat, lon] or {"lat": lat, "lon": lon}')
        if isinstance(value, dict) and 'lat' in value and 'lon' in value:
            return (float(value['lat']), float(value['lon']))
        raise ValidationError('Invalid location format. Use [lat, lon] or {"lat": lat, "lon": lon}')

    def get_prep_value(self, value):
        """Convert (lat, lon) tuple to JSON string for storage"""
        if value is None:
            return None
        lat, lon = self.to_python(value)
        return json.dumps({'lat': lat, 'lon': lon})