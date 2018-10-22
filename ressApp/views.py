from .models import Offer, Address, User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import OfferForm, AddressForm, SignUpForm, ProfileForm, ChangeUserForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login, authenticate
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta


'''
---------------------------------- Views für Angebote (Offer) ----------------------------------
'''


def index(request):
    """
    Gibt alle Angebote mit einer bestimmten Sortierung / Filterung zurück

    authors: Simon Hoffmann
    """
    if request.method == 'GET':
        if 'deletefilter' in request.GET:
            #zurücksetzen der Filter
            clear_filter(request)
            offer_list = Offer.objects.all()
            context = {'offer_list': offer_list, 'categories': get_active_categories(offer_list),
                       'cart_size': get_cart_size(request), 'cart': get_cart(request)}
        else:
            offer_list = Offer.objects.all()
            #speichert filter in session
            handle_filter(request)
            #anwenden der gesetzten filter
            offer_list = apply_filter(request)
            context = {'offer_list': offer_list, 'categories': get_active_categories(offer_list),
                       'cart_size': get_cart_size(request), 'cart': get_cart(request)}
    else:
        #Alle Angebote zurückliefern
        clear_filter(request)
        offer_list = Offer.objects.all()
        context = {'offer_list': offer_list, 'categories': get_active_categories(offer_list), 'cart_size': get_cart_size(request), 'cart': get_cart(request)}
    return render(request, 'ressApp/index.html', context)


def detail(request, offer_id):
    """
    View für die Darstellung der Details eines Angebots

    authors: Simon Hoffmann
    """
    clear_filter(request)
    offer = get_object_or_404(Offer, pk=offer_id)
    #Angebote durch matchmaking bekommen
    offers = matchmaking(request, offer)
    return render(request, 'ressApp/detail.html', {'offer': offer, 'offers':offers,'cart': get_cart(request), 'cart_size': get_cart_size(request)})


def newoffer(request):
    """
    View um ein neues Angebot einstellen zu können

    authors: Simon Hoffmann
    """
    template = 'ressApp/newoffer.html'
    if request.method == 'POST':
        offerForm = OfferForm(request.POST, request.FILES)
        addressForm = AddressForm(request.POST)
        if offerForm.is_valid() & addressForm.is_valid():
            return saveoffertodb(offerForm, addressForm, request, -1)
        else:
            context = {'offerForm': offerForm, 'addressForm': addressForm, 'cart_size': get_cart_size(request)}
            return render(request, template, context)

    else:
        offerForm = OfferForm
        addressForm = AddressForm
        context = {'offerForm': offerForm, 'addressForm': addressForm, 'cart_size': get_cart_size(request)}
        return render(request, template, context)

def changeoffer(request, offer_id):
    """
    View um ein Angebot zu ändern

    authors: Simon Hoffmann, David Hartmann
    """
    template = 'ressApp/changeoffer.html'
    if request.method == 'POST':
        offerForm = OfferForm(request.POST, request.FILES)
        addressForm = AddressForm(request.POST)
        if offerForm.is_valid() & addressForm.is_valid():
            return saveoffertodb(offerForm, addressForm, request,offer_id)

        else:
            context = {'offerForm': offerForm, 'addressForm': addressForm, 'cart_size': get_cart_size(request)}
            return render(request, template, context)

    else:
        if request.method == 'GET' and 'delteOffer' in request.GET:
            Offer.objects.get(pk=offer_id).delete()
            clear_filter(request)
            return redirect("/ressApp/account/")
        else:
            offer = Offer.objects.get(pk=offer_id)
            offerForm = OfferForm(instance=offer)
            addressForm = AddressForm(instance=offer.offerAdress)
            context = {'offerForm': offerForm, 'addressForm': addressForm, 'offer_id': offer_id, 'cart_size': get_cart_size(request)}
            return render(request, template, context)


def providerpage(request):
    """
    View für die Darestellung der Anbieterseite

    authors: Simon Hoffmann
    """
    profile_id = request.GET.get('profile_id')
    user = get_object_or_404(User, pk=profile_id)
    offers = user.offer_set.all()
    userprofile = user.profile
    template = 'ressApp/providerpage.html'
    context = {'userprofile': userprofile, 'offers': offers, 'cart_size': get_cart_size(request)}
    return render(request, template, context)


