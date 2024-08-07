from rest_framework import routers

from airport.views import (
    CountryViewSet,
    CityViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    CrewViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()

router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("airplanetypes", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("crews", CrewViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls

app_name = "airport"
