import amadeus
import json
import pandas as pd
import datetime
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

def get_next_segment_id():
    if Segment.objects.order_by('-id').first() == None:
        return 1
    else:
        return Segment.objects.order_by('-id').first().id + 1

def get_next_flight_id():
    if Flight.objects.order_by('-id').first() == None:
        return 1
    else:
        return Flight.objects.order_by('-id').first().id + 1
    
def amadeus_flight_offer_search(o_place,d_place,flight_date,adults,req_type,link):  
    try:
        flight_offers_search_response = amaclient.shopping.flight_offers_search.get(
            originLocationCode=o_place,
            destinationLocationCode=d_place,
            departureDate=flight_date,
            adults=adults)
        json_flight_offers_search = json.loads(flight_offers_search_response.body)
        print(json_flight_offers_search)
        return json_flight_offers_search
    except amadeus.ResponseError as error:
        print(error)
        return -1

def get_flights(o_place,d_place,flight_date,adults,req_type):
    link = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={o_place}&destinationLocationCode={d_place}&departureDate={flight_date}&adults={adults}_{req_type}"
    print(link)
    
    json_flight_offers_search = amadeus_flight_offer_search(o_place,d_place,flight_date,adults,req_type,link)
    if json_flight_offers_search == -1:
        return -1
    flights = []
    
    for raw_flight in json_flight_offers_search['data']:
        flight_id = get_next_flight_id()
        loc_segments = []
        id_segments = []
        for seg in raw_flight['itineraries'][0]['segments']:
            current_id=get_next_segment_id()
            operating_cxr = ""
            raw_arr =  str(seg['arrival']['at'])
            raw_dep =  str(seg['departure']['at'])
            try:
                operating_cxr = seg['operating']['carrierCode']
            except:
                operating_cxr = seg['carrierCode']
                pass
            
            plane_str = seg['aircraft']['code'].replace(' ','')
            plane = json_flight_offers_search['dictionaries']['aircraft'][plane_str]
            cxr_str = seg['carrierCode'].replace(' ','')
            cxr = json_flight_offers_search['dictionaries']['carriers'][cxr_str]
            op_cxr = json_flight_offers_search['dictionaries']['carriers'][operating_cxr]
            segment = Segment(
                link =link,
                id = current_id,
                departure = Place.objects.get(code=seg['departure']['iataCode']),
                arrival = Place.objects.get(code=seg['arrival']['iataCode']),
                arrival_date =raw_arr[:raw_arr.find('T')],
                departure_date =raw_dep[:raw_dep.find('T')],
                departure_time = raw_dep[raw_dep.find('T')+1:],
                arrival_time = raw_arr[raw_arr.find('T')+1:],
                mk_carrier_code = cxr,
                op_carrier_code = op_cxr,
                numberOfStops = seg['numberOfStops'],
                duration = seg['duration'],
                aircraft =plane
            )
            loc_segments.append(segment)
            id_segments.append(segment.id)
            for seg in loc_segments:
                seg.save()
                #Segment.objects.add(seg) 
        
        dep_str = f"""{getattr(loc_segments[0], 'departure_date')}T{getattr(loc_segments[0], 'departure_time')} """
        arr_str = f"""{getattr(loc_segments[-1], 'arrival_date')}T{getattr(loc_segments[-1], 'arrival_time')} """
        dep_ts = datetime.strptime(dep_str.replace(' ',''), "%Y-%m-%dT%H:%M:%S")
        arr_ts = datetime.strptime(arr_str.replace(' ',''), "%Y-%m-%dT%H:%M:%S")
        duration = pd.Timedelta(arr_ts-dep_ts)

        flight = Flight(
            id = flight_id,
            link=link,
            origin = getattr(loc_segments[0], 'departure'),
            destination = getattr(loc_segments[-1], 'arrival'),
            depart_time = getattr(loc_segments[0], 'departure_time'),
            departure_date = getattr(loc_segments[0], 'departure_date'),
            arrival_date = getattr(loc_segments[-1], 'arrival_date'),
            arrival_time =  getattr(loc_segments[-1], 'arrival_time'),
            plane = getattr(loc_segments[-1], 'aircraft'),
            airline = getattr(loc_segments[-1], 'mk_carrier_code'),
            price_grand_total = raw_flight['price']['grandTotal'],
            price_base= raw_flight['price']['base'],
            price_currency = raw_flight['price']['currency'],
            fare_type =raw_flight['pricingOptions']['fareType'][0], 
            duration =duration
        )
        
        flight.save()
        for seg_id in id_segments:
            flight.segments.add(seg_id)
        flights.append(flight)
    return flights
    

