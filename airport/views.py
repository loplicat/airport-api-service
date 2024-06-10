from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Route,
    Flight,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirportSerializer,
    AirportListSerializer,
    CrewSerializer,
    RouteSerializer,
    RouteListSerializer,
    FlightSerializer,
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
    queryset = City.objects.select_related("country")
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer
        return CitySerializer


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
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.select_related("city__country")
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        return AirportSerializer


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
    queryset = Route.objects.select_related("source__city", "destination__city")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
