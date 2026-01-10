from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
from .models import *
from django.db import connection
from .functions import *
from .query import *

# Create your views here.

def test(request):
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
        print(data)
        data = cursor.fetchall()
        print(data)

    return render(request, "index.html")


def index(request):

    all_trains = None
    error = ""

    if request.method == "POST":
        form = from_to_Form(request.POST)
        if form.is_valid():
            from_des = form.cleaned_data['From']
            to_des = form.cleaned_data['To']
            date = form.cleaned_data['Date']
            category = form.cleaned_data['Category']

            all_trains = get_trains(from_des,to_des,date,category)
        else:
            error = "enter right stations"
            
    else:
        form = from_to_Form()

    return render(request, "index.html",{"form":form,"all_trains":all_trains,"error":error})


def Booking(request,route_id=0,S_class="SL",category='NA'):
    print(route_id,S_class)
    if route_not_exit(route_id) or seats_not_exist(route_id,S_class):
        return render(request, "index.html")
    
    train_details = get_ticket_details(route_id,S_class,category)

    print(train_details)
    return render(request, "booking.html",{"info" : train_details})

def Payment(request,route_id=0,S_class="SL",category="NA"):
    if route_not_exit(route_id) or seats_not_exist(route_id,S_class):
        return render(request, "index.html")
    
    train_details = get_ticket_details(route_id,S_class,category)
    error = ""

    if request.method == "POST":
        form = user_Form(request.POST)
        if form.is_valid():
            print(form)
            print("form valid")

        else:
            print("invalid")
            error = "form invalid"
            
    else:
        form = user_Form()

    bill = get_bill(route_id,S_class,category)

    print(train_details)
    return render(request, "payment.html",{"info" : train_details,"form":form,"total":bill["total"],"error":error})

def Booking_status(request,route_id=0,S_class="SL",category="NA"):
    if route_not_exit(route_id) or seats_not_exist(route_id,S_class):
        return render(request, "index.html")
    
    train_details = get_ticket_details(route_id,S_class)
    booking_details = {}
    error = ""

    if request.method == "POST":
        form = user_Form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            booking_details["details"] = confirm_booking(data,route_id,S_class,category)
            print("done")
        else:
            print("invalid")
            booking_details["status"] = "Booking Failed"
            return Payment(request,route_id,S_class)
    else:
        return render(request, "index.html")
    
    train_details = get_ticket_details(route_id,S_class)
    booking_details["cat"] = category

    print(train_details)
    return render(request, "booking_status.html",{"info" : train_details,"details":booking_details})


def Cancel_booking(request):
    error = ""

    if request.method == "POST":
        form = cancelation_form(request.POST)
        if form.is_valid():
            PNR = form.cleaned_data["PNR"]
            cancellation_status = cancel_booking(PNR)
            if(cancellation_status):
                error = "cancellation was successful. \n Amount had been refunded"
            else:
                error = "cancellation not successful"
        else:
            error = "enter right PNR"
            
    else:
        form = cancelation_form()

    return render(request, "cancellation.html",{"form":form,"error":error})

def pnr_status(request):
    error = ""
    train_details = []
    booking_details = {}

    if request.method == "POST":
        form = cancelation_form(request.POST)
        if form.is_valid():
            PNR = form.cleaned_data["PNR"]
            if(pnr_exist(PNR)):
                route_id = get_routid_pnr(PNR)
                train_details = get_ticket_details(route_id)
                booking_details = get_booking_details(PNR)
                booking_details["user"] = get_user_pnr(PNR)
                print(train_details,booking_details)
                return render(request, "pnr_status.html",{"info" : train_details,"details":booking_details})
            else:
                error = "enter rigth PNR"
        else:
            error = "enter right PNR"
    else:
        form = cancelation_form() 

    print(train_details)
    return render(request, "cancellation.html",{"form":form,"error":error})

def train_schedule_lookup(request):
    train = None
    error = ""

    if request.method == "POST":
        form = train_form(request.POST)
        if form.is_valid():
            train_id = form.cleaned_data["Train_No"]
            date = form.cleaned_data["Date"]
            train = get_train(train_id,date)
        else:
            error = "enter right stations"
            
    else:
        form = train_form()

    return render(request, "schedule.html",{"form":form,"all_trains":train,"error":error})

def passenger_lookup(request):
    details = None
    wl_passengers = None
    error = ""

    if request.method == "POST":
        form = train_form(request.POST)
        if form.is_valid():
            train_id = form.cleaned_data["Train_No"]
            date = form.cleaned_data["Date"]
            details = get_passengers(train_id,date)
            wl_passengers = get_wl_passengers(train_id,date)
            if(len(wl_passengers)==0):
                wl_passengers = None
        else:
            error = "enter right stations"
    else:
        form = train_form()

    print(details)
    

    return render(request, "passengers.html",{"form":form,"details":details,"error":error,"wl":wl_passengers})

def total_refund(request):
    details = None
    error = ""

    if request.method == "POST":
        form = route_form(request.POST)
        if form.is_valid():
            route_id = form.cleaned_data["Route_id"]
            if not route_not_exit(route_id):
                details = get_refund_amount(route_id)[0]
            else:
                error = "enter right Route id"
        else:
            error = "enter right Route id"
    else:
        form = route_form()

    print(details)

    return render(request, "route.html",{"form":form,"details":details,"error":error})

def stats(request):
    details = {}
    revenue = None
    error = ""

    if request.method == "POST":
        form = revenue_form(request.POST)
        if form.is_valid():
            From_Date = form.cleaned_data["From_Date"]
            To_Date = form.cleaned_data["To_Date"]
            revenue = get_revenue(From_Date,To_Date)
           
        else:
            error = "enter right Route id"
    else:
        form = revenue_form()

    details["refund"] = get_refunded_list()
    details["busy"] = get_busiest_route()

    print(details)

    return render(request, "stats.html",{"form":form,"details":details,"revenue":revenue,"error":error})

def admin(request):
    return render(request, "admin.html")


