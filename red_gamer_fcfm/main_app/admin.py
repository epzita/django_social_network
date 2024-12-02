from django.contrib import admin
from .models import *

# Registro de los modelos en el admin
admin.site.register(Post)
admin.site.register(VideoGame)
admin.site.register(UserFCFM)
admin.site.register(Follow)