from django.contrib import admin

from repairs.models import Measurement, MeasurementImage, Project, ProjectContact

admin.site.register(Measurement)
admin.site.register(MeasurementImage)
admin.site.register(Project)
admin.site.register(ProjectContact)
