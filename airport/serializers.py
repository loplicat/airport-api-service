from rest_framework import serializers

from airport.models import (
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class CityListSerializer(CitySerializer):
    country = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "image"
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "city",
            "closest_big_city"
        )


class AirportListSerializer(AirportSerializer):
    city = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    source_city = serializers.CharField(
        source="source.city.name", read_only=True
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    destination_city = serializers.CharField(
        source="destination.city.name", read_only=True
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "source_city",
            "destination",
            "destination_city",
            "distance")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )


class FlightListSerializer(FlightSerializer):
    source = serializers.CharField(
        source="route.source.city.name", read_only=True
    )
    destination = serializers.CharField(
        source="route.destination.city.name", read_only=True
    )
    airplane = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "source",
            "destination",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )
