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
    race_results = {}

    if race_div:
        print race      
        if race == 'president' or 'senate':
            race_urls = [race_div.find('a')['href']]
        else:
            race_districts = race_div.find_all('td', class_="eln-winner")
            print len(race_districts), "NUMBER OF DISTRICTS"
            race_urls = [district.find('a')['href'] for district in race_districts]
        print race_urls

        race_results_statewide = 'State, District, Candidate, Party, Votes, Last Name\n'

        for url in race_urls:
            print url
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
            else:
                district = ','

            candidates_table = race_districtwide_soup.find('table', class_= 'eln-results-table')
            candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')

            candidate_affiliation = {}

            for row in candidiate_rows:
                candidiate = row.find('td', class_= 'eln-name'
                                ).find('span', class_='eln-name-display'
                                ).get_text(
                                ).strip()
                last_name = row.find('span', class_='eln-last-name'
                              ).get_text(
                              ).strip(
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
                                      ).strip()
                loser = counties_table.find_all('th', class_='eln-candidate'
                                  )[1].get_text(
                                     ).strip()
                winning_party = candidate_affiliation[winner]
                loser_party = candidate_affiliation[loser]
                race_results_local = ('State, District, County,' + winner + ' Votes (' 
                                      + winning_party + '),' + loser + ' Votes (' + 
                                      loser_party + '),\n')

                for county_row in county_rows:
                    county = county_row.find('td', 'eln-name'
                                      ).get_text(
                                      ).strip()
                    winner_votes = county_row.find('td', 'eln-candidate'
                                            ).get_text(
                                            ).strip(
                                            ).replace(',', '')
                    loser_votes = county_row.find('td', 'eln-last-candidate'
                                           ).get_text(
                                           ).strip(
                                           ).replace(',', '')
                    race_results_local += (state + ',' + district + ',' + county + 
                                          ',' + winner_votes + ',' + loser_votes + '\n')
            else:
                race_results_local = state + ',' + district + ',no county level data from NYT'

        race_results['statewide'] = race_results_statewide
        race_results['local'] = race_results_local

    else:
        race_results['statewide'] = state + ",,No " + race + " race in" + state + "this election"
        race_results['local'] = state + ",,,No " + race + " race in" + state + "this election"

    print race_results
    return race_results

# def get_state_senate_race_results(state):
#     """ For a given 'State' return a dictionary with keys 'statewide' and 
#     'local' which are two csv formatted strings:'State, District, 
#     Candidate Name, Party, Votes, Last Name \n' and 'State, District, County Name, 
#     Winner Votes, Loser Votes' """

#     results_statewide = ('State, Candidate, Party, Votes\n')
#     statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
#                                     state.lower())
#     statewide_soup = BeautifulSoup(statewide_html.content, "lxml")
#     state_senate_race_div = statewide_soup.find("div", id="state-senate")
#     statewide_state_senate_race_results = {}

#     if state_senate_race_div:
#         state_senate_race_districts = state_senate_race_div.find_all('td', class_="eln-winner")
#         state_senate_race_results = 'State, District, Candidate, Party, Votes, Last Name\n'

#         for state_senate_race_district in state_senate_race_districts:
#             state_senate_race_url = state_senate_race_district.find('a')['href']
#             state_senate_race_districtwide_html = requests.get(state_senate_race_url)
#             state_senate_race_districtwide_soup = BeautifulSoup(state_senate_race_districtwide_html.content, "lxml")

#             district = state_senate_race_districtwide_soup.find('h1', class_='eln-headline'
#                                                      ).get_text(
#                                                      ).split(":"
#                                                      )[0].replace(" State Senate Results", ""
#                                                      ).replace("District", ""
#                                                      ).replace(state, ""
#                                                      ).strip(
#                                                      )
#             candidates_table = state_senate_race_districtwide_soup.find('table', class_= 'eln-results-table')
#             candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')
#             print district
#             candidate_affiliation = {}

#             for row in candidiate_rows:
#                 candidiate = row.find('td', class_= 'eln-name'
#                                 ).find('span', class_='eln-name-display'
#                                 ).get_text(
#                                 ).strip()
#                 last_name = row.find('span', class_='eln-last-name'
#                               ).get_text(
#                               ).strip(
#                               ).replace('*', '')
#                 party = row.find('td', class_= 'eln-party'
#                           ).find('span', class_='eln-party-display'
#                           ).get_text(
#                           ).strip()
#                 votes = row.find('td', class_= 'eln-votes'
#                           ).get_text(
#                           ).strip(
#                           ).replace(',', '')
#                 state_senate_race_results += state + ',' + district + ',' + candidiate + ',' + party + ',' + votes + ',' + last_name + '\n'
#                 candidate_affiliation[last_name] = party
#                 uncontested = row.find('span', class_='eln-uncontested-label')

