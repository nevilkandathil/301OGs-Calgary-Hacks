from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import operator

class Location():
    def __init__(self, lat, lon, name, addr, dist, covid, score):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.addr = addr
        self.dist = dist
        self.covid = covid
        self.score = score

class CommentForm(forms.Form):
    startLatLon = forms.CharField(widget=forms.TextInput(attrs={'id':'start_lat_lon'}))
    priorityBias = forms.CharField(widget=forms.TextInput(attrs={'id':'priority_bias'}))
    lats = forms.CharField(widget=forms.TextInput(attrs={'id':'lats'}))
    lons = forms.CharField(widget=forms.TextInput(attrs={'id':'lons'}))
    names = forms.CharField(widget=forms.TextInput(attrs={'id':'names'}))
    addrs = forms.CharField(widget=forms.TextInput(attrs={'id':'addrs'}))

def home(request):
    locations = []

    f = CommentForm(auto_id=False)


    f = CommentForm(request.POST)

    if f.is_valid():
        startLatLon = f.cleaned_data["startLatLon"].split(";")
        priorityBias = f.cleaned_data["priorityBias"]
        lats = f.cleaned_data["lats"].split(";")
        lons = f.cleaned_data["lons"].split(";")
        names = f.cleaned_data["names"].split(";")
        addrs = f.cleaned_data["addrs"].split(";")

        for i in range(len(lats)-1):
            euclidDistToStart = (float(startLatLon[0]) - float(lats[i]))**2 + (float(startLatLon[1]) - float(lons[i]))**2

            # Determine COVID Zone (Ramy)
            CovidScore = 1

            overallScore = ( float(priorityBias) * euclidDistToStart )  -  ( (100.0 - float(priorityBias)) * float(CovidScore) )

            myLoc = Location(float(lats[i]), lons[i], names[i], addrs[i], euclidDistToStart, CovidScore, overallScore)

            locations.append(myLoc)

        # Sort our garbage
        locations.sort(key=operator.attrgetter('score'))

        # Double check to make sure we are sorting lowest first, since lower => better


    context = {
        'locations': locations,
        'form': f,
    }

    return render(request, "home/home.html", context)
