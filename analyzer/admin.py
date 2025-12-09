from django.contrib import admin

from .models import AnalysisRecord, AspectResult

# Register your models here.
admin.site.register(AnalysisRecord)
admin.site.register(AspectResult)
