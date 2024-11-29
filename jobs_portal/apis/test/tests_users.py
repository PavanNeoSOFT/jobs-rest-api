from faker import Faker
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User


class RegisterAPITest(APITestCase):

    def setUp(self):

        self.fake = Faker()
        self.register = reverse("register_user")

        self.user_create_data_employer = {
            "username": self.fake.user_name(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "password": self.fake.password(),
            "user_type": "employer",
            "email": self.fake.email(),
        }

        self.user_create_data_applicant = {
            "username": self.fake.user_name(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "password": self.fake.password(),
            "user_type": "applicant",
            "email": self.fake.email(),
        }

        return super().setUp()

    def test_register_with_proper_creds(self):

        Group.objects.get_or_create(name="employer")
        Group.objects.get_or_create(name="applicant")

        response = self.client.post(
            path=self.register, data=self.user_create_data_employer
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            path=self.register, data=self.user_create_data_applicant
        )
        self.assertEqual(response.status_code, 200)

    def test_register_and_return_error(self):

        user_create_data_employer = {
            "username": "",
            "first_name": "",
            "last_name": "",
            "password": "",
            "user_type": "employer",
            "email": "",
        }
        user_create_data_applicant = {
            "username": "",
            "first_name": "",
            "last_name": "",
            "password": "",
            "user_type": "applicant",
            "email": "",
        }

        response = self.client.post(path=self.register, data=user_create_data_employer)
        self.assertEqual(response.status_code, 400)

        response = self.client.post(path=self.register, data=user_create_data_applicant)
        self.assertEqual(response.status_code, 400)

    def test_register_with_used_username(self):

        user_create_data = {
            "username": "admin",
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "password": self.fake.password(),
            "email": self.fake.email(),
        }

        User.objects.create(**user_create_data)

        response = self.client.post(path=self.register, data=user_create_data)
        self.assertEqual(response.status_code, 400)

    def test_register_with_invalid_user_type(self):

        new_dict = self.user_create_data_employer
        new_dict.update({"user_type": "abcdefgh"})

        response = self.client.post(path=self.register, data=new_dict)
        self.assertEqual(response.status_code, 400)


class LoginAPITest(APITestCase):

    def setUp(self):

        self.fake = Faker()
        self.login = reverse("token_obtain_pair")
        self.fake_username = self.fake.user_name()
        self.fake_password = make_password(self.fake.password())

        self.user_correct_creds = user_correct_creds = {
            "username": "admin",
            "password": "admin",
        }

        user_correct_creds.update(
            {
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "user_type": "employer",
                "email": self.fake.email(),
            }
        )

        Group.objects.get_or_create(name="employer")
        Group.objects.get_or_create(name="applicant")
        register = reverse("register_user")
        self.client.post(path=register, data=user_correct_creds)

        return super().setUp()

    def test_login_with_correct_creds(self):

        response = self.client.post(path=self.login, data=self.user_correct_creds)
        self.assertEqual(response.status_code, 200, "Error : Login Unsuccessfull!")

    def test_login_with_incorrect_creds(self):

        response = self.client.post(
            path=self.login,
            data={"username": self.fake_username, "password": self.fake_password},
        )
        self.assertEqual(response.status_code, 401, "Error : Login Successfull!")

    def test_login_with_empty_creds(self):

        response = self.client.post(
            path=self.login,
            data={"username": "", "password": ""},
        )
        self.assertEqual(response.status_code, 400, "Error : Login Successfull!")


class LogoutAPITest(APITestCase):
    def setUp(self):
        self.fake = Faker()
        self.logout = reverse("logout")  # Ensure "logout" URL name maps to TokenBlacklistView
        self.login = reverse("token_obtain_pair")

        self.user_data = {
            "username": "admin",
            "password": "admin",
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "user_type": "employer",
            "email": self.fake.email(),
        }

        Group.objects.get_or_create(name="employer")
        Group.objects.get_or_create(name="applicant")

        register = reverse("register_user")
        self.client.post(path=register, data=self.user_data)

        login_response = self.client.post(
            path=self.login,
            data={"username": self.user_data["username"], "password": self.user_data["password"]},
        )

        self.access_token = login_response.data.get("access")
        self.refresh_token = login_response.data.get("refresh")

        return super().setUp()

    def test_logout_with_correct_refresh_token(self):
        response = self.client.post(
            path=self.logout,
            data={"refresh_token": self.refresh_token},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200, "Error: Logout with correct token failed!")

    def test_logout_with_no_refresh_token(self):
        response = self.client.post(
            path=self.logout,
            data={},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400, "Error: Logout without token succeeded!")

    def test_logout_with_invalid_refresh_token(self):
        response = self.client.post(
            path=self.logout,
            data={"refresh": "invalid_refresh_token"},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400, "Error: Logout with invalid token succeeded!")


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.fake = Faker()

        self.user = {
            "username": "testuser",
            "password": "password123",
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "user_type": "applicant",
        }
        Group.objects.get_or_create(name="applicant")

        register = reverse("register_user")
        self.client.post(path=register, data=self.user)

        login = self.client.post(
            path=reverse("token_obtain_pair"),
            data={"username": self.user["username"], "password": self.user["password"]},
        )
        self.access_token = login.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.profile_url = reverse("user_profile")

    def test_get_user_profile_success(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_employer_user_profile(self):
        self.user = {
            "username": "testusere",
            "password": "password123",
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "user_type": "employer",
        }
        Group.objects.get_or_create(name="employer")

        register = reverse("register_user")
        self.client.post(path=register, data=self.user)

        login = self.client.post(
            path=reverse("token_obtain_pair"),
            data={"username": self.user["username"], "password": self.user["password"]},
        )
        self.access_token = login.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_profile_not_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_success(self):
        data = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "email": "updatedemail@example.com",
            "user_type": "applicant",
            "extra_info": {"address": "Updated Address", "phone_number": "1234567890"},
        }
        response = self.client.put(self.profile_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_profile_not_pdf(self):
        with open(str(settings.BASE_DIR / "resumes/Jethalal.jpeg"), "rb") as img_file:
            mock_file = SimpleUploadedFile(
                name="Jethalal.jpeg",
                content=img_file.read(),
                content_type="image/jpeg"
            )
            
        data = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "email": "updatedemail@example.com",
            "user_type": "applicant",
            # "extra_info": {"address": "Updated Address", "phone_number": "1234567890"},
            "resume_file" : mock_file,
        }
        response = self.client.put(self.profile_url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_with_pdf(self):
        with open(str(settings.BASE_DIR / "resumes/applicant_7.pdf"), "rb") as img_file:
            mock_file = SimpleUploadedFile(
                name="Jethalal.jpeg",
                content=img_file.read(),
                content_type="application/pdf"
            )
            
        data = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "email": "updatedemail@example.com",
            "user_type": "applicant",
            # "extra_info": {"address": "Updated Address", "phone_number": "1234567890"},
            "resume_file" : mock_file,
        }
        response = self.client.put(self.profile_url, data=data, format="multipart")
        self.assertEqual(response.status_code,200)

    def test_update_user_profile_invalid_data(self):
        data = {"email": "not-an-email"}
        response = self.client.put(self.profile_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_missing_data(self):
        data = {}
        response = self.client.put(self.profile_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
