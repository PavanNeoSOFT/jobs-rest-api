from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from users.models import User
from apis.util import ApiResponse
from . import serializers


class RegisterUser(APIView):

    def post(self, request):
        serializer = serializers.RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return ApiResponse.serializer_error(serializer.errors, "Error Occoured")

        serializer.save()
        return ApiResponse.success(
            None,
            "User Registered Successfully",
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return ApiResponse.success(None, "User Logout successfully")

        except Exception as e:
            return ApiResponse.error(str(e), f"Error Occoured : {str(e)} ")


class UserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
            user_obj = User.objects.get(id=request.user.id)
            serializer = serializers.UserProfileSerializer(instance=user_obj)
            return ApiResponse.success(serializer.data, "User Fetched")

    def put(self, request):
            user_obj = User.objects.get(id=request.user.id)
            serializer = serializers.UserProfileSerializer(
                instance=user_obj, data=request.data
            )

            if not serializer.is_valid():
                return ApiResponse.serializer_error(serializer.errors, "Error Ocooured")

            serializer.save()
            return ApiResponse.success(serializer.data, "Updated Successfully.")
