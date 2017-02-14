from lxml import html
import requests


STATES = [alabama, alaska, arizona, arkansas, california, colorado, connecticut, 
        delaware, florida, georgia, hawaii, idaho, illinois, indiana, iowa, 
        kansas, kentucky, louisiana, maine, maryland, massachusetts, michigan, 
        minnesota, mississippi, missouri, montana, nebraska, nevada, new hampshire, 
        new jersey, new mexico, new york, north carolina, north dakota, ohio, 
        oklahoma, oregon, pennsylvania, rhode island, south carolina, south dakota, 
        tennessee, texas, utah, vermont, virginia, washington, west virginia, 
        wisconsin, wyoming]


    state_page = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_tree = html.fromstring(state_page.content)
#Take a race
#gather data for each state
#senate:
def scrape_senate_races():
    for state in STATES:
        senate.scrape_state_overview(state)
        senate.scrape_regional_details(state)
    state_overview = json.dumps()
    regional_details = json

    text_file = open('senate_state_overview.txt', 'w')
    text_file.write(file to be writtem)
    text_file.close()

    text_file = open('senate_regional_details.txt', 'w')
    text_file.write(file to be writtem)
    text_file.close()
