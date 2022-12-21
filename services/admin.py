""" Admin config file for services app """
from django.contrib import admin
from .models import Services, ServiceHistory


class services_(admin.ModelAdmin):
    list_display = ('price', 'description', 'price_id', 'service_name')


admin.site.register(Services, services_)
admin.site.register(ServiceHistory)
