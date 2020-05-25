import csv
from geopy.geocoders import Nominatim
import pandas as pd
import numpy as np

def getDistance(lat1, lng1, lat2, lng2):
    r = 6371
    dlat = np.deg2rad(lat2-lat1)
    dlng = np.deg2rad(lng2-lng1)

    a = np.sin(dlat/2) * np.sin(dlat/2) + \
        np.cos(np.deg2rad(lat1)) * np.cos(np.deg2rad(lat2)) * \
        np.sin(dlng/2) * np.sin(dlng/2)

    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = r * c
    return d

towns = ['Omisalj', 'Matulji', 'Medveja', 'Lovran', 'Lipa', 'Krasica', 'Klenovica', 'Kastav', 'Klana', 'Grobnik', 'Hreljin', 'Fuzine', 'Drazice',
         'Delnice', 'Crikvenica', 'Bribir', 'Brgud', 'Bakar', 'Bakarac', 'Baska', 'Rubesi', 'Rijeka', 'Opatija', 'Jadranovo', 'Vrata',
         'Selce', 'Veprinac']
geolocator = Nominatim(user_agent='DetectionOfSignificantMicroclimatesFromMeterologicalAndGeographicalData')

file = open('./geolocation.csv', 'w')
writer = csv.writer(file)
writer.writerow(['Town', 'Lat', 'Lng'])
for town in towns:
    if town.lower() == 'lipa':
        location = geolocator.geocode(town + ' Matulji, Hrvatska')
    elif town.lower() == 'krasica':
        location = geolocator.geocode(town + ' Bakar, Hrvatska')
    else:
        location = geolocator.geocode(town + ', Hrvatska')
    writer.writerow([town.lower(), location.latitude, location.longitude])

file.close()

file = open('./distance.csv', 'w')
writer = csv.writer(file)
writer.writerow(['Town1', 'Town2', 'Distance'])
data = pd.read_csv('./geolocation.csv')

for ind1 in data.index:
    for ind2 in data.index:
        if ind1 == ind2:
            continue
        dist = getDistance(data['Lat'][ind1], data['Lng'][ind1], data['Lat'][ind2], data['Lng'][ind2])
        writer.writerow([data['Town'][ind1], data['Town'][ind2], dist])

file.close()