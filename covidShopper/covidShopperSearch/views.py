from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import operator
import math
import requests
from bs4 import BeautifulSoup
import json

zones = {
    "Abbottsfield": "5243721",
    "Bonnie Doon": "5243861",
    "Castle Downs": "5243897",
    "Duggan": "5243926",
    "Eastwood": "5243951",
    "Jasper Place": "5244007",
    "Millwoods South & East": "5244033",
    "Millwoods West": "5244060",
    "Northeast": "5244072",
    "Northgate": "5244081",
    "Rutherford": "5244099",
    "Twin Brooks": "5244182",
    "West Jasper Place": "5244220",
    "Woodcroft East": "5244234",
    "Woodcroft West": "5244257",
    "Beaumont": "5243826",
    "Fort Saskatchewan": "5243979",
    "Leduc & Devon": "5244025",
    "St. Albert": "5244138",
    "Sherwood Park": "5244126",
    "Stony Plain & Spruce Grove": "5244164"}

runonceFlag = True

allZones = None


def get_latest_zone_data(zone_name, zone_url):
    url = "https://flo.uri.sh/visualisation/" + zone_url + "/embed"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    data = soup.find_all('script')[-1].string.strip()

    # initialize indicies to slice JSON data
    end = -(len(data) - data.rfind("}]};") - 1)
    start = end

    # find start index
    while data[start] != '{':
        start -= 1

    # slice data
    res = data[start:end]

    # convert to JSON from string
    json_obj = json.loads(res)
    json_obj["zone_name"] = zone_name

    # update infection rate to json obj
    updated_data = find_infection_rate(zone_name, json_obj)
    # print(updated_data)
    return updated_data

def find_infection_rate(zone_name, data_set):

    actives = data_set["value"][2]
    new_data = {}
    new_data["zone_name"] = zone_name
    new_data["active_cases"] = actives

    #predefined name of neighbourhoods in Edmonton zone and their total populations
    area_pops = {"Abbottsfield" : 14540, "Bonnie Doon": 96574, "Castle Downs": 70526, "Duggan": 40428,
            "Eastwood": 72600, "Jasper Place": 47069, "Millwoods South & East":82983, "Millwoods West": 51122,
            "Northeast": 88901, "Northgate": 82404, "Rutherford": 104153, "Twin Brooks": 75685, "West Jasper Place": 101046,
            "Woodcroft East": 60381, "Woodcroft West": 32479, "Beaumont": 25073, "Fort Saskatchewan": 26486,
            "Leduc & Devon": 42154, "St. Albert": 68912, "Sherwood Park": 81454, "Stony Plain & Spruce Grove": 57274}

    #find the number of current actives in the given area and divide by its pop to find infection rate
    infection_rate = int(actives)/area_pops[zone_name]
    new_data["infection_rate"] = infection_rate*100

    return new_data



def get_data():
    global zones

    all_zones = {}

    # find latest data for all zones in Edmonton
    for zone_name in list(zones.keys()):
        print("Loading", zone_name, "...")
        latest_data = get_latest_zone_data(zone_name, zones[zone_name])
        all_zones[zone_name] = latest_data

    return all_zones


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
    global zones, runonceFlag, allZones

    locations = []

    if(runonceFlag):
        allZones = get_data()
        runonceFlag = False

    f = CommentForm(auto_id=False)

    context = {
        'form': f,
    }

    f = CommentForm(request.POST)

    if f.is_valid():
        startLatLon = f.cleaned_data["startLatLon"].split(";")
        priorityBias = f.cleaned_data["priorityBias"]
        lats = f.cleaned_data["lats"].split(";")
        lons = f.cleaned_data["lons"].split(";")
        names = f.cleaned_data["names"].split(";")
        addrs = f.cleaned_data["addrs"].split(";")

        for i in range(len(lats)-1):
            # 111km in every degree of lon/lat
            euclidDistToStart = round(111 * math.sqrt(((float(startLatLon[0]) - float(lats[i]))**2 + (float(startLatLon[1]) - float(lons[i]))**2)), 4)

            # Determine COVID Zone (Ramy)
            CovidScore = 1

            overallScore = ( float(priorityBias) * euclidDistToStart )  -  ( (100.0 - float(priorityBias)) * float(CovidScore) )

            myLoc = Location(float(lats[i]), lons[i], names[i], addrs[i], euclidDistToStart, CovidScore, overallScore)

            locations.append(myLoc)

        # Sort our garbage
        locations.sort(key=operator.attrgetter('score'))

        # Double check to make sure we are sorting lowest first, since lower => better

        context2 = {
            'locations': locations,
            'form': f,
        }

        return render(request, "home/cards.html", context2)


    return render(request, "home/home.html", context)