#             if uncontested:
#                 state_senate_race_results_local = state + ',' + district + ',uncontested race\n'
#             elif state_senate_race_districtwide_soup.find('table', 'eln-county-table'):
#                 counties_table = state_senate_race_districtwide_soup.find('table', 'eln-county-table')
#                 county_rows = counties_table.find_all('tr', class_='eln-row')
#                 winner = counties_table.find_all('th', class_='eln-candidate')[0].get_text().strip()
#                 loser = counties_table.find_all('th', class_='eln-candidate')[1].get_text().strip()
#                 winning_party = candidate_affiliation[winner]
#                 loser_party = candidate_affiliation[loser]
#                 state_senate_race_results_local = 'State, District, County,' + winner + ',' + winning_party + ',Winning Votes,' + loser + ',' + loser_party + ',Losing Votes\n'
#                 state_senate_race_results_local = state + district 
#                 for county_row in county_rows:
#                     county = county_row.find('td', 'eln-name').get_text().strip()
#                     winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
#                     loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
#                     state_senate_race_results_local += county + ',' + winner_votes + ',' + loser_votes +'\n'
#             else:
#                 statewide_state_senate_race_results['local'] = state + ',' + district + ',no county level data from NYT'

#         statewide_state_senate_race_results['statewide'] = state_senate_race_results
#         statewide_state_senate_race_results['local'] = state_senate_race_results_local
#     else:
#         statewide_state_senate_race_results['statewide'] = state + ",,No State House/Assembly race in" + state + "this election"
#         statewide_state_senate_race_results['local'] = state + ",,,No State House/Assembly race in" + state + "this election"

#     print statewide_state_senate_race_results
#     return statewide_state_senate_race_results


# def get_senate_race_results(state):     #####THIS IS SIGNIFICANTLY DIFFERENT
#     """ For a given 'State' return a dictionary with keys 'statewide' and 
#     'local' which are two csv formatted strings:'State, District, 
#     Candidate Name, Party, Votes, Last Name \n' and 'State, District, County Name, 
#     Winner Votes, Loser Votes' """

#     senate_race_results = ('State, Candidate, Party, Votes\n')
#     statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
#                                     state.lower())
#     statewide_soup = BeautifulSoup(statewide_html.content, "lxml")
#     senate_race_div = statewide_soup.find("div", id="senate")
#     statewide_senate_race_results = {}

#     if senate_race_div:
#         senate_race_url = senate_race_div.find('a')['href']
#         senate_race_statewide_html = requests.get(senate_race_url)
#         senate_race_statewide_soup = BeautifulSoup(senate_race_statewide_html.content, "lxml")

#         candidates_table = senate_race_statewide_soup.find('table', class_= 'eln-results-table')
#         candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')
#         candidate_affiliation = {}

#         for row in candidiate_rows:
#             candidiate = row.find('td', class_= 'eln-name'
#                             ).find('span', class_='eln-name-display'
#                             ).get_text(
#                             ).strip()
#             last_name = row.find('span', class_='eln-last-name'
#                           ).get_text(
#                           ).strip(
#                           ).replace('*', '')
#             party = row.find('td', class_= 'eln-party'
#                       ).find('span', class_='eln-party-display'
#                       ).get_text(
#                       ).strip()
#             votes = row.find('td', class_= 'eln-votes'
#                       ).get_text(
#                       ).strip(
#                       ).replace(',', '')
#             senate_race_results += state + ',' + candidiate + ',' + party + ',' + votes + ',' + last_name + '\n'
#             candidate_affiliation[last_name] = party
#             uncontested = row.find('span', class_='eln-uncontested-label')

