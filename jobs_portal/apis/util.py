from rest_framework import status
from rest_framework.response import Response


class ApiResponse:
    @staticmethod
    def success(
        data=None,
        message="Request processed successfully.",
        status_code=status.HTTP_200_OK,
    ):
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data if data is not None else {},
            },
            status=status_code,
        )

    @staticmethod
    def error(
        errors=None,
        message="An error occurred.",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        return Response(
            {
                "status": "error",
                "message": message,
                "errors": errors if errors is not None else {},
            },
            status=status_code,
        )

    @staticmethod
    def serializer_error(
        serializer_errors,
        message="Invalid data provided.",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        formatted_errors = {
            field: error[0] if isinstance(error, list) else error
            for field, error in serializer_errors.items()
        }
        return Response(
            {"status": "error", "message": message, "errors": formatted_errors},
            status=status_code,
        )
