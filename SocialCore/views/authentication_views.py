from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..serializers import UserSignupSerializer, UserLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class UserSignupView(generics.CreateAPIView):
    """
    View for handling user signup requests.

    Allows any user (authenticated or not) to access this view.
    Uses the `UserSignupSerializer` to validate and create new user instances.

    Methods:
        post(request): Handles POST requests for creating a new user.
                       Returns a success message and HTTP 201 status if the user is created.
    """
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for user signup.

        Validates the input data using the `UserSignupSerializer`, and if the data
        is valid, a new user is created. Responds with a success message.

        Args:
            request: The HTTP request object containing the signup data.

        Returns:
            Response: A success message and HTTP 201 status if the user is created successfully,
                      otherwise raises a validation error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "User created successfully"}, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    """
    View for handling user login requests.

    Allows any user (authenticated or not) to access this view.
    Uses the `UserLoginSerializer` to validate login credentials.

    Methods:
        post(request): Handles POST requests for user login.
                       Returns JWT tokens (refresh and access) if login is successful.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for user login.

        Validates the input data using the `UserLoginSerializer`, and if the credentials
        are correct, returns a JWT access and refresh token pair.

        Args:
            request: The HTTP request object containing the login data.

        Returns:
            Response: A response with a refresh token and an access token if login is successful,
                      otherwise raises a validation error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
