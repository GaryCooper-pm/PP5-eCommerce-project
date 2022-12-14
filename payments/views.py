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
    template_name = 'payments/success.html'

    def test_func(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session_id = self.request.GET['session_id']
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session['payment_status'] == 'paid':
                line_item = stripe.checkout.Session.list_line_items(session_id, limit=1)  # noqa
                service_name = line_item['data'][0].description
                service = Services.objects.get(service_name=service_name)
                order_date = datetime.datetime.now()
                ServiceHistory.objects.create(booked_by=self.request.user, service_type=service, order_date=order_date)  # noqa
                return True
            else:
                return False
        except:  # noqa
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
        # domain_url = settings.DOMAIN_URL
        domain_url = settings.DOMAIN_URL
        print("domain url---->> ", domain_url)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Extract the PK from the GET Pararameter (?pk=)

        service = Services.objects.get(pk=request.GET['pk'])
        print("dfgdfhdfhgf", service.price)
        try:
            print("domain url---->> ", domain_url, 'payments/success?session_id=2133')
            checkout_session = stripe.checkout.Session.create(

                success_url=domain_url + 'payments/success/?session_id='+str(random.randint(100, 100000000)),  # noqa
                cancel_url=domain_url + 'payments/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        # 'price': service.price,
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
                # print("line_items",line_items)

            )

            print("checkout_session", checkout_session)
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            print("data----------->> ", e)
            return JsonResponse({'error': str(e)})


# Stripe webhook handler
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    wh_secret = settings.STRIPE_WH_SECRET
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
