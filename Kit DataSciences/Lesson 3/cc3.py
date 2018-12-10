from bs4 import BeautifulSoup
from urllib.request import urlopen

import requests

url = "https://www.insee.fr/fr/statistiques/1906659?sommaire=1906743"

# Making the soup

def soup(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    soup.get_text()
    return soup

soup = soup(url)

def get_top50_city():
    topcity = []
    for i in range(1,100, 2):
        city = soup.find_all('th', attrs = {'class':'ligne'})[i].get_text(strip=True)
        topcity.append(city)
    return topcity

cities = get_top50_city()

def distance_cities_fr_list():
    distancecities = []
    for i in range(0,49):
        r = requests.get("https://fr.distance24.org/route.json?stops=" + cities[i] + "|" + cities[i+1])
        get_json = r.json()
        distance = get_json['distance']
        distancecities.append(distance)
    return distancecities

results = distance_cities_fr_list()
print(results)
