from django.contrib import admin
from .models import User, ArtistProfile

# Register your models here.
admin.site.register(User)
admin.site.register(ArtistProfile)
