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
    print(updated_data)
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
        latest_data = get_latest_zone_data(zone_name, zones[zone_name])
        all_zones[zone_name] = latest_data

    return all_zones

print(get_data())

