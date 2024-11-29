from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from users.models import User
from users.models import ApplicantProfile, EmployerProfile


class RegisterSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "password",
            "user_type",
            "email",
        ]

    def validate(self, data):
        if data["user_type"] not in ["applicant", "employer"]:
            raise serializers.ValidationError("user_type must be applicant or employer")

        return data

    def create(self, validated_data):
        user_type = validated_data.pop("user_type")
        password = validated_data.pop("password")

        user = User.objects.create(password=make_password(password), **validated_data)
        user.save()

        if user_type == "applicant":
            content_type = ContentType.objects.get_for_model(ApplicantProfile)
            profile = ApplicantProfile.objects.create(
                user=user, full_name=user.first_name + " " + user.last_name
            )

        else:
            content_type = ContentType.objects.get_for_model(EmployerProfile)
            profile = EmployerProfile.objects.create(user=user)

        user.content_type = content_type
        user.object_id = profile.id
        groups_obj = Group.objects.get(name=user_type)
        user.groups.set([groups_obj])
        user.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    user_type = serializers.CharField()
    extra_info = serializers.DictField(write_only=True)
    resume_file = serializers.FileField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "extra_info",
            "resume_file",
        ]

    def validate_resume_file(self, file):
        if file.content_type != "application/pdf":
            raise serializers.ValidationError("Only PDF files are supported.")
        return file

    def to_representation(self, instance):

        extra_details = {}
        if instance.content_type.model == "applicantprofile":
            user_type = "Applicant"
            resume_file_url = (
                instance.content_object.resume_file.url
                if instance.content_object.resume_file
                else None
            )
            extra_details = {
                "full_name": instance.content_object.full_name,
                "phone_number": instance.content_object.phone_number,
                "address": instance.content_object.address,
                "resume_file": resume_file_url,
                "skills": instance.content_object.skills,
            }

        else:
            user_type = "Employer"
            extra_details = {
                "company_name": instance.content_object.company_name,
                "company_website": instance.content_object.company_website,
                "location": instance.content_object.location,
                "description": instance.content_object.description,
            }

        user_details = {
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
            "user_type": user_type,
            "extra_info": extra_details,
            "is_profile_complete": instance.content_object.is_profile_complete(),
        }

        return user_details

    def update(self, obj, validated_data):
        extra_info = validated_data.pop("extra_info")
        extra_info.pop("full_name", None)
        resume_file = validated_data.pop("resume_file", None)
        user_type = validated_data.pop("user_type")
        validated_data.pop("is_profile_complete", None)

        for key, value in validated_data.items():
            setattr(obj, key, value)

        for key, value in extra_info.items():
            setattr(obj.content_object, key, value)

        if user_type == "applicant":
            obj.content_object.full_name = obj.first_name + " " + obj.last_name
            if resume_file is not None:
                obj.content_object.resume_file = resume_file

        obj.save()
        obj.content_object.save()

        return obj