def cart(request):
    """
    View für die Darstellung des Warenkorbs

    authors: David Hartmann
    """
    offers_in_cart = []
    if 'cart' in request.session:
        offers_in_cart = Offer.objects.filter(id__in=request.session["cart"])
    context = {"cart_contents": offers_in_cart, 'cart_size': len(offers_in_cart)}
    return render(request, 'ressApp/cart.html', context)


def add_to_cart(request, offer_id):
    """
    Support-View um das Angebot in den Warenkorb zu schieben

    authors: David Hartmann
    """
    if 'cart' not in request.session:
        request.session["cart"] = []
    request.session["cart"].append(offer_id)
    request.session.modified = True
    return redirect("cart")


def remove_from_cart(request, offer_id):
    """
    Support-View um das Angebot aus dem Warenkorb zu löschen

    authors: Julian Sears, Simon Hoffmann
    """
    if 'cart' not in request.session:
        request.session["cart"] = []
    request.session["cart"].remove(offer_id)
    request.session.modified = True
    return redirect("cart")

'''
---------------------------------- Views für Benutzer (Account) ----------------------------------
'''


@login_required(login_url="login")
def account(request):
    """
    View für die Accountdarstellung

    authors: David Hartmann
    """
    return render(request, 'ressApp/account.html', {'cart_size': get_cart_size(request)})



@login_required(login_url="login")
def changeaccount(request):
    """
    View für die Änderungen an den Account-Daten

    authors: David Hartmann, Simon Hoffmann
    """
    user = request.user
    template = 'ressApp/changeaccount.html'
    if request.method == 'POST':
        profileform = ProfileForm(request.POST, request.FILES )
        addressform = AddressForm(request.POST)
        userform = ChangeUserForm(request.POST, instance=user)
        if profileform.is_valid() & addressform.is_valid() & userform.is_valid():
            return saveaccountodb(profileform, userform, addressform, user)
        else:
            context = {'addressform': addressform, 'profileform': profileform, 'userform': userform,'cart_size': get_cart_size(request)}
            return render(request, template, context)
    else:
        addressform = AddressForm(instance=user.profile.address)
        profileform = ProfileForm(instance=user.profile)
        userform = ChangeUserForm(instance=user)
        context = {'addressform': addressform, 'profileform': profileform,'userform': userform,'cart_size': get_cart_size(request)}
        return render(request, template, context)


