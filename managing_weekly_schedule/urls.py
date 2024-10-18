from django.contrib import admin
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from manage_schedule.views import GetWeekSchedule, CreateRecord, DeleteRecord, UpdateRecord
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Your API Title",
        default_version='v1',
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('admin/', admin.site.urls),
    path('weekly-schedule/', GetWeekSchedule.as_view(), name='get-weekly-schedule'),
    path('create-record/', CreateRecord.as_view(), name='create-record'),
    path('delete-record/', DeleteRecord.as_view(), name='delete-record'),
    path('update-record/', UpdateRecord.as_view(), name='update-record'),
]
