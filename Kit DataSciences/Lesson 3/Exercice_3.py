import requests
from bs4 import BeautifulSoup
import time
import json
import pandas as pd

def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        soup = BeautifulSoup(request_result.content,"html.parser")
    return soup

def get_list_contributors(url):
    page = requests.get(url)
    soup = _handle_request_result_and_build_soup(page)
    rows = soup.find('table').find_all('tr')
    rows = rows[1:]
    contributors = []
    for row in rows:
        cols=row.find('td').text.split(' ')[0]
        contributors.append(cols)
    return contributors

def _handle_request_result_and_build_json(response):
    if response.status_code == 200:
        json_tab = json.loads(response.content)
    return json_tab

def get_sum_stars_per_owner(response):
    try:
        json_tab =_handle_request_result_and_build_json(response)
        d = dict(sorted([(json_tab[i]['name'], json_tab[i]['stargazers_count']) for i in range(len(json.loads(response.content)))]))
        df = pd.DataFrame(list(d.items()), columns=['Repository','Count stars'])
        return df['Count stars'].sum()
    except ValueError:
       return 0

def get_info_repositories(owner):
    number_repos = 0
    number_stars = 0
    j = 1
    while True:
        api_token = '...'
        headers = {'Authorization': 'token {}'.format(api_token)}
        api_url_base = "https://api.github.com/users/{owner}/repos?page={j}&per_page=100"
        response = requests.get(api_url_base, headers=headers)
        json_tab =_handle_request_result_and_build_json(response)
        if len(json_tab) != 0:
            number_repos += len(json_tab)
            number_stars += get_sum_stars_per_owner(response)
            j += 1
        else:
            break
    if number_repos == 0:
        return(0,0)
    else:
        return (round(number_stars/number_repos*100)/100, number_repos)

def get_dataframe_users_averaged_stars(owners):
    average_stars = []
    names = []
    repositories = []
    for owner in owners:
        print(owner)
        star, repository = get_info_repositories(owner)
        names.append(owner)
        repositories.append(repository)
        average_stars.append(star)
    df = pd.DataFrame({\"Name\": names,
                       \"# Repositories\": repositories,
                        \"Average stars score\": average_stars})
    return df.sort_values(by=['Average stars score'], ascending=False)

if __name__ == '__main__':

    start = time.time()
# Contributors information
    url = "https://gist.github.com/paulmillr/2657075"

    contributors = get_list_contributors(url)
    df = get_dataframe_users_averaged_stars(contributors)
    end = time.time()
    print("Execution time: " + str(round((end - start)/60)) + " min")
    df.to_csv("Dataframe_github_256_serial.csv")
