import amadeus
import json
from flight.src.amaclient.client import amaclient
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
#from django.urls import reverse
#from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from django.contrib.auth import authenticate, login, logout

from datetime import datetime
import math
from ...models import *

#from capstone.utils import render_to_pdf, createticket

#Fee and Surcharge variable
FEE = 100.0
#from flight.utils import createWeekDays, addPlaces, addDomesticFlights, addInternationalFlights



def request_flight_2(request):
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType')
    departdate = request.GET.get('DepartDate')
    adults = request.GET.get('countadults')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d")
    return_date = None
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        return_date = datetime.strptime(returndate, "%Y-%m-%d")
        origin2 = Place.objects.get(code=d_place.upper())   ##
        destination2 = Place.objects.get(code=o_place.upper())  ##
    seat = request.GET.get('SeatClass')

    # flightday = Week.objects.get(number=depart_date.weekday())
    # destination = Place.objects.get(code=d_place.upper())
    # origin = Place.objects.get(code=o_place.upper())
        
    try:
        flight_offers_search_response = amaclient.shopping.flight_offers_search.get(
            originLocationCode=o_place,
            destinationLocationCode=d_place,
            departureDate=departdate,
            adults=adults)
        json_flight_offers_search = json.loads(flight_offers_search_response.body)
        print(json_flight_offers_search)
    except amadeus.ResponseError as error:
        print(error)
    #link = json_flight_offers_search['links']['self']
    flights = []
    #if len(Segment.objec)
    for raw_flight in json_flight_offers_search['data']:
        loc_segments = []
        for seg in raw_flight['itineraries'][0]['segments']:
            operating_cxr = ""
            raw_arr =  str(seg['arrival']['at'])
            raw_dep =  str(seg['departure']['at'])
            try:
                operating_cxr = seg['operating']['carrierCode']
            except:
                pass
            
            segment = Segment(
                departure = Place.objects.get(code=seg['departure']['iataCode']),
                arrival = Place.objects.get(code=seg['arrival']['iataCode']),
                arrival_date =raw_arr[:raw_arr.find('T')],
                departure_date =raw_dep[:raw_dep.find('T')],
                departure_time = raw_dep[raw_dep.find('T')+1:],
                arrival_time = raw_arr[raw_arr.find('T')+1:],
                mk_carrier_code = seg['carrierCode'],
                op_carrier_code = operating_cxr,
                numberOfStops = seg['numberOfStops'],
                duration = seg['duration'],
                #aircraft = raw_flight['dictionaries']['aircraft'][seg['aircraft']]
                aircraft = seg['aircraft']
                
            )
            loc_segments.append(segment)
            Segment.objects.bulk_create(loc_segments)
        flight = Flight(
            origin = getattr(loc_segments[0], 'departure'),
            destination = getattr(loc_segments[0], 'arrival')
        )
        for ss in loc_segments:
            flight.segments.add(ss)
    

def request_flight(request):
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType')
    departdate = request.GET.get('DepartDate')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d")
    return_date = None
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        return_date = datetime.strptime(returndate, "%Y-%m-%d")
        flightday2 = Week.objects.get(number=return_date.weekday()) ##
        origin2 = Place.objects.get(code=d_place.upper())   ##
        destination2 = Place.objects.get(code=o_place.upper())  ##
    seat = request.GET.get('SeatClass')

    flightday = Week.objects.get(number=depart_date.weekday())
    destination = Place.objects.get(code=d_place.upper())
    origin = Place.objects.get(code=o_place.upper())
    if seat == 'economy':
        flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(economy_fare=0).order_by('economy_fare')
        try:
            max_price = flights.last().economy_fare
            min_price = flights.first().economy_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':    ##
            flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(economy_fare=0).order_by('economy_fare')    ##
            try:
                max_price2 = flights2.last().economy_fare   ##
                min_price2 = flights2.first().economy_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##
                
    elif seat == 'business':
        flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(business_fare=0).order_by('business_fare')
        try:
            max_price = flights.last().business_fare
            min_price = flights.first().business_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':    ##
            flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(business_fare=0).order_by('business_fare')    ##
            try:
                max_price2 = flights2.last().business_fare   ##
                min_price2 = flights2.first().business_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##

    elif seat == 'first':
        flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(first_fare=0).order_by('first_fare')
        try:
            max_price = flights.last().first_fare
            min_price = flights.first().first_fare
        except:
            max_price = 0
            min_price = 0
            
        if trip_type == '2':    ##
            flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(first_fare=0).order_by('first_fare')
            try:
                max_price2 = flights2.last().first_fare   ##
                min_price2 = flights2.first().first_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##    ##

    #print(calendar.day_name[depart_date.weekday()])
    if trip_type == '2':
        return render(request, "flight/search.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'flights2': flights2,   ##
            'origin2': origin2,    ##
            'destination2': destination2,    ##
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price/100)*100,
            'min_price': math.floor(min_price/100)*100,
            'max_price2': math.ceil(max_price2/100)*100,    ##
            'min_price2': math.floor(min_price2/100)*100    ##
        })
    else:
        return render(request, "flight/search.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price/100)*100,
            'min_price': math.floor(min_price/100)*100
        })