""" Payments app views file """

import stripe
import random
import datetime
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from services.models import Services, ServiceHistory
from blue_turtle import settings


class PaymentsView(TemplateView):
    """ Renders the payments page """
    template_name = 'payments/payments.html'


class SuccessView(TemplateView):
    """ Retrieves the payments success from stripe
        then adds the purchased service to the users Service History """
    def dispatch(self, request, *args, **kwargs):
        self.test_func()
        return super(SuccessView, self).dispatch(request, *args, **kwargs)
    template_name = 'payments/success.html'

    def test_func(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        service_name = self.request.GET.get('service_name', '')
        service = Services.objects.get(service_name=service_name)
        order_date = datetime.datetime.now()
        ServiceHistory.objects.create(booked_by=self.request.user, service_type=service, order_date=order_date)

        try:
            return True
        except Exception as e:
            return False


class CancelledView(TemplateView):
    """ Renders the payments cancelled/failed page """
    template_name = 'payments/cancelled.html'


@csrf_exempt
# Taken from Testdriven.io
def stripe_config(request):

    if request.method == 'GET':
        stripe_config_data = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config_data, safe=False)
    return HttpResponse(status=400)


@csrf_exempt
# Taken from Testdriven.io
def create_checkout_session(request):

    if request.method == 'GET':
        domain_url = settings.DOMAIN_URL
        print("domain url---->> ", domain_url)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Extract the PK from the GET Pararameter (?pk=)

        service = Services.objects.get(pk=request.GET['pk'])
        print("dfgdfhdfhgf", service.price)
        try:
            checkout_session = stripe.checkout.Session.create(

                success_url=domain_url + 'payments/success/?session_id={}&service_name={}'.format(str(random.randint(100, 100000000)), service.service_name),  # noqa
                cancel_url=domain_url + 'payments/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'quantity': 1,
                        'price_data': {
                        'currency': 'GBP',
                        'unit_amount': int(service.price*100),
                        'product_data': {
                            'name': service.service_name,
                            'description': service.description,
                        },

                    }
                    }
                ],

            )

            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


# Stripe webhook handler
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    # wh_secret = settings.STRIPE_WH_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:  # noqa
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:  # noqa
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")

    return HttpResponse(status=200)
