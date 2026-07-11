from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login

from user.serializers import UserSerializer, LoginSerializer


class CreateUserView(generics.CreateAPIView):
    """
    Endpoint for registering a new user
    (available to everyone)
    """

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Endpoint for managing the authenticated user's profile
    (available only to authenticated users)
    """

    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LoginView(APIView):
    """
    Endpoint for logging in a user and creating a session
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)

        return Response(
            {"detail": "Login successful"},
            status=status.HTTP_200_OK,
        )
