import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

website_prefix = "https://www.lacentrale.fr"
website_url = website_prefix + "/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-IDF%2CFR-NAQ%2CFR-PAC&yearMin=2013&yearMax=2018.html"


def get_request_soup(request_url):
    request_result = requests.get(request_url)
    if request_result.status_code == 200:
        html_doc =  request_result.text
        soup = BeautifulSoup(html_doc,"html.parser")
        return soup

def get_all_car_links(page_url):
    res_links = []
    request_soup = get_request_soup(page_url)
    link_tags = request_soup.findAll("a", class_="linkAd ann")
    res_links = res_links + list(map(lambda x: website_prefix + x.attrs['href'], link_tags))
    return res_links

def get_info_argus(argus_ref):
    argus_link = website_prefix + argus_ref
    argus_soup = get_request_soup(argus_link)
    argus_cote = argus_soup.find("span", class_="jsRefinedQuot")
    if argus_cote is not None:
        argus_cote = argus_cote.get_text().strip().replace(" ", "")
    else:
        argus_cote  = "NA"
    return argus_cote

def get_info_car(car_url):
    soup = get_request_soup(car_url)
    price = soup.find("strong", class_="sizeD lH35 inlineBlock vMiddle ").get_text().strip()
    elem_reg = re.compile("Année")
    year = soup.find("h4", text=elem_reg).findNext("span").get_text().strip()
    elem_reg = re.compile("Kilométrage")
    km = soup.find("h4", text=elem_reg).findNext("span").get_text().strip()
    seller_type = soup.find("div", class_="bold italic mB10").contents[0].strip()
    phone = soup.find("div", class_="phoneNumberContent").findNext("span").contents[0].strip()
    version = soup.find("div", class_="versionTxt txtGrey7C sizeC mB10 hiddenPhone").get_text().strip()

    argus_ref = soup.find("a", class_="btnDark txtL block").attrs["href"]
    car_cote = get_info_argus(argus_ref)
    car_info = [version, year, km, price, car_cote, seller_type, phone]
    return car_info

def format_info_cars_df(df):
    df["model"] = df["model"].str.split(" ").str[0]
    df["km"] = df["km"].str.replace(r"\D+", "").astype("int")
    df["price"] = df["price"].str.replace(r"\D+", "").astype("int")
    df["phone"] = df["phone"].str.replace(r"\D+", "")
    return df

#
# Main code starts here
#

# Retreive cars links
zoe_links = get_all_car_links(website_url)

# Retreive information about the cars
cars_info = []
cars_info = cars_info + list(map(lambda x: get_info_car(x), zoe_links))
# Build cars dataframe
cars_df = pd.DataFrame(cars_info)
cars_df.columns = ["model", "year", "km", "price", "cote", "seller_type", "phone"]

# Format columns in cars dataframe
cars_df = format_info_cars_df(cars_df)

print(cars_df)
