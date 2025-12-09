from django.contrib import admin

from .models import AnalysisSession, AnalysisRecord, AspectResult


# Register your models here.
admin.site.register(AnalysisSession)
admin.site.register(AnalysisRecord)
admin.site.register(AspectResult)
