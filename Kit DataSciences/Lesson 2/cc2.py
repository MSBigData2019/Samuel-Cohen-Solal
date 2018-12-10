import requests
from bs4 import BeautifulSoup
import pandas as pd
import math

website_prefix = "https://www.darty.com/nav/achat/informatique/ordinateur_portable/portable/marque_"


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        html_doc = request_result.content
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup


def get_page_discount_products(brand):
    url = website_prefix + "_" + brand.lower() + "__" + brand.upper() + ".html"
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    specific_class = "striped_price"

    #Calcul du discount moyen pour la première page
    somme = 0
    nb_modeles_discount = 0
    all_discounts_page = soup.find_all("span",specific_class)
    for discount in all_discounts_page:
        somme = somme + float(discount.text[2:-1])
    nb_modeles_discount += len(all_discounts_page)

    #Calcul du nombre de pages au total pour récuprérer les informations de discount des autres pages
    number_models_text = soup.find("div", {"class", "list_number_product"}).text
    position = number_models_text.find(" ")
    number_models = int(number_models_text[:position].strip("\n"))
    if number_models % 30 == 0:
        number_pages = math.floor(number_models/30)
    else:
        number_pages = math.floor(number_models/30) + 1

    #Calcul du discount moyen pour les autres pages
    for page in range(2, number_pages + 1):
        url = website_prefix + str(page) + "__" + brand.lower() + "__" + brand.upper() + ".html"
        res = requests.get(url)
        soup = _handle_request_result_and_build_soup(res)
        all_discounts_page = soup.find_all("span",specific_class)
        for discount in all_discounts_page:
            somme = somme + float(discount.text[2:-1])
        nb_modeles_discount += len(all_discounts_page)
    mean = somme / nb_modeles_discount
    return(mean)

print("Average discount for Dell Laptops : " + str(get_page_discount_products("dell")))
print("Average discount for Acer Laptops : " + str(get_page_discount_products("acer")))
