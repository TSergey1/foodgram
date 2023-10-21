from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns_api = [
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
