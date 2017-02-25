from lxml import html
import requests
import senate, state_senate, state_assembly
import json



STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
        'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 
        'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
        'Maryland', 'Massachusetts', 'Minnesota', 'Mississippi',
        'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New-Hampshire',
        'New-Mexico', 'New-York', 'North-Carolina', 'North-Dakota', 'Ohio', 
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode-Island', 'South-Carolina',
        'South-Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
        'Washington', 'West-Virginia', 'Wisconsin', 'Wyoming']

results_2016 = {}

def run_the_country(scope):
    """Scope can be 'national', 'state', or 'county' """

    races = ['presidential','senate', 'house', 'state_senate', 'state_assembly']
    for state in STATES:
        results_2016['national'][state]['local'] = senate.get_race_results(state, 'local')


def scrape_senate_races():

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

def scrape_state_senate_races():
    """ Writes one text file per state to file."""

    state_senate_results_by_county = ""
    state_senate_results_by_district = ""
    for state in STATES:
        print "PROCESSING", state.upper()

        state_senate_results_by_county += state_senate.get_race_results_by_county(state)
        state_senate_results_by_district += state_senate.get_race_results_by_district(state)

        print state.upper(), "DONE"

    by_county = str(state_senate_results_by_county)
    text_file = open('State_Senate_By_County/national' + '.txt', 'w')
    text_file.write(by_county)
    text_file.close()

    by_district = str(state_senate_results_by_district)
    text_file = open('State_Senate_By_District/national' + '.txt', 'w')
    text_file.write(by_district)
    text_file.close()

def scrape_state_assembly_races():
    """ Writes one text file per state to file."""

    state_assembly_results_by_county = ""
    state_assembly_results_by_district = ""
    for state in STATES:
        print "PROCESSING", state.upper()

        state_assembly_results_by_county += state_assembly.get_race_results_by_county(state)
        state_assembly_results_by_district += state_assembly.get_race_results_by_district(state)

        print state.upper(), "DONE"

    by_county = str(state_assembly_results_by_county)
    text_file = open('State_Assembly_By_County/national' + '.txt', 'w')
    text_file.write(by_county)
    text_file.close()

    by_district = str(state_assembly_results_by_district)
    text_file = open('State_Assembly_By_District/national' + '.txt', 'w')
    text_file.write(by_district)
    text_file.close()

        

# scrape_state_senate_races()
scrape_state_assembly_races()