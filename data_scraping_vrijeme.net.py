import urllib3
import csv
from bs4 import BeautifulSoup
import os
import re

towns = ['Omisalj', 'Matulji', 'Medveja', 'Lovran', 'Lipa', 'Krasica', 'Klenovica', 'Kastav', 'Klana', 'Grobnik', 'Hreljin', 'Fuzine', 'Drazice',
         'Delnice', 'Crikvenica', 'Bribir', 'Brgud', 'Bakar', 'Bakarac', 'Baska', 'Rubesi', 'Rijeka', 'Opatija', 'Jadranovo', 'Vrata',
         'Selce', 'Veprinac']
http = urllib3.PoolManager()

if os.path.exists('./data_pgz.csv'):
    file = open('./data_pgz.csv', 'a')
else:
    file = open('./data_pgz.csv', 'w')

writer = csv.writer(file)
if file.mode == 'w':
    writer.writerow(['Town', 'Date', 'Collected_at', 'Temperature', 'Humidity', 'Pressure', 'Biostatus', 'Wind', 'Sunrise', 'Sunset', 'Weather', 'Real_feel'])

for town in towns:
    url = 'http://www.vrijeme.net/hrvatska/' + town.lower()
    response = http.request('GET', url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36' })
    soup = BeautifulSoup(response.data, 'html5lib')

    date = soup.find('span', class_='title').text.strip()[-11:]
    temp = soup.find('li', class_='temp').find('span', class_='val').text.strip()[:-1]
    humidity = soup.find('li', class_='humidity').find('span', class_='val').text.strip()[:-1]
    pressure = soup.find('li', class_='pressure').find('span', class_='val').text.strip()[:-4]
    biostatus = soup.find('li', class_='biostatus').find('span', class_='icon-biostatus').text.strip()
    wind = soup.find('li', class_='wind').find('span', class_='val').text.strip()
    sunrise = soup.find('li', class_='sunrise').find('span', class_='val').text.strip()
    sunset = soup.find('li', class_='sunset').find('span', class_='val').text.strip()
    weather = soup.find('li', class_='visual').find('span', class_='icon-weather').text.strip()
    real_feel = soup.find('span', class_='real-feel').find('span', class_='real-feel-temp').text.strip()[:-1]
    collected_at = soup.find('span', class_='updated').find('time').text.strip()[:-1]

    writer.writerow([town.lower(), date, collected_at, temp, humidity, pressure, biostatus, wind, sunrise, sunset, weather, real_feel])

file.close()