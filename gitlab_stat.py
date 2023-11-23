import requests
from datetime import datetime, timedelta
import calendar
import csv

# GitLab API konfiguráció
gitlab_url = ''  # GitLab szerver URL-je
private_token = ''  # GitLab API privát token

# Csv kimenet
csvfile=open('gitlab_stat.csv', 'w', encoding='utf-8', newline='')
cswriter = csv.writer(csvfile, delimiter=';',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
# API hívásokhoz használt függvény
def gitlab_api_get(endpoint, params=None):
    headers = {
        'Private-Token': private_token
    }
    try:
        response = requests.get(
            f'{gitlab_url}/api/v4/{endpoint}', headers=headers, params=params)
        #print(response.headers)
        response.raise_for_status()
        return response.json(), response.headers
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return None, None

# Projekt lista lekérése
projects = []
page = 1
while True:
    response, headers = gitlab_api_get(
        'projects', params={'page': page, 'per_page': 100})
    if response is not None:
        projects.extend(response)
    else:
        print("API request failed.")
    if page < int(headers['x-total-pages']):
        page += 1
    else:
        break

print(len(projects))
# Minden projekt CI/CD analitikáinak lekérése és kiírása
for project in projects:
    project_id = project['id']
    project_name = project['name']
    print(project_name)

    # Visszamenőleges éves időszak beállítása (12 hónap)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    # Ciklus az egyes hónapok lekérése és kiírása céljából
    current_date = end_date

    while current_date >= start_date:
        current_month = current_date.strftime('%Y-%m')
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        response, headers = gitlab_api_get(f'projects/{project_id}/pipelines', {
                                           'updated_after': f'{current_month}-01', 'updated_before': f'{current_month}-{last_day}', 'per_page': 100})

  
        if response is not None:
            print(current_month+" "+headers['X-Total'])
            cswriter.writerow([project_name,project_id,current_month, headers['X-Total']])
        else:
            print("API request failed.")

        current_date -= timedelta(days=30)
cswriter.close()