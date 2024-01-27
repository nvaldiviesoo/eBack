"""
Views for the user API.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import authenticate


from .serializers import UserSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Create a token for the newly registered user
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response({'data': serializer.data, 'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(TokenObtainPairView):

  def post(self, request, *args, **kwargs):
        username = request.data.get('email', None)
        password = request.data.get('password', None)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            user_data = {
                'username': user.name,
                'email': user.email,
                'is_superuser': user.is_superuser,
            }
            response = super().post(request, *args, **kwargs)
            response.data['user'] = user_data
            return Response({'data': response.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


