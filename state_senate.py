from bs4 import BeautifulSoup
import urllib
import lxml
import requests


def get_active_districts(state):
    """Given a state, return a list of districts in which an election was held"""

    r = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_soup = BeautifulSoup(r.content)
    state_senate_race = state_soup.find_all("div", class_="eln-state-senate")
    results_table = state_senate_race[0].find_all("table", class_="eln-group-table")
    district_rows = results_table[0].find_all("tr", class_="eln-group-row")

    districts = []
    #these three sates are only running elections in one or two districts so their tables don't have a column for district numbers
    if state == 'virginia':
        districts = ['1', '5']
    elif state == 'new-jersey':
        districts = ['18']
    elif state == 'michigan':
        districts = ['4']
    else:
        for item in district_rows:
            district = item.find("td", class_="eln-name-cell").get_text()
            #is there a better way to make these sequential replacements than a chain of .replace commands?
            #ALASKA (districts are letters)
            district = district.strip().lower()
            #MASS/VT (districts are words)
            district = district.replace("-", "")
            #Washington state has unicode keys after the district numbers, that I took care of in get_race_results_ , but there's gotta be a better way
            # district = district.replace("\u2020", "")
            district = district.replace("  ", " ")
            district = district.replace(" & ", "-")
            district = district.replace(", ", "-")
            district = district.replace(" ", "-")
            districts.append(district)
    return districts


def get_race_results_by_district(state):
    """Returns a string formatted for csv upload into excel for a given state. 
    Lines are 'state, district, candidate, party, districtwide votes' """

    r = requests.get('http://www.nytimes.com/elections/results/' + state.lower())
    state_soup = BeautifulSoup(r.content)
    state_senate_race = state_soup.find_all("div", class_="eln-state-senate")

    if state_senate_race:
        results_by_district = "State. District, Candidate, Party, Votes\n"

        for district in get_active_districts(state):

            #see note in get_active_districts
            
            if state == 'washington':
                district = str(district[0:1])

            #there are three possible formats for the state senate url
            #two for regular elections, depending on whether the state districts are named or numbered
            #one for special state senate elections   

            if state == 'massachusetts' or state == 'vermont':
                r = requests.get('http://www.nytimes.com/elections/results/' + state.lower() + '-state-senate-' + district)
            elif state == 'virginia' or state == 'michigan':
                r = requests.get('http://www.nytimes.com/elections/results/' + state.lower() + '-state-senate-special-district-' + district)
            else:
                r = requests.get('http://www.nytimes.com/elections/results/' + state.lower() + '-state-senate-district-' + district)

            state_senate_soup = BeautifulSoup(r.content)
            districtwide_table = state_senate_soup.find("table", class_ = "eln-results-table")
            all_candidates_rows = districtwide_table.find_all("tr", class_ = "eln-row")

            for row in all_candidates_rows:
                candidate = row.find("span", class_="eln-name-display").get_text().strip()
                party = row.find("span", class_="eln-party-display").get_text().replace(u'\u2019', '')
                votes = row.find("td", class_="eln-votes").get_text().replace(",", "")
                results_by_district += state + ',' + district + ',' + candidate+ ',' + party + ',' + votes + '\n'
        return results_by_district
    else:
        return state + ',,,no state senate race in 2016\n'

def get_race_results_by_county(state):
    """Returns a string formatted for csv upload into excel for a given state. 
    Lines are 'state, district, county, winner votes, winner name, runner up votes runner up name' """


    r = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_soup = BeautifulSoup(r.content)
    state_senate_race = state_soup.find_all("div", class_="eln-state-senate")

    if state_senate_race:
        results_by_county = "State, District, County, Winner Votes, Winner, Runner Up Votes, Runner Up\n"
        for district in get_active_districts(state):

            #there are three possible formats for the state senate url
            #two for regular elections, depending on whether the state districts are named or numbered
            #one for special state senate elections  

            if state == 'massachusetts' or state == 'vermont':
                r = requests.get('http://www.nytimes.com/elections/results/' + 
                    state + '-state-senate-' + district)
            elif state == 'virginia':
                r = requests.get('http://www.nytimes.com/elections/results/' + state + '-state-senate-special-district-' + district)
            else:
                r = requests.get('http://www.nytimes.com/elections/results/' + 
                    state + '-state-senate-district-' + district)


            state_senate_soup = BeautifulSoup(r.content)
            counties_in_district = state_senate_soup.find("table", class_ = "eln-county-table")

            #sometimes the district doesn't have a sublist of conties
            #WRITE TEST FOR UNCONTESTED RACES
            uncontested_race = state_senate_soup.find("span", "eln-uncontested-label")
            if uncontested_race:
                results_by_county += state + ',' + district + ',' + 'uncontested race\n'
            if counties_in_district:
                header = counties_in_district.find_all("th")
                winner = header[1].get_text().strip()
                loser =  header[2].get_text().strip()
                all_county_rows = counties_in_district.find_all("tr", class_ = "eln-row")
                for row in all_county_rows:
                    county = row.find("td", class_ = "eln-name").get_text().strip()
                    winner_votes = row.find("td", class_="eln-candidate").get_text().strip().replace(",", "")
                    loser_votes = row.find("td", class_="eln-last-candidate").get_text().strip().replace(",", "")
                    results_by_county += state + ',' + district + ',' + county + ',' + winner_votes + ',' +  winner + ',' + loser_votes + ',' + loser + '\n'
            else:
                results_by_county += state + ',' + district + ',' + "no county level data for 2016\n"
        return results_by_county
    else:
        return state + ',,,no state senate race in 2016\n'

# get_race_results_by_county('massachusetts')