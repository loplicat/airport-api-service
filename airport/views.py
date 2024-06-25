from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from airport.models import (
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Route,
    Flight,
    Order,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneImageSerializer,
    AirplaneListSerializer,
    AirportSerializer,
    AirportListSerializer,
    CrewSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = Pagination


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = City.objects.select_related("country")
    serializer_class = CitySerializer
    pagination_class = Pagination

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
    pagination_class = Pagination


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the airplanes with filters"""
        name = self.request.query_params.get("name")
        airplane_types = self.request.query_params.get("airplane_types")
        capacity_gte = self.request.query_params.get("capacity_gte")

        queryset = self.queryset.annotate(
            total_capacity=F("rows") * F("seats_in_row")
        )

        if name:
            queryset = queryset.filter(name__icontains=name)

        if airplane_types:
            airplane_type_ids = self._params_to_ints(airplane_types)
            queryset = queryset.filter(airplane_type__id__in=airplane_type_ids)

        if capacity_gte:
            queryset = queryset.filter(total_capacity__gte=capacity_gte)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image"
    )
    def upload_image(self, request, pk: int = None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.select_related("city__country")
    serializer_class = AirportSerializer
    pagination_class = Pagination

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
    pagination_class = Pagination


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Route.objects.select_related("source__city", "destination__city")
    serializer_class = RouteSerializer
    pagination_class = Pagination

    def get_queryset(self):
        """Retrieve the route with filters"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("flights", "flights__crew")

        if source:
            queryset = queryset.filter(source__city__name__icontains=source)

        if destination:
            queryset = queryset.filter(destination__city__name__icontains=destination)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source name (ex. ?source=Kyiv)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination name (ex. ?destination=New York)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of routs"""
        return super().list(request, *args, **kwargs)


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Flight.objects.select_related(
        "route__source__city",
        "route__destination__city",
        "airplane"
    ).prefetch_related("crew").annotate(
        tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
        )
    )
    serializer_class = FlightSerializer
    pagination_class = Pagination

    def get_queryset(self):
        """Retrieve the flights with filters"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            queryset = queryset.filter(route__source__city__name__icontains=source)

        if destination:
            queryset = queryset.filter(route__destination__city__name__icontains=destination)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source name (ex. ?source=Kyiv)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination name (ex. ?destination=New York)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of flights"""
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get_queryset(self):
        queryset = self.queryset.prefetch_related(
            "tickets__flight__route",
            "tickets__flight__airplane",
            "tickets__flight__crew"
        )
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
