
# Register your models here.
from django.contrib import admin
from .models import CustomUser  

admin.site.register(CustomUser)  # Registers the model with the admin