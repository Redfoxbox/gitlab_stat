import requests
from datetime import datetime, timedelta
import calendar
import csv

# GitLab API configuration
gitlab_url = ''  # GitLab szerver URL-je
private_token = ''  # GitLab API privát token

# Csv output
csvfile = open('gitlab_stat_commits.csv', 'w', encoding='utf-8', newline='')
cswriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
cswriter.writerow(["project_name", "project_id", "current_month" ,"Commits", "lines_added", "lines_deleted", "net_total_changes"])

# API function for making requests
def gitlab_api_get(endpoint, params=None):
    headers = {
        'Private-Token': private_token
    }
    try:
        response = requests.get(
            f'{gitlab_url}/api/v4/{endpoint}', headers=headers, params=params)
        response.raise_for_status()
        return response.json(), response.headers
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return None, None

# Function to get commit statistics
def get_commit_stats(project_id, commit_id):
    response, _ = gitlab_api_get(f'projects/{project_id}/repository/commits/{commit_id}')
    if response:
        return response.get('stats', {'additions': 0, 'deletions': 0})
    else:
        return {'additions': 0, 'deletions': 0}
    
# Get the list of projects
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

# Retrieve and write information about all changes made by developers for each project
for project in projects:
    project_id = project['id']
    project_name = project['name']
    print(project_name)

    # Set a retrospective yearly period (12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    # Loop through each month to retrieve and write information about all changes
    current_date = end_date

    while current_date >= start_date:
        current_month = current_date.strftime('%Y-%m')
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]

        response, headers = gitlab_api_get(f'projects/{project_id}/repository/commits', {
                                           'since': f'{current_month}-01T00:00:00Z', 'until': f'{current_month}-{last_day}T23:59:59Z', 'per_page': 100})
        #print(response)

        if response is not None:
            
            lines_added = 0
            lines_deleted = 0
            for commit in response:
                commit_stats = get_commit_stats(project_id, commit['id'])
                lines_added += commit_stats['additions']
                lines_deleted += commit_stats['deletions']

            net_total_changes = lines_added - lines_deleted

            #print(current_month + f" Lines added: {lines_added}, Lines deleted: {lines_deleted}, Net total changes: {net_total_changes}")

            
            # Write to CSV
            cswriter.writerow([project_name, project_id, current_month,len(response), lines_added, lines_deleted, net_total_changes])
        else:
            print("API request failed.")

        current_date -= timedelta(days=30)

csvfile.close()