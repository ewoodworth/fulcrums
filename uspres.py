from lxml import html
import requests
import senate


STATES = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
        'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
        'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine',
        'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi',
        'missouri', 'montana', 'nebraska', 'nevada', 'new-hampshire', 'new-jersey',
        'new-mexico', 'new-york', 'north-carolina', 'north-dakota', 'ohio', 
        'oklahoma', 'oregon', 'pennsylvania', 'rhode-island', 'south-carolina',
        'south-dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia',
        'washington', 'west-virginia', 'wisconsin', 'wyoming']


# state_page = requests.get('http://www.nytimes.com/elections/results/' + state)
# state_tree = html.fromstring(state_page.content)

def scrape_senate_races():
    print "line 20"
    senate_state_overviews = {}
    senate_regional_details = {}

    for state in STATES:
        senate_state_overviews[state] = senate.scrape_state_overview(state)
        senate_regional_details[state] = senate.scrape_regional_details(state)

    state_overviews = json.dumps(senate_state_overviews)
    text_file = open('senate_state_overview.txt', 'w')
    text_file.write(state_overviews)
    text_file.close()

    regional_details = json.dumps(senate_regional_details)
    text_file = open('senate_regional_details.txt', 'w')
    text_file.write(regional_details)
    text_file.close()

scrape_senate_races()