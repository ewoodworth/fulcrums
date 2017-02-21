from lxml import html
import requests
import senate, state_senate
import json


STATES = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
        'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
        'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine',
        'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi',
        'missouri', 'montana', 'nebraska', 'nevada', 'new-hampshire', 'new-jersey',
        'new-mexico', 'new-york', 'north-carolina', 'north-dakota', 'ohio', 
        'oklahoma', 'oregon', 'pennsylvania', 'rhode-island', 'south-carolina',
        'south-dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia',
        'washington', 'west-virginia', 'wisconsin', 'wyoming']


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

    state_senate_results_by_county = {}
    state_senate_results_by_district = {}
    for state in STATES:
        print "PROCESSING ", state.upper()

        state_senate_results_by_county = state_senate.get_race_results_by_county(state)
        state_senate_results_by_district = state_senate.get_race_results_by_district(state)

        by_county = json.dumps(state_senate_results_by_county)
        text_file = open('State_Senate_By_County/state_senate_by_county_' + state + '.txt', 'w')
        text_file.write(by_county)
        text_file.close()

        by_district = json.dumps(state_senate_results_by_district)
        text_file = open('State_Senate_By_District/state_senate_by_district_' + state + '.txt', 'w')
        text_file.write(by_district)
        text_file.close()

        print state.upper(), " DONE"

scrape_state_senate_races()