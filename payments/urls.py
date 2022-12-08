""" Payments and stripe url config file """
from django.urls import path
from .views import (PaymentsView, stripe_config,
                    create_checkout_session,
                    SuccessView, CancelledView,
                    stripe_webhook)

APP_NAME = 'payments'
urlpatterns = [
    path('', views.PaymentsView.as_view(), name='payments'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),  # new
    path('success/', SuccessView.as_view(), name="success"),
    path('cancelled/', CancelledView.as_view(), name="cancelled"),
    path('webhook/', stripe_webhook),
]
