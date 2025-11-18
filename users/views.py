# users/views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from .serializers import RegisterSerializer, UserSerializer
from .models import ArtistProfile
from .serializers import ArtistProfileSerializer

# -----------------------------
# Registration Endpoint
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes=[]
    authentication_classes=[]

    def post(self, request, *args, **kwargs):
        # print(self.request.body)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            "user_id": user.id,
            "token": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)


# -----------------------------
# JWT Token Endpoint (Login)
# -----------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer to include 'role' in token
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token
    

    def validate(self, attrs):
        # This gets called on successful authentication
        data = super().validate(attrs)  # This gives us {'refresh': ..., 'access': ...}

        # Add extra user info to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            # add any other fields you want
        }
        print(data)

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer




# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer  # optional, if you want full control


class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Optional: add custom claims to the access token
        refresh.access_token['role'] = user.role
        refresh.access_token['user_id'] = user.id

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                # add anything else: first_name, profile_pic, etc.
            }
        }, status=status.HTTP_200_OK)


# -----------------------------
# User Profile Endpoint
# -----------------------------
class UserDetailView(generics.RetrieveAPIView):
    """
    Get current logged-in user profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Returns the currently authenticated user
        return self.request.user
    




# GET artist profile
class ArtistProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ArtistProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # user_id = self.kwargs['user_id']
        # return ArtistProfile.objects.get(user_id=user_id)
        return self.request.user.artist_profile
    
    


# UPDATE artist profile
class ArtistProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ArtistProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        return ArtistProfile.objects.get(user_id=user_id)

