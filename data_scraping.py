import urllib3
import csv
from bs4 import BeautifulSoup
import os
import re

hours = 24
http = urllib3.PoolManager()

if os.path.exists('./data.csv'):
    file = open('./data.csv', 'a')
else:
    file = open('./data.csv', 'w')

writer = csv.writer(file)
if file.mode == 'w':
    writer.writerow(['Postaja', 'Vjetar smjer', 'Vjetar brzina (m/s)', 'Temperatura zraka (°C)', 'Relativna vlažnost (%)', 'Tlak zraka (hPa)', 'Tendencija tlaka (hPa/3h)', 'Stanje vremena'])

for i in range(hours):
    url = 'https://meteo.hr/podaci.php?section=podaci_vrijeme&param=hrvatska_n&sat='
    if i < 10:
        url += '0'
    url += str(i) + '&prikaz=abc'
    response = http.request('GET', url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36' })
    soup = BeautifulSoup(response.data, 'html5lib')
    rows = soup.find_all('tbody')[1].find_all('tr', recursive=False)

    for row in rows:
        all_table_rows = row.find_all('td')
        postaja = all_table_rows[0].text.strip()
        vjetar_smjer = all_table_rows[1].find_all('span')[0].text.strip()
        vjetar_brzina = all_table_rows[1].find_all('span')[1].text.strip()
        temperatura_zraka = all_table_rows[2].text.strip()
        relativna_vlaznost = all_table_rows[3].text.strip()
        tlak_zraka = all_table_rows[4].text.strip()
        tendencija_tlaka = all_table_rows[5].text.strip()
        stanje_vremena = all_table_rows[6].text.strip()

        writer.writerow([postaja, vjetar_smjer, vjetar_brzina, temperatura_zraka, relativna_vlaznost, tlak_zraka, tendencija_tlaka, stanje_vremena])

file.close()