from bs4 import BeautifulSoup
import urllib
import lxml
import requests


# STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
#         'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 
#         'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
#         'Maryland', 'Massachusetts', 'Minnesota', 'Mississippi',
#         'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New-Hampshire',
#         'New-Mexico', 'New-York', 'North-Carolina', 'North-Dakota', 'Ohio', 
#         'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode-Island', 'South-Carolina',
#         'South-Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
#         'Washington', 'West-Virginia', 'Wisconsin', 'Wyoming']

STATES = ['California']

RACES = ['president', 'senate', 'house', 'state-house', 'state-senate']


# def scrape(race, state):
#     scraping_scripts = {
#                     'president': get_presidential_race_results,
#                     'senate': get_senate_race_results,
#                     'house': get_house_race_results,
#                     'state_house': get_state_house_race_results,
#                     'state_senate': get_state_senate_race_results,
#                     }

#     fn_to_call = scraping_scripts[race]
#     return fn_to_call(state)

def record():
    for race in RACES:
        statewide_data = ""
        local_data = ""
        for state in STATES:
            race_data_dict = get_race_results(state, race)
            print race_data_dict
            statewide_data += str(race_data_dict['statewide'])
            local_data += str(race_data_dict['local'])

        text_file = open('Race_Results/statewide_' + race + '_results.txt', 'w')
        text_file.write(statewide_data)
        text_file.close()

        text_file = open('Race_Results/local_' + race + '_results.txt', 'w')
        text_file.write(local_data)
        text_file.close()


def get_race_results(state, race):
    """ For a given 'State' return a dictionary with keys 'statewide' and 
    'local' which are two csv formatted strings:'State, District, 
    Candidate Name, Party, Votes, Last Name \n' and 'State, District, County Name, 
    Winner Votes, Loser Votes' """

    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
                                    state.lower())
    statewide_soup = BeautifulSoup(statewide_html.content, "lxml")
    race_div = statewide_soup.find("div", id=race)
    race_results_local = ""
    race_results = {}
    # local_results_dict = {}

    if race_div:
        if race == 'president' or race == 'senate':
            race_urls = [race_div.find('a')['href']]
            race_results_statewide = 'State, Candidate, Party, Votes, Last Name\n'
        else:
            race_districts = race_div.find_all('td', class_="eln-winner")
            race_urls = [district.find('a')['href'] for district in race_districts]
            race_results_statewide = 'State, District, Candidate, Party, Votes, Last Name\n'

        for url in race_urls:
            race_districtwide_html = requests.get(url)
            race_districtwide_soup = BeautifulSoup(race_districtwide_html.content, "lxml")

            if race_districtwide_soup.find('h1', class_='eln-headline'):
                district = race_districtwide_soup.find('h1', class_='eln-headline'
                                                 ).get_text(
                                                 ).split(":"
                                                 )[0].replace("Results", ""
                                                 ).replace("District", ""
                                                 ).replace("U.S.",""
                                                 ).replace("House", ""
                                                 ).replace("State Assembly", ""
                                                 ).replace("Senate",""
                                                 ).replace("State",""
                                                 ).replace("Presidential",""
                                                 ).replace("Race",""
                                                 ).replace(state, ""
                                                 ).strip(
                                                 )
                # local_results_dict[district] = {}
            else:
                district = ''

            candidates_table = race_districtwide_soup.find('table', class_= 'eln-results-table')
            candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')

            candidate_affiliation = {}

            for row in candidiate_rows:
                candidiate = row.find('td', class_= 'eln-name'
                                ).find('span', class_='eln-name-display'
                                ).get_text(
                                ).strip(
                                ).replace(u'\xe1', 'a'
                                ).replace(u'\xe9', 'e'
                                ).replace(u'\xed', 'i'
                                ).replace(u'\xf3', 'o'
                                ).replace(u'\xed', 'u')
                last_name = row.find('span', class_='eln-last-name'
                              ).get_text(
                              ).strip(
                              ).replace(u'\xe1', 'a'
                              ).replace(u'\xe9', 'e'
                              ).replace(u'\xed', 'i'
                              ).replace(u'\xf3', 'o'
                              ).replace(u'\xed', 'u'
                              ).replace('*', '')
                party = row.find('td', class_= 'eln-party'
                          ).find('span', class_='eln-party-display'
                          ).get_text(
                          ).strip()
                votes = row.find('td', class_= 'eln-votes'
                          ).get_text(
                          ).strip(
                          ).replace(',', '')
                race_results_statewide += state + ',' + district + ',' + candidiate + ',' + \
                                party + ',' + votes + ',' + last_name + '\n'
                candidate_affiliation[last_name] = party
                uncontested = row.find('span', class_='eln-uncontested-label')

            if uncontested:
                race_results_local = state + ',' + district + ',uncontested race\n'
            elif race_districtwide_soup.find('table', 'eln-county-table'):
                counties_table = race_districtwide_soup.find('table', 'eln-county-table')
                county_rows = counties_table.find_all('tr', class_='eln-row')
                winner = counties_table.find_all('th', class_='eln-candidate'
                                   )[0].get_text(
                                      ).strip(
                                      ).replace(u'\xe1', 'a'
                                      ).replace(u'\xe9', 'e'
                                      ).replace(u'\xed', 'i'
                                      ).replace(u'\xf3', 'o'
                                      ).replace(u'\xed', 'u')
                loser = counties_table.find_all('th', class_='eln-candidate'
                                  )[1].get_text(
                                     ).strip(
                                     ).replace(u'\xe1', 'a'
                                     ).replace(u'\xe9', 'e'
                                     ).replace(u'\xed', 'i'
                                     ).replace(u'\xf3', 'o'
                                     ).replace(u'\xed', 'u')
                winning_party = candidate_affiliation[winner]
                losing_party = candidate_affiliation[loser]
                race_results_local += ('State, District, County,' + winner + ' Votes (' 
                                      + winning_party + '),' + loser + ' Votes (' + 
                                      losing_party + '),\n')

                for county_row in county_rows:
                    county = county_row.find('td', 'eln-name'
                                      ).get_text(
                                      ).strip()
                    # local_results_dict[district][county] = {}
                    winner_votes = county_row.find('td', 'eln-candidate'
                                            ).get_text(
                                            ).strip(
                                            ).replace(',', '')
                    loser_votes = county_row.find('td', 'eln-last-candidate'
                                           ).get_text(
                                           ).strip(
                                           ).replace(',', '')
                    # local_results_dict[district][county][winning_party] = []
                    # local_results_dict[district][county][losing_party] = []
                    # local_results_dict[district][county][winning_party].append([winner, votes])
                    # local_results_dict[district][county][losing_party].append([loser, votes])
                    # local_results_dict[district][county]['Republican']
                    # local_results_dict[district][county]['Democrat']           this is valuable but i need to find all options for party first
                    race_results_local += (state + ',' + district + ',' + county + 
                                          ',' + winner_votes + ',' + loser_votes + '\n')
            else:
                race_results_local += state + ',' + district + ',no county level data from NYT'

        race_results['statewide'] = race_results_statewide
        race_results['local'] = race_results_local

    else:
        race_results['statewide'] = state + ",,No " + race + " race in" + state + "this election"
        race_results['local'] = state + ",,,No " + race + " race in" + state + "this election"

    print local_results_dict
    return race_results

record()