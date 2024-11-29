from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from .models import ApplicantProfile, EmployerProfile, User

admin.site.register(User)
admin.site.register(ApplicantProfile)
admin.site.register(EmployerProfile)
admin.site.register(ContentType)
admin.site.register(Permission)
