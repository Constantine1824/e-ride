"""
Tests for the find_nearest_instances method on LocationMixin.
Uses plain unit tests with mock objects to avoid needing a running database
for the Haversine distance logic, plus Django DB integration tests for the
full query path.
"""
import pytest
from unittest.mock import MagicMock, patch
from base.mixins import LocationMixin


class TestHaversineDistance:
    """Unit tests for the haversine_distance calculation."""

    def test_same_point_returns_zero(self):
        mixin = LocationMixin()
        coord = (6.5244, 3.3792)  # Lagos, Nigeria
        assert mixin.haversine_distance(coord, coord) == 0.0

    def test_known_distance(self):
        mixin = LocationMixin()
        # Lagos (6.5244, 3.3792) to Ibadan (7.3775, 3.9470)
        # Expected ~119 km
        lagos = (6.5244, 3.3792)
        ibadan = (7.3775, 3.9470)
        dist = mixin.haversine_distance(lagos, ibadan)
        assert 100 < dist < 140  # Rough range check

    def test_symmetry(self):
        mixin = LocationMixin()
        a = (6.5244, 3.3792)
        b = (9.0579, 7.4951)  # Abuja
        assert mixin.haversine_distance(a, b) == pytest.approx(
            mixin.haversine_distance(b, a), abs=0.01
        )


class TestDistanceMethods:
    """Unit tests for the distance and distance_to convenience methods."""

    def test_distance(self):
        mixin = LocationMixin()
        mixin.location = (6.5244, 3.3792)
        target = (7.3775, 3.9470)
        dist = mixin.distance(target)
        assert dist > 0

    def test_distance_to(self):
        mixin = LocationMixin()
        mixin.location = (6.5244, 3.3792)
        other = MagicMock()
        other.location = (7.3775, 3.9470)
        dist = mixin.distance_to(other)
        assert dist > 0

    def test_distance_to_no_location_attr(self):
        mixin = LocationMixin()
        mixin.location = (6.5244, 3.3792)
        other = object()
        with pytest.raises(AttributeError):
            mixin.distance_to(other)


@pytest.mark.django_db
class TestFindNearestInstances:
    """Integration tests for find_nearest_instances using the Driver model."""

    @pytest.fixture
    def setup_drivers(self, django_user_model):
        """Create multiple drivers at known locations around Lagos."""
        from apps.Accounts.models import Driver, UserRole

        role, _ = UserRole.objects.get_or_create(name='Driver')
        drivers = []

        driver_data = [
            # (username, email, lat, lon, availability, label)
            ('driver1', 'd1@test.com', 6.5300, 3.3800, 'ONLINE', 'Near Lagos'),
            ('driver2', 'd2@test.com', 6.6000, 3.4000, 'ONLINE', 'Slightly farther'),
            ('driver3', 'd3@test.com', 7.3775, 3.9470, 'ONLINE', 'In Ibadan'),
            ('driver4', 'd4@test.com', 6.5250, 3.3795, 'OFFLINE', 'Near but offline'),
            ('driver5', 'd5@test.com', 6.5260, 3.3798, 'ONLINE', 'Very close'),
        ]

        for username, email, lat, lon, avail, label in driver_data:
            user = django_user_model.objects.create_user(
                username=username, email=email, password='testpass123'
            )
            user.role = role
            user.save()
            driver = Driver.objects.create(
                user=user,
                first_name=label,
                last_name='Test',
                nin=1234567890,
                car_type='Sedan',
                plate_number=f'ABC-{username}',
                availability_status=avail,
                location=(lat, lon),
            )
            drivers.append(driver)

        return drivers

    @pytest.fixture
    def client_profile(self, django_user_model):
        """Create a client at a known location in Lagos."""
        from apps.Accounts.models import Client, UserRole

        role, _ = UserRole.objects.get_or_create(name='Client')
        user = django_user_model.objects.create_user(
            username='client1', email='c1@test.com', password='testpass123'
        )
        user.role = role
        user.save()
        client_obj = Client.objects.create(
            user=user,
            first_name='Test',
            last_name='Client',
            location=(6.5244, 3.3792),  # Central Lagos
        )
        return client_obj

    def test_returns_sorted_by_distance(self, setup_drivers, client_profile):
        """Nearest drivers should be sorted closest first."""
        results = client_profile.find_nearest_instances(
            type(setup_drivers[0]), limit=10, max_distance_km=200
        )
        distances = [dist for _, dist in results]
        assert distances == sorted(distances)

    def test_excludes_offline_drivers(self, setup_drivers, client_profile):
        """Only ONLINE drivers should be returned."""
        from apps.Accounts.models import Driver

        results = client_profile.find_nearest_instances(
            Driver, limit=10, max_distance_km=200
        )
        driver_names = [d.first_name for d, _ in results]
        assert 'Near but offline' not in driver_names

    def test_respects_limit(self, setup_drivers, client_profile):
        """Should return at most `limit` results."""
        from apps.Accounts.models import Driver

        results = client_profile.find_nearest_instances(
            Driver, limit=2, max_distance_km=200
        )
        assert len(results) <= 2

    def test_respects_max_distance(self, setup_drivers, client_profile):
        """Should exclude drivers beyond max_distance_km."""
        from apps.Accounts.models import Driver

        # Only include drivers within 20km (should exclude Ibadan ~119km away)
        results = client_profile.find_nearest_instances(
            Driver, limit=10, max_distance_km=20
        )
        for _, dist in results:
            assert dist <= 20

        driver_names = [d.first_name for d, _ in results]
        assert 'In Ibadan' not in driver_names

    def test_empty_when_no_location(self, setup_drivers, django_user_model):
        """Should return empty list when caller has no location."""
        from apps.Accounts.models import Client, Driver, UserRole

        role, _ = UserRole.objects.get_or_create(name='Client')
        user = django_user_model.objects.create_user(
            username='no_loc', email='noloc@test.com', password='testpass123'
        )
        user.role = role
        user.save()
        client_obj = Client.objects.create(
            user=user,
            first_name='NoLoc',
            last_name='Client',
            location=None,
        )
        results = client_obj.find_nearest_instances(Driver)
        assert results == []

    def test_returns_tuples(self, setup_drivers, client_profile):
        """Each result should be a (instance, distance) tuple."""
        from apps.Accounts.models import Driver

        results = client_profile.find_nearest_instances(
            Driver, limit=3, max_distance_km=200
        )
        for item in results:
            assert len(item) == 2
            instance, dist = item
            assert isinstance(instance, Driver)
            assert isinstance(dist, float)
