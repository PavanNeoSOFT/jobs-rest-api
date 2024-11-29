import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class User(AbstractUser):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def assign_profile(self, user_type):
        self.save()
        if user_type.lower() == "applicant":
            profile = ApplicantProfile.objects.create()  # Create with null values
            self.content_type = ContentType.objects.get_for_model(ApplicantProfile)

        elif user_type.lower() == "employer":
            profile = EmployerProfile.objects.create(
                user=self.id
            )  # Create with null values
            self.content_type = ContentType.objects.get_for_model(EmployerProfile)

        else:
            raise ValueError("Invalid user_type. Must be 'applicant' or 'employer'.")

        self.object_id = profile.id
        self.save()


class ApplicantProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="applicant_profile"
    )
    full_name = models.CharField(null=True, blank=True, max_length=50)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    resume_file = models.FileField(upload_to="resumes/", null=True, blank=True)
    skills = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def is_profile_complete(self):
        return all([self.phone_number, self.address, self.resume_file, self.skills])

    def save(self, *args, **kwargs):
        if self.pk:
            old_file = ApplicantProfile.objects.get(pk=self.pk).resume_file
            if old_file and old_file != self.resume_file:
                if os.path.isfile(old_file.path):
                    os.remove(old_file.path)

        if self.resume_file:
            self.resume_file.name = f"applicant_{self.user.id}.pdf"

        super().save(*args, **kwargs)


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employer_profile"
    )
    company_name = models.CharField(max_length=100)
    company_website = models.URLField()
    location = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.company_name

    def is_profile_complete(self):
        if (
            self.company_name
            and self.company_website
            and self.location
            and self.description
        ):
            return True
        return False
