from django.urls import path, include
from rest_framework.routers import DefaultRouter
from jobs.api_views import (
    JobViewSet,
    ApplicationViewSet,
    MatchCheckAPIView,
    CustomObtainAuthToken,
)

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='api-job')
router.register('applications', ApplicationViewSet, basename='api-application')

urlpatterns = [
    # Token Authentication endpoint
    path('auth/token/', CustomObtainAuthToken.as_view(), name='api-token'),

    # Direct match analysis endpoint
    path('match/', MatchCheckAPIView.as_view(), name='api-match'),

    # ViewSet routes
    path('', include(router.urls)),
]
