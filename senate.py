from bs4 import BeautifulSoup
import urllib
import lxml
import requests


def generate_results_object_statewide(state, senate_soup):
    """Return a dictionary of states, with value lists of [[Candidate Name, Last_name 
    Vote Count, Vote Percent of Total Cast]...]"""

    results_object_statewide = {}
    results_object_statewide[state] = [['Candidate Name', 'Last Name', 'Party', 'Vote Count',
                                      'Vote Percent of Total Cast']]
    senate_race_results = senate_soup.find_all("table", class_="eln-results-table")
    race_results = senate_race_results[0].find_all("tr", class_="eln-row")

    for item in race_results:
        candidate_name = item.find("span", class_="eln-name-display")
        candidate_name = candidate_name.get_text().strip()

        candidate_last =  item.find("span", class_="eln-last-name")
        candidate_last = candidate_last.get_text().strip()
        
        candidate_party = item.find("span", class_="eln-party-display")
        candidate_party = candidate_party.get_text().strip()

        candidate_votes = item.find("td", class_="eln-votes")
        candidate_votes = int(candidate_votes.get_text().strip().replace(",", ""))

        results_object_statewide[state].append([candidate_name, candidate_last, 
                                                candidate_party, candidate_votes])
    return results_object_statewide



def generate_results_object_by_county(state, senate_soup):
    """Return a dictionary of states, with value lists of [[County Name, 
    Votes for Winning Candidate, Votes for Second Place]...]"""

    results_object_by_county = [["County Name", "Winner", "Runner Up"]]
    senate_race_results_by_county = senate_soup.find_all("table", class_="eln-county-table")
    try:
        senate_race_results_by_county[0]
    except IndexError:
        print "NYT lacks county data for the senate race in " + state + " this election"
        county_details = None
    else:
        county_results = senate_race_results_by_county[0].find_all("tr", class_="eln-row")
        for item in county_results:
            county_details = []
            county_name = item.find("td", class_="eln-cell eln-name")
            county_name = county_name.get_text()
            county_name = county_name.strip()

            winner_votes = item.find("td", class_="eln-cell eln-candidate ")
            winner_votes = winner_votes.get_text()
            winner_votes = winner_votes.strip()
            winner_votes = winner_votes.replace(",", "")
            winner_votes = int(winner_votes)

            loser_votes = item.find("td", class_="eln-cell eln-candidate eln-last-candidate")
            loser_votes = loser_votes.get_text()
            loser_votes = loser_votes.strip()
            loser_votes = loser_votes.replace(",", "")
            loser_votes = int(loser_votes)
            county_details = [county_name, winner_votes, loser_votes]
            results_object_by_county.append(county_details)

    return results_object_by_county


def get_race_details(state):
    """Get list of candidates from a given state 
    returns senate_candidate_list = [lastname, lastname, lastname, etc]"""

    r = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_soup = BeautifulSoup(r.content)
    senate_race = state_soup.find_all("div", class_="eln-senate")
    #VVVVVVVV  THIS TOSSES AN ERROR IF THERES NO SENATE RCE HERE THIS CYCLE VVVVVVV
    senate_results = senate_race[0].find(class_="eln-results-container")
    candidates = senate_results.find_all(class_="eln-last-name")
    parties = senate_results.find_all(class_="eln-party-display")
    parties = [item.get_text() for item in parties]
    print parties
    #SO! ITS THE WINNER BETWEEN R AND D FOLLOWED BY THE LOSER BETWEEN R AND D
    senate_candidate_list = []
    index = 0
    for item in candidates:
        last_name = item.get_text()
        last_name = last_name.strip()
        last_name = str(last_name)
        last_name = last_name.translate(None, '*')
        last_name = last_name.replace(' ', '-')
        last_name = last_name.lower()
        if parties[index] == "Democrat" or parties[index] == "Republican":
            senate_candidate_list.append(last_name)
        index += 1
    return senate_candidate_list

def get_race_results(state, scope):
    """Check that a race was fought in this state, if so return results statewide 
    and local, else return None"""

    r = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_soup = BeautifulSoup(r.content)
    senate_race = state_soup.find_all("div", class_="eln-senate")

    #What if there is was no senate race here this year?
    try:
        senate_race[0]
    except IndexError:
        print "There is no senate race in " + state + " this election"
        county_details = None
        statewide_details = None
    else:
        #NYT HAS THREE POSSIBLE URL FORMATS FOR SENATE RACES, ONE W/ STATE NAME, ONE WITH THE TWO CANDIDATE NAMES BUT ONLY THE DEM AND REP CANDIDATES
        r = requests.get("http://www.nytimes.com/elections/results/" + state + "-senate")
        check_soup = BeautifulSoup(r.content)
        div_w_404 = check_soup.find("div", class_="columnGroup")
        if div_w_404 is not None:
            senate_candidate_list = get_race_details(state)
            r = requests.get("http://www.nytimes.com/elections/results/" + state + "-" + "senate-" + senate_candidate_list[0] + "-" + senate_candidate_list[1])
            check_soup = BeautifulSoup(r.content)
            div_w_404 = check_soup.find("div", class_="columnGroup")
            if div_w_404 is not None:
                senate_candidate_list = get_race_details(state)
                r = requests.get("http://www.nytimes.com/elections/results/" + state + "-" + "senate-" + senate_candidate_list[1] + "-" + senate_candidate_list[0])                
        senate_soup = BeautifulSoup(r.content)
        if scope == "state":
            return generate_results_object_statewide(state)
        elif scope == "county":
            return generate_results_object_by_county(state)
        else:
            return None
