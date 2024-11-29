from django.urls import path, include

urlpatterns = [
    path("user/",include("apis.users_api.urls")),
    path("job/",include("apis.jobs_api.urls")),
]