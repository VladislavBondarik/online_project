from django.contrib import admin
from .models import Course, Module, Material, Enrollment, UserProgress

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Material)
admin.site.register(Enrollment)
admin.site.register(UserProgress)
