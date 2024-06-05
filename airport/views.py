from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Route, Flight,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirportSerializer,
    CrewSerializer,
    RouteSerializer, FlightSerializer,
)


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer



