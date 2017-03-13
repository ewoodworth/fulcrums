from bs4 import BeautifulSoup
import urllib
import lxml
import requests


STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
        'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 
        'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
        'Maryland', 'Massachusetts', 'Minnesota', 'Mississippi',
        'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New-Hampshire',
        'New-Mexico', 'New-York', 'North-Carolina', 'North-Dakota', 'Ohio', 
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode-Island', 'South-Carolina',
        'South-Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
        'Washington', 'West-Virginia', 'Wisconsin', 'Wyoming']


def scrape_state_house_races():
    """ Writes one text file per state to file."""

    house_results_by_county = ""
    house_results_by_district = ""
    for state in STATES:
        print "PROCESSING", state.upper()
        state_house_results_by_district += get_state_house_race_results_statewide(state)[by_district]
        state_house_results_by_county += get_state_house_race_results_statewide(state)[by_county]
        print state.upper(), "DONE"

    by_district = str(state_house_results_by_district)
    text_file = open('Race_Results/state_house_by_district' + '.txt', 'w')
    text_file.write(by_district)
    text_file.close()

    by_county = str(state_house_results_by_county)
    text_file = open('Race_Results/state_house_results_by_county' + '.txt', 'w')
    text_file.write(by_county)
    text_file.close()

def get_state_house_race_results_statewide(state):
    """ For a given 'State' return a dictionary with keys 'by_district' and 
    'by_county' which are two csv formatted strings:'State, District, 
    Candidate Name, Party, Votes, Last Name \n' and 'State, District, County Name, 
    Winner Votes, Loser Votes' """

    results_statewide = ('State, Candidate, Party, Votes\n')
    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
                                    state.lower())
    statewide_soup = BeautifulSoup(statewide_html.content, "lxml")
    state_house_race_div = statewide_soup.find("div", id="state-house")
    statewide_state_house_race_results = {}

    if state_house_race_div:
        state_house_race_districts = state_house_race_div.find_all('td', class_="eln-winner")

        for state_house_race_district in state_house_race_districts:
            state_house_race_url = state_house_race_district.find('a')['href']
            print state_house_race_url
            state_house_race_statewide_html = requests.get(state_house_race_url)
            state_house_race_statewide_soup = BeautifulSoup(state_house_race_statewide_html.content)

            district = state_house_race_statewide_soup.find('h1', class_='eln-headline'
                                                     ).get_text(
                                                     ).split(":"
                                                     )[0].replace("District State House Results", ""
                                                     ).replace("State House Results", ""
                                                     ).replace(state, ""
                                                     )
            candidates_table = state_house_race_statewide_soup.find('table', class_= 'eln-results-table')
            candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')

            candidate_affiliation = {}

            for row in candidiate_rows:
                state_house_race_results_by_district = 'Candidate, Party, Votes, Last Name\n'
                candidiate = row.find('td', class_= 'eln-name').find('span', class_='eln-name-display').get_text().strip()
                last_name = 
                party = row.find('td', class_= 'eln-party').find('span', class_='eln-party-display').get_text().strip()
                votes = row.find('td', class_= 'eln-votes').get_text().strip().replace(',', '')
                state_house_race_results_by_district += candidiate + ',' + party + ',' + votes+ '\n'
                candidate_affiliation[last_name] = party
            statewide_state_house_race_results['by_district'] = state_house_race_results_by_district

            counties_table = house_race_statewide_soup.find('table', 'eln-county-table')
            county_rows = counties_table.find_all('tr', class_='eln-row')

            winner = counties_table.find('th', class_='')
            loser = counties_table.find('th', class_='')
            winning_party = candidate_affiliation[winner]
            loser_party = candidate_affiliation[loser]

            state_house_race_results_by_county = state + district
            for county_row in county_rows:
                county = county_row.find('td', 'eln-name').get_text().strip()
                winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
                loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
                state_house_race_results_by_county += county + ',' + winner_votes + ',' + loser_votes +'\n'
            statewide_state_house_race_results['by_county'] = state_house_race_results_by_county
    else:
        statewide_state_house_race_results['by_district'] = state + ",,No State House/Assembly race in" + state + "this election"
        statewide_state_house_race_results['by_county'] = state + ",,,no State House/Assembly race in" + state + "this election"

    return statewide_state_house_race_results