def request_flight(request):
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType')
    departdate = request.GET.get('DepartDate')
    adults = request.GET.get('countadults')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d")
    seat = request.GET.get('SeatClass')

    origin = Place.objects.get(code=o_place.upper())   ##
    destination = Place.objects.get(code=d_place.upper())  #
    
    return_date = None
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        return_date = datetime.strptime(returndate, "%Y-%m-%d")
        origin2 = Place.objects.get(code=d_place.upper())   ##
        destination2 = Place.objects.get(code=o_place.upper())  ##
        link_2 = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={d_place}&destinationLocationCode={o_place}&departureDate={returndate}&adults={adults}_2"
        flights2 = get_flights(d_place,o_place,returndate,adults,2)
        
    link_1 = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={o_place}&destinationLocationCode={d_place}&departureDate={departdate}&adults={adults}_1"
    
    
    flights = get_flights(o_place,d_place,departdate,adults,1)
    
    if trip_type == '2':
        return render(request, "flight/search2.html", {
            'flights': Flight.objects.filter(link=link_1),
            'origin': origin,
            'destination': destination,
            'flights2': Flight.objects.filter(link=link_2),   ##
            'origin2': origin2,    ##
            'trip_type': trip_type,
            'destination2': destination2,    ##
            'seat': seat.capitalize(),
            'depart_date': depart_date,
            'return_date': return_date,
            # 'max_price': Flight.objects.filter(link=link+"_1").order_by('-price_grand_total').first().price_grand_total,
            # 'min_price': Flight.objects.filter(link=link+"_1").order_by('price_grand_total').first().price_grand_total,
            # 'max_price2':Flight.objects.filter(link=link+"_2").order_by('-price_grand_total').first().price_grand_total,    
            # 'min_price2': Flight.objects.filter(link=link+"_2").order_by('price_grand_total').first().price_grand_total    ##
        })
        return render(request, "flight/search2.html", {
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
        return render(request, "flight/search2.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(10000/100)*100,
            'min_price': math.floor(100/100)*100
        })


def request_flight_2(request):
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

    #flightday = Week.objects.get(number=depart_date.weekday())
    destination = Place.objects.get(code=d_place.upper())
    origin = Place.objects.get(code=o_place.upper())
    if seat == 'economy':
        flights = Flight.objects.filter(origin=origin,destination=destination).order_by('price_grand_total')
        try:
            max_price = flights.last().economy_fare
            min_price = flights.first().economy_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':    ##
            flights2 = Flight.objects.filter(origin=origin2,destination=destination2).order_by('price_grand_total')    ##
            try:
                max_price2 = flights2.last().economy_fare   ##
                min_price2 = flights2.first().economy_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##
                
    elif seat == 'business':
        flights = Flight.objects.filter(origin=origin,destination=destination).order_by('price_grand_total')
        try:
            max_price = flights.last().business_fare
            min_price = flights.first().business_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':    ##
            flights2 = Flight.objects.filter(origin=origin2,destination=destination2).order_by('price_grand_total')    ##
            try:
                max_price2 = flights2.last().business_fare   ##
                min_price2 = flights2.first().business_fare  ##
            except:
                max_price2 = 0  ##
                min_price2 = 0  ##

    elif seat == 'first':
        flights = Flight.objects.filter(origin=origin,destination=destination).order_by('price_grand_total')
        try:
            max_price = flights.last().first_fare
            min_price = flights.first().first_fare
        except:
            max_price = 0
            min_price = 0
            
        if trip_type == '2':    ##
            flights2 = Flight.objects.filter(origin=origin2,destination=destination2).order_by('price_grand_total')
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