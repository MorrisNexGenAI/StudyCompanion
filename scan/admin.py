from django.contrib import admin


from .models import Department, Course, Topic, AIRefine

# # Simple registration without customization
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(AIRefine)