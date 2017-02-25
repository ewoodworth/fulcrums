from bs4 import BeautifulSoup
import urllib
import lxml
import requests


def get_active_districts(state):
    """Given a state, return a list of districts in which an election was held"""

    r = requests.get('http://www.nytimes.com/elections/results/' + state.lower())
    state_soup = BeautifulSoup(r.content)
    state_house_race = state_soup.find_all("div", class_="eln-state-house")
    results_table = state_house_race[0].find_all("table", class_="eln-group-table")
    district_rows = results_table[0].find_all("tr", class_="eln-group-row")

    districts = []

    #michigan has two districts in special elections and a bunch of others in traditional ones BOO

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
    print districts
    return districts


def get_race_results_by_district(state):
    """Returns a string formatted for csv upload into excel for a given state. 
    Lines are 'state, district, candidate, party, districtwide votes' """

    r = requests.get('http://www.nytimes.com/elections/results/' + state.lower())
    state_soup = BeautifulSoup(r.content)
    state_assembly_race = state_soup.find_all("div", class_="eln-state-house")

    if state_assembly_race:
        results_by_district = "State. District, Candidate, Party, Votes\n"

        for district in get_active_districts(state):

            #see note in get_active_districts
            
            if state == 'Washington':
                district = str(district[0:1])

            #there are three possible formats for the state house url
            #two for regular elections, depending on whether the state districts are named or numbered
            #one for special state house elections   

            if state == 'Massachusetts' or state == 'Vermont':
                r = requests.get('http://www.nytimes.com/elections/results/' + state.lower() + '-state-house-' + district)
            elif state == 'Virginia' or state == 'Michigan':
                r = requests.get('http://www.nytimes.com/elections/results/' + state.lower() + '-state-house-special-district-' + district)
            else:
                r = requests.get('http://www.nytimes.com/elections/results/' + state.lower() + '-state-house-district-' + district)

            state_house_soup = BeautifulSoup(r.content)
            districtwide_table = state_house_soup.find("table", class_ = "eln-results-table")
            all_candidates_rows = districtwide_table.find_all("tr", class_ = "eln-row")

            results_by_district += state + ',' + district

            for row in all_candidates_rows:
                candidate = row.find("span", class_="eln-name-display").get_text().strip()
                party = row.find("span", class_="eln-party-display").get_text().replace(u'\u2019', '')
                votes = row.find("td", class_="eln-votes").get_text().replace(",", "")
                results_by_district +=  ',' + candidate+ ',' + party + ',' + votes 
            results_by_district += '\n'
        print results_by_district
        return results_by_district
    else:
        return state + ',,,no state house/assembly race in 2016\n'
        return state + ',,,no state house/assembly race in 2016\n'

def get_race_results_by_county(state):
    """Returns a string formatted for csv upload into excel for a given state. 
    Lines are 'state, district, county, winner votes, winner name, runner up votes runner up name' """

    r = requests.get('http://www.nytimes.com/elections/results/' + state.lower())
    state_soup = BeautifulSoup(r.content)
    state_house_race = state_soup.find_all("div", class_="eln-state-house")

    if state_house_race:
        results_by_county = "State, District, County, Winner Votes, Winner, Runner Up Votes, Runner Up\n"
        for district in get_active_districts(state):

            #there are three possible formats for the state house url
            #two for regular elections, depending on whether the state districts are named or numbered
            #one for special state house elections  

            if state == 'Massachusetts' or state == 'Vermont':
                r = requests.get('http://www.nytimes.com/elections/results/' + 
                    state.lower() + '-state-house-' + district)
            elif state == 'Virginia':
                r = requests.get('http://www.nytimes.com/elections/results/' + state.lower() + '-state-house-special-district-' + district)
            else:
                r = requests.get('http://www.nytimes.com/elections/results/' + 
                    state.lower() + '-state-house-district-' + district)


            state_house_soup = BeautifulSoup(r.content)
            counties_in_district = state_house_soup.find("table", class_ = "eln-county-table")

            #sometimes the district doesn't have a sublist of conties
            #sometimes this is because the race is uncontested.
            
            uncontested_race = state_house_soup.find("span", "eln-uncontested-label")
            if uncontested_race:
                party = state_house_soup.find("span", class_="eln-party")
                winner = state_house_soup.find("span", class_="eln-name")
                winner_votes = "uncontested"
                results_by_county += state + ',' + district + ',' + 'uncontested race' + winner_votes + winner + ',,\n'
            elif counties_in_district:
                header = counties_in_district.find_all("th")
                winner = header[1].get_text().strip()
                loser =  header[2].get_text().strip()
                all_county_rows = counties_in_district.find_all("tr", class_ = "eln-row")
                for row in all_county_rows:
                    county = row.find("td", class_ = "eln-name").get_text().strip()
                    winner_votes = row.find("td", class_="eln-candidate").get_text().strip().replace(",", "")
                    # winner_party = winner_votes.find("div", class_="eln-republican")
                    loser_votes = row.find("td", class_="eln-last-candidate").get_text().strip().replace(",", "")
                    # loser_party = row.find("td", class_="eln-party").get_text()
                    results_by_county += state + ',' + district + ',' + county + ',' + winner_votes + ',' +  winner + ',' + loser_votes + ',' + loser + '\n'
            else:
                results_by_county += state + ',' + district + ',' + 'no county data at NYT\n'
        print results_by_county    
        return results_by_county
    else:
        print state + ',,,no state house/assembly race in 2016\n'
        return state + ',,,no state house/assembly race in 2016\n'

# get_race_results_by_district('Arizona')