from django.db import models, connection
from django.core.exceptions import ValidationError

class LocationField(models.Field):
    description = "A geographical point (latitude, longitude) stored as PostGIS Geography"

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
        return 'geography(Point, 4326)'  # Stores as PostGIS Geography

    def from_db_value(self, value, expression, connection):
        """Convert PostGIS value to a tuple (lat, lon) when reading from the DB"""
        if value is None:
            return None
        return tuple(map(float, value.strip('POINT()').split()))

    def to_python(self, value):
        """Ensure values are stored as (lat, lon) tuples"""
        try:
            if isinstance(value, tuple):
                return value
            if value is None:
                return None
            return tuple(map(float, value.strip('POINT()').split()))
        except ValidationError:
            print('validation error')
            raise ValidationError #Will write a custom exception later

    def get_prep_value(self, value):
        """Convert (lat, lon) tuple to PostGIS-compatible WKT format"""
        if value is None:
            return None
        lat, lon = value
        return f'SRID=4326;POINT({lon} {lat})'