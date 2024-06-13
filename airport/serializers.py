from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
    Order
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


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "capacity",
            "airplane_type",
            "image"
        )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


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
        fields = ("id", "first_name", "last_name")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


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


class RouteDetailSerializer(RouteListSerializer):
    source_city = serializers.CharField(
        source="source.city.name", read_only=True
    )
    destination_city = serializers.CharField(
        source="destination.city.name", read_only=True
    )
    flights = FlightSerializer(
        many=True,
        read_only=True)

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "source_city",
            "destination",
            "destination_city",
            "distance",
            "flights",
        )


class FlightListSerializer(FlightSerializer):
    source = serializers.CharField(
        source="route.source", read_only=True
    )
    destination = serializers.CharField(
        source="route.destination", read_only=True
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


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
