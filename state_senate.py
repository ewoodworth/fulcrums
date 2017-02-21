from bs4 import BeautifulSoup
import urllib
import lxml
import requests


def get_active_districts(state):
    """Given a state, return a list of districts numbers in which an election was held"""

    r = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_soup = BeautifulSoup(r.content)
    state_senate_race = state_soup.find_all("div", class_="eln-state-senate")
    results_table = state_senate_race[0].find_all("table", class_="eln-group-table")

    districts = []
    district_rows = results_table[0].find_all("tr", class_="eln-group-row")
    for item in district_rows: #district rows doesnt exists
        district_number = item.find("td", class_="eln-name-cell").get_text()#district number text
        district_number = district_number.strip().lower()
        districts.append(district_number)
    return districts


def get_race_results_by_district(state):
    """Returns a list of lists for a given state. Innermost lists are [district, candidate, party, 
    districtwide votes] """

    r = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_soup = BeautifulSoup(r.content)
    state_senate_race = state_soup.find_all("div", class_="eln-state-senate")

    if state_senate_race:
        results_by_district = []
        for district in get_active_districts(state):
            r = requests.get('http://www.nytimes.com/elections/results/' + state + '-state-senate-district-' + district)
            state_senate_soup = BeautifulSoup(r.content)
            districtwide_table = state_senate_soup.find("table", class_ = "eln-results-table")
            all_candidates_rows = districtwide_table.find_all("tr", class_ = "eln-row")

            for row in all_candidates_rows:
                candidate = row.find("span", class_="eln-name-display").get_text().strip()
                party = row.find("span", class_="eln-party-display").get_text()
                votes = row.find("td", class_="eln-votes").get_text()
                results_by_district.append([district, candidate, party, votes])
        return results_by_district
    else:
        return ["NO STATE SENATE RACE IN" + state + "THIS YEAR"]

def get_race_results_by_county(state):
    """Returns a list of lists for a given state. innermosts lists are [district, 
    county, winner's vote count, runner-up's vote count]"""


    r = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_soup = BeautifulSoup(r.content)
    state_senate_race = state_soup.find_all("div", class_="eln-state-senate")

    if state_senate_race:
        results_by_county = []
        for district in get_active_districts(state):
            r = requests.get('http://www.nytimes.com/elections/results/' + state + '-state-senate-district-' + district)
            state_senate_soup = BeautifulSoup(r.content)

            counties_in_district = state_senate_soup.find("table", class_ = "eln-county-table")
            #sometimes the district doesn't have a sublist of conties
            if counties_in_district:  
                all_county_rows = counties_in_district.find_all("tr", class_ = "eln-row")
                for row in all_county_rows:
                    county = row.find("td", class_ = "eln-name").get_text().strip()
                    winner_votes = row.find("td", class_="eln-candidate").get_text().strip()
                    loser_votes = row.find("td", class_="eln-last-candidate").get_text().strip()
                    results_by_county.append([district, county, winner_votes, loser_votes])
            else:
                results_by_county.append(["No county level data for district " + district])
        return results_by_county
    else:
        return ["NO STATE SENATE RACE IN" + state + "THIS YEAR"]

# get_race_results_by_district('alaska')