@login_required(login_url="login")
def change_password(request):
    """
    View um das Passwort zu ändern

    authors: David Hartmann
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('/ressApp/account/')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ressApp/change_password.html', {'form': form})


def signup(request):
    """
    View um sich als Anbieter auf der Seite zu registieren

    authors: David Hartmann
    """
    template = "ressApp/signup.html"
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.email = form.cleaned_data.get("email")
            user.profile.einrichtungsname = form.cleaned_data.get("einrichtungsname")
            user.profile.phone = form.cleaned_data.get("phone")
            user.profile.image = form.cleaned_data.get("image")

            street = form.cleaned_data.get('street')
            house_number = form.cleaned_data.get('house_number')
            additional_info = form.cleaned_data.get('additional_info')
            city = form.cleaned_data.get('city')
            postcode = form.cleaned_data.get('postcode')

            address = Address(street=street, house_number=house_number, additional_info=additional_info,
                              city=city, postcode=postcode)
            address.save()

            gps = addresstolocation(str(address.city) + " " + str(address.street)+ " " +str(address.house_number))
            if gps != None:
                address.latitude = gps[0]
                address.longitude = gps[1]
            address.save()

            user.profile.address = address
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('/ressApp/account/')
        else:
            context = {'form': form,'cart_size': get_cart_size(request)}
            return render(request, template, context)
    else:
        form = SignUpForm()
    return render(request, template , {"form": form, 'cart_size': get_cart_size(request)})


'''
----------------------------------------------------------------------------------------------------------------
'''



'''
---------------------------------- Support Methoden für die Views ----------------------------------
'''


def saveoffertodb(offerform, addressform, request, offer_id):
    """
    Speichert die Daten aus den Angebot-Forms in die Datenbank

    authors: Simon Hoffmann, David Hartmann
    """
    address = addressform.save()
    gps = addresstolocation(str(address.city) + " " + str(address.street) + " " + str(address.house_number))
    if gps != None:
        address.latitude = gps[0]
        address.longitude = gps[1]
    address.save()

    if offer_id >-1:
        offer_by_id = Offer.objects.get(pk=offer_id)
        offer_by_id.title = offerform.cleaned_data.get('title')
        offer_by_id.subtitle = offerform.cleaned_data.get('subtitle')
        offer_by_id.description= offerform.cleaned_data.get('description')
        offer_by_id.deposit= offerform.cleaned_data.get('deposit')
        offer_by_id.price= offerform.cleaned_data.get('price')
        offer_by_id.deposit= offerform.cleaned_data.get('deposit')
        offer_by_id.BlockedDays= offerform.cleaned_data.get('BlockedDays')
        offer_by_id.category = offerform.cleaned_data.get('category')
        offer_by_id.lend_or_gift = offerform.cleaned_data.get('lend_or_gift')
        offer_by_id.offerAdress= address
        offer_by_id.deposit= offerform.cleaned_data.get('deposit')
        if offer_by_id.image != offerform.cleaned_data.get('image') and offerform.cleaned_data.get('image') != "offer_image/no_offer_image.jpg":
            offer_by_id.image = offerform.cleaned_data.get('image')
        offer_by_id.save()
    else:
        offer = offerform.save()  # commit=False
        offer.offerAdress = address
        offer.owner = request.user
        offer.save()

    return redirect('/ressApp/account/')


def saveaccountodb(profileform, userform, addressform, user):
    """
    Speichert die Daten aus den Account-Forms in die Datenbank

    authors: Simon Hoffmann, David Hartmann
    """
    user.refresh_from_db()

    #create address
    address = addressform.save()
    gps = addresstolocation(str(address.city) + " " + str(address.street) + " " + str(address.house_number))
    if gps != None:
        address.latitude = gps[0]
        address.longitude = gps[1]
    address.save()

    #update user
    user.username = userform.cleaned_data.get('username')
    user.first_name = userform.cleaned_data.get('first_name')
    user.last_name = userform.cleaned_data.get('last_name')
    user.email = userform.cleaned_data.get("email")
    user.password = userform.cleaned_data.get("password")

    #update address
    user.profile.address = address

    #update profile
    user.profile.einrichtungsname = profileform.cleaned_data.get('einrichtungsname')
    user.profile.phone = profileform.cleaned_data.get("phone")
    if user.profile.image != profileform.cleaned_data.get("image") and profileform.cleaned_data.get("image") != "profile_image/no_profile_image.jpg":
        user.profile.image = profileform.cleaned_data.get("image")

    user.save()
    user.refresh_from_db()
    return redirect('/ressApp/account/')


def addresstolocation(addressstr):
    """
    Extrahiert die Breiten und Längengrade aus der Adresse

    authors: Simon Hoffmann
    :param addressstr: Die Straße der Adresse
    :return: Längen und Breitengerade
    """
    try:
        geolocator = Nominatim()
        location = geolocator.geocode(addressstr)
        return [location.latitude, location.longitude]
    except:
        return None


def get_cart(request):
    """
    Gibt die Angebote im Warenkorb zurück

    authors: David Hartmann
    """
    offers_in_cart = []
    if 'cart' in request.session:
        offers_in_cart = Offer.objects.filter(id__in=request.session["cart"])
    return offers_in_cart


def get_cart_size(request):
    """
    Gibt die Anzahl der Angebote im Warenkorb zurück

    authors: Julian Sears
    """
    offers_in_cart = []
    if 'cart' in request.session:
        offers_in_cart = Offer.objects.filter(id__in=request.session["cart"])
    return len(offers_in_cart)


def get_active_categories(offer_list):
    """
    Gibt alle genutzten Kategorien in 'Human-Readable-Form' zurück

    authors: Simon Hoffmann
    """
    category_list = []
    for offer in offer_list:
        if offer.get_category_display() not in category_list:
            category_list.append(offer.get_category_display())

    return category_list


def handle_filter(request):
    """
    Filter in session speichern

    authors: Simon Hoffmann
    """
    if 'filter_datum_von' not in request.session:
        request.session["filter_datum_von"] = ""
    if 'filter_datum_bis' not in request.session:
        request.session["filter_datum_bis"] = ""
    if 'filter_datum' not in request.session:
        request.session["filter_datum"] = ""
    if 'filter_typ' not in request.session:
        request.session["filter_typ"] = ""
    if 'filter_query' not in request.session:
        request.session["filter_query"] = ""
    if 'filter_category' not in request.session:
        request.session["filter_category"] = ""
    if 'filter_sorting' not in request.session:
        request.session["sorting"] = ""


    if request.GET.get('q') != None:
        request.session["filter_query"] = request.GET.get('q')

    for key in request.GET:
        # Spezialfälle für Filter
        value = request.GET[key]
        if key == "sorting":
            request.session["sorting"] = value
        else:
            request.session["filter_"+key] = value

    #Fehlerbehandlung für Datum
    if request.session["filter_datum"] != "":
        if request.session["filter_datum_von"] =="" or request.session["filter_datum_bis"] == "":
            clear_filter(request)
        else:
            if datetime.strptime(request.session["filter_datum_von"], '%d-%m-%Y') >  datetime.strptime(request.session["filter_datum_von"], '%d-%m-%Y'):
                clear_filter(request)
    request.session.modified = True

def clear_date_filter(request):
    request.session["filter_datum_bis"] = ""
    request.session["filter_datum"] = ""
    request.session["filter_datum_von"] = ""


def clear_filter(request):
    """
    Filter entfernen

    authors: Simon Hoffmann
    """
    request.session["filter_typ"] = ""
    request.session["filter_category"] = ""
    request.session["sorting"] = ""
    request.session["filter_query"] = ""
    request.session["filter_datum"] = ""
    request.session["filter_datum_von"] = ""
    request.session["sorting_datum_bis"] = ""



def apply_filter(request):
    """
    Filter anwenden

    authors:Simon Hoffmann
    """
    filtered_offers = []
    # wendet filter auf die Angebote an
    if request.session["sorting"] == "Preis absteigend":
        offer_list = Offer.objects.order_by('-price')
    elif request.session["sorting"] == "Preis aufsteigend":
        offer_list = Offer.objects.order_by('price')
    elif request.session["sorting"] == "Alphabetisch":
        offer_list = Offer.objects.order_by('title')
    elif request.session["sorting"] == "Alphabetisch":
        offer_list = Offer.objects.order_by('created_at')
    else:
        offer_list = Offer.objects.all()

    # Filter nach dem Suchtext, falls einer eingegeben wurde
    if request.session["filter_query"] != "":
        offer_list = offer_list.filter(Q(description__icontains=request.session["filter_query"]) | Q(
            title__icontains=request.session["filter_query"]) | Q(subtitle__icontains=request.session["filter_query"]))


    # Iteriert über die Angebote, um nach Kategory und
    for offer in offer_list:
        if request.session["filter_datum"] == "" or isavailable(offer,request.session["filter_datum_von"], request.session["filter_datum_bis"]):
            if request.session["filter_category"] != "" and request.session["filter_typ"] != "":
                if offer.get_lend_or_gift_display() == request.session["filter_typ"] and offer.get_category_display() == \
                        request.session["filter_category"]:
                    filtered_offers.append(offer)
            elif request.session["filter_category"] != "" and request.session["filter_typ"] == "":
                if offer.get_category_display() == request.session["filter_category"]:
                    filtered_offers.append(offer)
            elif request.session["filter_category"] == "" and request.session["filter_typ"] != "":
                if offer.get_lend_or_gift_display() == request.session["filter_typ"]:
                    filtered_offers.append(offer)
            else:
                filtered_offers.append(offer)

    return filtered_offers


def matchmaking(request, offer):
    """
    Matchmaking für passende weitere Angebote

    authors: Simon Hoffmann
    """
    offers = Offer.objects.filter(Q(category=offer.category) | Q(title__icontains=offer.title) | Q(subtitle__icontains=offer.subtitle)| Q(description__icontains=offer.title)).exclude(id=offer.id)
    return offers

def isavailable(offer, von, bis):

    """
    Angebote rausfiltern die in dem angegeben Zeitraum nicht verfügbar sind

    authors: Simon Hoffmann
    """
    if von =="" or bis == "":
        return true
    date_von = datetime.strptime(von, '%d-%m-%Y')
    date_bis = datetime.strptime(bis, '%d-%m-%Y')
    days_count = (date_bis - date_von).days
    date_list = [(date_von + timedelta(days=x)).weekday() for x in range(0, days_count + 1)]
    for d in offer.BlockedDays:
        for dl in date_list:
            if str(dl) == str(d):
                return False
    return True



def daystringtonumber(day):
    """
    Deutschen Wochentag zu Weekday Nummer

    authors: Simon Hoffmann
    """
    if day == 'Montag':
        return 0
    if day == 'Dienstag':
        return 1
    if day == 'Mittwoch':
        return 2
    if day == 'Donnerstag':
        return 3
    if day == 'Freitag':
        return 4
    if day == 'Samstag':
        return 5
    if day == 'Sonntag':
        return 6

'''
----------------------------------------------------------------------------------------------------------------
'''