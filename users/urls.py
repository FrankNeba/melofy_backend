from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ArtistProfileDetailView, ArtistProfileUpdateView, CustomLoginView

urlpatterns = [
    # User registration
    path('register/', RegisterView.as_view(), name='register'),

    # JWT login
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ArtistProfile endpoints
    path('profile/', ArtistProfileDetailView.as_view(), name='artist_profile_detail'),
    path('profile/<int:user_id>/update/', ArtistProfileUpdateView.as_view(), name='artist_profile_update'),
]
