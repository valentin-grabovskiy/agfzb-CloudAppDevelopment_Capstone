import requests
import json
from requests.auth import HTTPBasicAuth

from .models import CarDealer, DealerReview


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        response = requests.get(
            url,
            headers={'Accept': 'application/json'},
            params=kwargs
        )
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def post_request(url, json_payload, api_key = '', **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        if api_key:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                auth=HTTPBasicAuth('apikey', api_key),
                json=json_payload,
                params=kwargs
            )
        else:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json=json_payload,
                params=kwargs
            )
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, **kwargs)
    if json_result:
        dealers = json_result["dealerships"]
        for dealer_doc in dealers:
            dealer_obj = CarDealer(
                id=dealer_doc.get("id"),
                city=dealer_doc.get("city"),
                state=dealer_doc.get("state"),
                st=dealer_doc.get("st"),
                address=dealer_doc.get("address"),
                zip=dealer_doc.get("zip"),
                lat=dealer_doc.get("lat"),
                long=dealer_doc.get("long"),
                short_name=dealer_doc.get("short_name"),
                full_name=dealer_doc.get("full_name")
            )
            results.append(dealer_obj)
    return results


def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, **kwargs)
    if json_result:
        reviews = json_result["reviews"]
        for review_doc in reviews:
            review = review_doc.get("review")
            sentiment = analyze_review_sentiments(review)
            review_obj = DealerReview(
                id=review_doc.get("id"),
                name=review_doc.get("name"),
                dealership=review_doc.get("dealership"),
                review=review,
                purchase=review_doc.get("purchase"),
                purchase_date=review_doc.get("purchase_date"),
                car_make=review_doc.get("car_make"),
                car_model=review_doc.get("car_model"),
                car_year=review_doc.get("car_year"),
                sentiment=sentiment
            )
            results.append(review_obj)
    return results


def analyze_review_sentiments(text):
    params = {
        'text': text,
        'features': {'sentiment': {}},
        'language': 'en'
    }
    json_result = post_request(
        'https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/b8867f0a-3a80-490c-9664-2abecfcb63c9/v1/analyze?version=2022-04-07',
        params,
        'cfUHqZY8794TpX0s_ksmaZYaYLunoMsrLbmPUw-wWqUI'
    )
    if json_result and 'sentiment' in json_result:
        return json_result["sentiment"]["document"]["label"]
    return 'neutral'
