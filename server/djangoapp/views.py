from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

DEALERSHIPS_URL = 'https://afa16f53.eu-de.apigw.appdomain.cloud/api/dealership'
REVIEWS_URL = 'https://afa16f53.eu-de.apigw.appdomain.cloud/api/review'


def about(request):
    return render(request, 'djangoapp/about.html')


def contact(request):
    return render(request, 'djangoapp/contact.html')


def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = 'Invalid username or password.'
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error('New user')
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = 'User already exists.'
            return render(request, 'djangoapp/registration.html', context)


def get_dealerships(request):
    if request.method == 'GET':
        dealerships = get_dealers_from_cf(DEALERSHIPS_URL)
        context = {'dealerships': dealerships}
        return render(request, 'djangoapp/index.html', context)


def get_dealer_details(request, dealer_id):
    if request.method == 'GET':
        reviews = get_dealer_reviews_from_cf(REVIEWS_URL, dealerId=dealer_id)
        context = {'reviews': reviews, 'dealer_id': dealer_id}
        return render(request, 'djangoapp/dealer_details.html', context)


def add_review(request, dealer_id):
    if not request.user.is_authenticated:
        return redirect('djangoapp:login')
    context = {'dealer_id': dealer_id}
    if request.method == 'GET':
        context['cars'] = CarModel.objects.all()
        context['dealer'] = get_dealers_from_cf(DEALERSHIPS_URL, dealerId=dealer_id)[0]
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        review = {
            'name': request.user.first_name + ' ' + request.user.last_name,
            'dealership': dealer_id,
            'review': request.POST.get('content', ''),
            'purchase': 'purchasecheck' in request.POST
        }
        if review['purchase']:
            review['purchase_date'] = request.POST.get('purchasedate', '')
            car = CarModel.objects.get(pk=int(request.POST.get('car')))
            review['car_make'] = car.make.name
            review['car_model'] = car.name
            review['car_year'] = int(car.year.strftime("%Y"))
        json_payload = {'review': review}
        post_request(REVIEWS_URL, json_payload)
        return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