#         if uncontested:
#             senate_race_results_local = state + ',' + district + ',uncontested race\n'
#         elif senate_race_statewide_soup.find('table', 'eln-county-table'):
#             counties_table = senate_race_statewide_soup.find('table', 'eln-county-table')
#             county_rows = counties_table.find_all('tr', class_='eln-row')
#             winner = counties_table.find_all('th', class_='eln-candidate'
#                                )[0].get_text(
#                                ).strip()
#             loser = counties_table.find_all('th', class_='eln-candidate'
#                               )[1].get_text(
#                                  ).strip()
#             winning_party = candidate_affiliation[winner]
#             loser_party = candidate_affiliation[loser]
#             senate_race_results_local = ('State, District, County,' + winner + 
#                                         ',' + winning_party + ',Winning Votes,' + 
#                                         loser + ',' + loser_party + ',Losing Votes\n')
#             for county_row in county_rows:
#                 county = county_row.find('td', 'eln-name').get_text().strip()
#                 winner_votes = county_row.find('td', 'eln-candidate'
#                                         ).get_text(
#                                         ).strip(
#                                         ).replace(',', '')
#                 loser_votes = county_row.find('td', 'eln-last-candidate'
#                                        ).get_text(
#                                        ).strip(
#                                        ).replace(',', '')
#                 senate_race_results_local += county + ',' + winner_votes + ',' + loser_votes +'\n'
#         else:
#             statewide_senate_race_results['local'] = state + ',' + district + ',no county level data from NYT'

#         statewide_senate_race_results['statewide'] = senate_race_results
#         statewide_senate_race_results['local'] = senate_race_results_local
#     else:
#         statewide_senate_race_results['statewide'] = state + ",,No State senate/Assembly race in" + state + "this election"
#         statewide_senate_race_results['local'] = state + ",,,No State senate/Assembly race in" + state + "this election"

#     print statewide_senate_race_results
#     return statewide_senate_race_results


# def get_house_race_results(state):
#     """ For a given 'State' return a dictionary with keys 'statewide' and 
#     'local' which are two csv formatted strings:'State, District, 
#     Candidate Name, Party, Votes, Last Name \n' and 'State, District, County Name, 
#     Winner Votes, Loser Votes' """

#     results_statewide = ('State, Candidate, Party, Votes\n')
#     statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
#                                     state.lower())
#     statewide_soup = BeautifulSoup(statewide_html.content, "lxml")
#     house_race_div = statewide_soup.find("div", id="house")
#     statewide_house_race_results = {}

#     if house_race_div:
#         house_race_districts = house_race_div.find_all('td', class_="eln-winner")
#         house_race_results = 'State, District, Candidate, Party, Votes, Last Name\n'

#         for house_race_district in house_race_districts:
#             house_race_url = house_race_district.find('a')['href']
#             house_race_districtwide_html = requests.get(house_race_url)
#             house_race_districtwide_soup = BeautifulSoup(house_race_districtwide_html.content, "lxml")

#             district = house_race_districtwide_soup.find('h1', class_='eln-headline'
#                                                      ).get_text(
#                                                      ).split(":"
#                                                      )[0].replace("U.S. House", ""
#                                                      ).replace("District", ""
#                                                      ).replace("Results", ""
#                                                      ).replace(state, ""
#                                                      ).strip(
#                                                      )
#             candidates_table = house_race_districtwide_soup.find('table', class_= 'eln-results-table')
#             candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')

#             candidate_affiliation = {}
#             print district

#             for row in candidiate_rows:
#                 candidiate = row.find('td', class_= 'eln-name'
#                                 ).find('span', class_='eln-name-display'
#                                 ).get_text(
#                                 ).strip()
#                 last_name = row.find('span', class_='eln-last-name'
#                               ).get_text(
#                               ).strip(
#                               ).replace('*', '')
#                 party = row.find('td', class_= 'eln-party'
#                           ).find('span', class_='eln-party-display'
#                           ).get_text(
#                           ).strip()
#                 votes = row.find('td', class_= 'eln-votes'
#                           ).get_text(
#                           ).strip(
#                           ).replace(',', '')
#                 house_race_results += state + ',' + district + ',' + candidiate + ',' + party + ',' + votes + ',' + last_name + '\n'
#                 candidate_affiliation[last_name] = party
#                 uncontested = row.find('span', class_='eln-uncontested-label')

#             if uncontested:
#                 house_race_results_local = state + ',' + district + ',uncontested race\n'
#             elif house_race_districtwide_soup.find('table', 'eln-county-table'):
#                 counties_table = house_race_districtwide_soup.find('table', 'eln-county-table')
#                 county_rows = counties_table.find_all('tr', class_='eln-row')
#                 winner = counties_table.find_all('th', class_='eln-candidate')[0].get_text().strip()
#                 loser = counties_table.find_all('th', class_='eln-candidate')[1].get_text().strip()
#                 winning_party = candidate_affiliation[winner]
#                 loser_party = candidate_affiliation[loser]
#                 house_race_results_local = 'State, District, County,' + winner + ',' + winning_party + ',Winning Votes,' + loser + ',' + loser_party + ',Losing Votes\n'