def get_state_senate_race_results_statewide(state):

    results_statewide = ('State, Candidate, Party, Votes\n')
    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
                                    state.lower())
    statewide_soup = BeautifulSoup(statewide_html.content)
    state_senate_race_div = statewide_soup.find("div", id="senate")
    state_senate_race_urls = state_senate_race_div.find('a')['href']
    for state_senate_race_url in state_senate_race_urls:
        state_senate_race_statewide_html = requests.get(state_senate_race_url['href'])
        state_senate_race_statewide_soup = BeautifulSoup(state_senate_race_statewide_html.content)

        candidates_table = state_senate_race_statewide_soup.find('table', class_= 'eln-results-table')
        candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')
        for row in candidiate_rows:
            candidiate = row.find('td', class_= 'eln-name').find('span', class_='eln-name-display').get_text().strip()
            party = row.find('td', class_= 'eln-party').find('span', class_='eln-party-display').get_text().strip()
            votes = row.find('td', class_= 'eln-votes').get_text().strip().replace(',', '')
            print candidiate,"\n", party,"\n", votes

        counties_table = senate_race_statewide_soup.find('table', 'eln-county-table')
        county_rows = counties_table.find_all('tr', class_='eln-row')
        for county_row in county_rows:
            county = county_row.find('td', 'eln-name').get_text().strip()
            winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
            loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
            print county, winner_votes, loser_votes


def get_senate_race_results_statewide(state):

    results_statewide = ('State, Candidate, Party, Votes\n')
    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
                                    state.lower())
    statewide_soup = BeautifulSoup(statewide_html.content)
    senate_race_div = statewide_soup.find("div", id="senate")
    senate_race_url = senate_race_div.find('a')['href']
    senate_race_statewide_html = requests.get(senate_race_url)
    senate_race_statewide_soup = BeautifulSoup(senate_race_statewide_html.content)

    candidates_table = senate_race_statewide_soup.find('table', class_= 'eln-results-table')
    candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')
    for row in candidiate_rows:
        candidiate = row.find('td', class_= 'eln-name').find('span', class_='eln-name-display').get_text().strip()
        party = row.find('td', class_= 'eln-party').find('span', class_='eln-party-display').get_text().strip()
        votes = row.find('td', class_= 'eln-votes').get_text().strip().replace(',', '')
        print candidiate,"\n", party,"\n", votes

    counties_table = senate_race_statewide_soup.find('table', 'eln-county-table')
    county_rows = counties_table.find_all('tr', class_='eln-row')
    for county_row in county_rows:
        county = county_row.find('td', 'eln-name').get_text().strip()
        winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
        loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
        print county, winner_votes, loser_votes


def get_house_race_results_statewide(state):

    results_statewide = ('State, Candidate, Party, Votes\n')
    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
                                    state.lower())
    statewide_soup = BeautifulSoup(statewide_html.content)
    house_race_div = statewide_soup.find("div", id="house")
    house_race_urls = house_race_div.find_all('a')
    for house_race_url in house_race_urls:
        house_race_statewide_html = requests.get(house_race_url['href'])
        house_race_statewide_soup = BeautifulSoup(house_race_statewide_html.content)

        candidates_table = house_race_statewide_soup.find('table', class_= 'eln-results-table')
        candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')
        for row in candidiate_rows:
            candidiate = row.find('td', class_= 'eln-name').find('span', class_='eln-name-display').get_text().strip()
            party = row.find('td', class_= 'eln-party').find('span', class_='eln-party-display').get_text().strip()
            votes = row.find('td', class_= 'eln-votes').get_text().strip().replace(',', '')
            print candidiate,"\n", party,"\n", votes

        counties_table = house_race_statewide_soup.find('table', 'eln-county-table')
        county_rows = counties_table.find_all('tr', class_='eln-row')
        for county_row in county_rows:
            county = county_row.find('td', 'eln-name').get_text().strip()
            winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
            loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
            print county, winner_votes, loser_votes

def get_presidential_race_results_statewide(state):

    results_statewide = ('State, Candidate, Party, Votes\n')
    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
                                    state.lower())
    statewide_soup = BeautifulSoup(statewide_html.content)
    presidential_race_div = statewide_soup.find("div", id="president")
    presidential_race_url = presidential_race_div.find('a')
    presidential_race_statewide_html = requests.get(presidential_race_url['href'])
    presidential_race_statewide_soup = BeautifulSoup(presidential_race_statewide_html.content)

    candidates_table = presidential_race_statewide_soup.find('table', class_= 'eln-results-table')
    candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')
    for row in candidiate_rows:
        candidiate = row.find('td', class_= 'eln-name').find('span', class_='eln-name-display').get_text().strip()
        party = row.find('td', class_= 'eln-party').find('span', class_='eln-party-display').get_text().strip()
        votes = row.find('td', class_= 'eln-votes').get_text().strip().replace(',', '')
        print candidiate,"\n", party,"\n", votes

    counties_table = presidential_race_statewide_soup.find('table', 'eln-county-table')
    county_rows = counties_table.find_all('tr', class_='eln-row')
    for county_row in county_rows:
        county = county_row.find('td', 'eln-name').get_text().strip()
        winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
        loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
        print county, winner_votes, loser_votes

scrape_state_house_races()
