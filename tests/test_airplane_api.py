import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Country, City, AirplaneType, Airplane, Airport, Route, Flight
from airport.serializers import AirplaneListSerializer, AirplaneSerializer


AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane_type(**params):
    defaults = {
        "name": "Boeing 737",
    }
    defaults.update(params)

    airplane_type, _ = AirplaneType.objects.get_or_create(**defaults)

    return airplane_type


def sample_airplane(**params):
    airplane_type = sample_airplane_type()

    defaults = {
        "name": "Boeing 737-800",
        "rows": 30,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def image_upload_url(airplane_id):
    """Return URL for airplane image upload"""
    return reverse("airport:airplane-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


def detail_flight_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


def sample_country(**params):
    defaults = {
        "name": "Ukraine",
    }
    defaults.update(params)

    return Country.objects.create(**defaults)


def sample_city(**params):
    country = sample_country()

    defaults = {"name": "Kyiv", "country": country}
    defaults.update(params)

    return City.objects.create(**defaults)


def sample_airport(**params):
    city = sample_country()

    defaults = {
        "name": "Kyiv international airport",
        "closest_big_city": "Kyiv",
        "city": city,
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    source_airport = sample_airport()
    country = sample_country(name="United Kingdom")
    city = sample_city(name="London", country=country)
    destination_airport = sample_airport(
        name="Heathrow Airport", closest_big_city="London", city=city
    )

    defaults = {
        "source": source_airport,
        "destination": destination_airport,
        "distance": 2500,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_flight(**params):
    airplane = sample_airplane()
    route = sample_route()

    defaults = {
        "departure_time": "2024-10-02 14:00:00",
        "arrival_time": "2024-10-02 23:00:00",
        "airplane": airplane,
        "route": route,
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        sample_airplane()
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.order_by("id")
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_airplanes_by_type_ids(self):
        type1 = sample_airplane_type(name="Airplane Type 1")
        type2 = sample_airplane_type(name="Airplane Type 2")

        airplane1 = sample_airplane(name="Airplane 1", airplane_type=type1)
        airplane2 = sample_airplane(name="Airplane 2", airplane_type=type2)

        airplane3 = sample_airplane(name="Airplane without types")

        res = self.client.get(
            AIRPLANE_URL, {"airplane_types": f"{type1.id},{type2.id}"}
        )

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)
        serializer3 = AirplaneListSerializer(airplane3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])

        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_airplanes_by_name(self):
        airplane1 = sample_airplane(
            name="Airplane Test 1",
            rows=5,
            seats_in_row=2,
        )
        airplane2 = sample_airplane(
            name="Airplane Test 2",
            rows=20,
            seats_in_row=5,
        )
        airplane3 = sample_airplane(name="Airplane 3")

        res = self.client.get(AIRPLANE_URL, {"name": "Test"})

        serializer1_data = AirplaneListSerializer(airplane1).data
        serializer2_data = AirplaneListSerializer(airplane2).data
        serializer3_data = AirplaneListSerializer(airplane3).data

        self.assertIn(serializer1_data, res.data["results"])
        self.assertIn(serializer2_data, res.data["results"])
        self.assertNotIn(serializer3_data, res.data["results"])

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Test Airplane",
            "rows": 10,
            "seats_in_row": 10,
            "airplane_type": sample_airplane_type().id,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        _type = sample_airplane_type()
        payload = {
            "name": "Airplane Boeing",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": _type.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(id=res.data["id"])
        for key in payload.keys():
            if key == "airplane_type":
                self.assertEqual(payload[key], airplane.airplane_type.id)
            else:
                self.assertEqual(payload[key], getattr(airplane, key))


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@example.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane_type = sample_airplane_type(name="Type Boeing")
        self.airplane = sample_airplane(airplane_type=self.airplane_type)
        self.country = Country.objects.create(name="Test")
        self.city = City.objects.create(name="Name", country=self.country)
        self.airport = Airport.objects.create(
            name="Airport", city=self.city, closest_big_city="City"
        )
        self.route = Route.objects.create(
            source=self.airport, destination=self.airport, distance=1000
        )
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            route=self.route,
            departure_time="2024-04-01T08:15:30.186000Z",
            arrival_time="2024-04-01T08:15:30.186000Z",
        )

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to airplane"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_is_in_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_is_in_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data["results"][0])

    def test_image_is_in_flight_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_flight_url(self.flight.id))

        self.assertIn("airplane_image", res.data)

    def test_put_airplane_not_allowed(self):
        payload = {
            "name": "Airplane 111",
            "rows": 10,
            "seats_in_row": 4,
            "airplane_type": sample_airplane_type(),
        }

        airplane = sample_airplane()
        url = detail_url(airplane.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_airplane_not_allowed(self):
        airplane = sample_airplane()
        url = detail_url(airplane.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