#                 for county_row in county_rows:
#                     county = county_row.find('td', 'eln-name').get_text().strip()
#                     winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
#                     loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
#                     house_race_results_local += county + ',' + winner_votes + ',' + loser_votes +'\n'
#             else:
#                 statewide_house_race_results['local'] = state + ',' + district + ',no county level data from NYT'

#         statewide_house_race_results['statewide'] = house_race_results
#         statewide_house_race_results['local'] = house_race_results_local
#     else:
#         statewide_house_race_results['statewide'] = state + ",,No State House/Assembly race in" + state + "this election"
#         statewide_house_race_results['local'] = state + ",,,No State House/Assembly race in" + state + "this election"

#     print statewide_house_race_results
#     return statewide_house_race_results


# def get_presidential_race_results(state):     #####THIS IS SIGNIFICANTLY DIFFERENT MATCHES ONLY SENATE
#     """ For a given 'State' return a dictionary with keys 'statewide' and 
#     'local' which are two csv formatted strings:'State, District, 
#     Candidate Name, Party, Votes, Last Name \n' and 'State, District, County Name, 
#     Winner Votes, Loser Votes' """

#     presidential_race_results = ('State, Candidate, Party, Votes\n')
#     statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
#                                     state.lower())
#     statewide_soup = BeautifulSoup(statewide_html.content, "lxml")
#     presidential_race_div = statewide_soup.find("div", id="president")
#     statewide_presidential_race_results = {}

#     if presidential_race_div:
#         presidential_race_url = presidential_race_div.find('a')['href']
#         presidential_race_statewide_html = requests.get(presidential_race_url)
#         presidential_race_statewide_soup = BeautifulSoup(presidential_race_statewide_html.content, "lxml")
        
#         candidates_table = presidential_race_statewide_soup.find('table', class_= 'eln-results-table')
#         candidiate_rows = candidates_table.find_all('tr', class_= 'eln-row')
#         candidate_affiliation = {}

#         for row in candidiate_rows:
#             candidiate = row.find('td', class_= 'eln-name'
#                             ).find('span', class_='eln-name-display'
#                             ).get_text(
#                             ).strip()
#             last_name = row.find('span', class_='eln-last-name'
#                           ).get_text(
#                           ).strip(
#                           ).replace('*', '')
#             party = row.find('td', class_= 'eln-party'
#                       ).find('span', class_='eln-party-display'
#                       ).get_text(
#                       ).strip()
#             votes = row.find('td', class_= 'eln-votes'
#                       ).get_text(
#                       ).strip(
#                       ).replace(',', '')
#             presidential_race_results += state + ',' + candidiate + ',' + party + ',' + votes + ',' + last_name + '\n'
#             candidate_affiliation[last_name] = party
#             uncontested = row.find('span', class_='eln-uncontested-label')

#         if uncontested:
#             presidential_race_results_local = state + ',' + district + ',uncontested race\n'
#         elif presidential_race_statewide_soup.find('table', 'eln-county-table'):
#             counties_table = presidential_race_statewide_soup.find('table', 'eln-county-table')
#             county_rows = counties_table.find_all('tr', class_='eln-row')
#             winner = counties_table.find_all('th', class_='eln-candidate')[0].get_text().strip()
#             loser = counties_table.find_all('th', class_='eln-candidate')[1].get_text().strip()
#             winning_party = candidate_affiliation[winner]
#             loser_party = candidate_affiliation[loser]
#             presidential_race_results_local = 'State, District, County,' + winner + ',' + winning_party + ',Winning Votes,' + loser + ',' + loser_party + ',Losing Votes\n'
#             for county_row in county_rows:
#                 county = county_row.find('td', 'eln-name').get_text().strip()
#                 winner_votes = county_row.find('td', 'eln-candidate').get_text().strip().replace(',', '')
#                 loser_votes = county_row.find('td', 'eln-last-candidate').get_text().strip().replace(',', '')
#                 presidential_race_results_local += county + ',' + winner_votes + ',' + loser_votes +'\n'
#         else:
#             statewide_presidential_race_results['local'] = state + ',' + district + ',no county level data from NYT'

#         statewide_presidential_race_results['statewide'] = presidential_race_results
#         statewide_presidential_race_results['local'] = presidential_race_results_local
#     else:
#         statewide_presidential_race_results['statewide'] = state + ",,No State presidential/Assembly race in" + state + "this election"
#         statewide_presidential_race_results['local'] = state + ",,,No State presidential/Assembly race in" + state + "this election"

#     print statewide_presidential_race_results
#     return statewide_presidential_race_results

record()
