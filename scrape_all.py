from bs4 import BeautifulSoup
import urllib
import lxml
import requests
import pprint


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

PARTIES = ["Constitution","Democrat","Green","Independent","Independent American",
           "Libertarian","Liberty Union","Mountain Party","P.S.L.","Pacific Green",
           "Pacifist","Party","Peace and Freedom","Petitioning Candidate","Reform",
           "Republican","Socialist U.S.A.","Socialist Workers",
           "Veteran's Party of America","Workers World"]

THIRD_PARTIES = ["Constitution","Green","Independent","Independent American",
           "Libertarian","Liberty Union","Mountain Party","P.S.L.","Pacific Green",
           "Pacifist","Party","Peace and Freedom","Petitioning Candidate","Reform",
           "Socialist U.S.A.","Socialist Workers", "Veteran's Party of America",
           "Workers World"]

def record():
    for race in RACES:
        statewide_data = ""
        local_data = ""
        race_results = {}
        race_results[race] = {}
        for state in STATES:
            print state, "Start", race
            race_results[race][state] = get_race_results(state, race)
            print state, "Complete"

        # text_file = open('Race_Results/statewide_' + race + '_results.txt', 'w')
        # text_file.write(statewide_data)
        # text_file.close()

        # text_file = open('Race_Results/local_' + race + '_results.txt', 'w')
        # text_file.write(local_data)
        # text_file.close()

def get_race_results(state, race):
    """ For a given 'State' and 'race' returns a dictionary 
    [STATE][DISTRICT][COUNTY][CANDIDIATE][ATTRIBUTE]: attribute value
     """

    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + \
                                    state.lower())
    statewide_soup = BeautifulSoup(statewide_html.content, "lxml")
    race_div = statewide_soup.find("div", id=race)
    race_results = {}

    # check that this particular race exists at all this election
    if race_div:
        
        #P/S races cover the whole state (no districts)
        #from this conditional, spit out list of race urls. In case os P/S is list of one
        if race == 'president' or race == 'senate':
            race_urls = [race_div.find('a')['href']]
        else:
            race_districts = race_div.find_all('td', class_="eln-winner")
            race_urls = [district.find('a')['href'] for district in race_districts]

        for url in race_urls:
            race_districtwide_html = requests.get(url)
            race_districtwide_soup = BeautifulSoup(race_districtwide_html.content, "lxml")
            #GET THE DISTRICT NAME OR NUMBER TRACKING THAT P/S ONLY HAVE ONE DISTRICT
            if race == 'president' or race == 'senate':
                district = 'statewide'
            else:
                if race_districtwide_soup.find('h1', class_='eln-headline'):
                    state_normal = state.replace("-", " ")
                    if state == 'Massachusetts' or state =='Vermont':
                        #YES, I COULD FIX ALL THE FORTHCOMING UNICODE BALONEY BY SWITCHING TO PYTHON 3. ONE THING AT A TIME.
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
                                                         ).replace(u'\u2013', '-'
                                                         ).replace(state_normal, ""
                                                         ).strip(
                                                         )
                    else:
                        district_header = race_districtwide_soup.find('h1', class_='eln-headline'
                                     ).get_text()
                        district_digits = [char for char in district_header if char.isdigit()]
                        district = "".join(district_digits)
                        district = int(district)
            race_results[district] = {}
            candidates_table = race_districtwide_soup.find('table', class_= 'eln-results-table')
            candidate_rows = candidates_table.find_all('tr', class_= 'eln-row')
            #GET THE CANDIDIATE INFO FOR THAT DISTRICT
            race_results[district]['districtwide'] = {}
            for row in candidate_rows:
                candidate_name = row.find('td', class_= 'eln-name'
                                ).find('span', class_='eln-name-display'
                                ).get_text(
                                ).strip(
                                ).replace(u'\u2019', "'"
                                ).replace(u'\u2013', '-'
                                ).replace(u'\xe1', 'a'
                                ).replace(u'\xe9', 'e'
                                ).replace(u'\xfa', 'i'
                                ).replace(u'\xf3', 'o'
                                ).replace(u'\xfa', 'u')
                last_name = row.find('span', class_='eln-last-name'
                              ).get_text(
                              ).strip(
                              ).replace(u'\u2019', "'"
                              ).replace(u'\u2013', '-'
                              ).replace(u'\xe1', 'a'
                              ).replace(u'\xe9', 'e'
                              ).replace(u'\xfa', 'i'
                              ).replace(u'\xf3', 'o'
                              ).replace(u'\xfa', 'u'
                              ).replace('*', '')

                candidate_party = row.find('td', class_= 'eln-party'
                          ).find('span', class_='eln-party-display'
                          ).get_text(
                          ).replace(u'\u2019', "'"
                          ).replace(u'\u2013', '-'
                          ).strip()

                votes = row.find('td', class_= 'eln-votes'
                          ).get_text(
                          ).strip(
                          ).replace(',', '')

                #CREATE SPACE FOR THE BASIC DISTRICTWIDEWIDE ENTRY FOR A CANDIDATE. THIS WILL HAPPEN ONCE PER DISTRICT PER CANDIDIATE
                race_results[district]['districtwide'][last_name] = {}

                #DEFINE THE BASIC DISTRICTWIDE ENTRY FOR A CANDIDATE. THIS WILL HAPPEN ONCE PER DISTRICT PER CANDIDIATE
                race_results[district]['districtwide'][last_name]['votes'] = votes
                race_results[district]['districtwide'][last_name]['name'] = candidate_name
                race_results[district]['districtwide'][last_name]['last'] = last_name
                race_results[district]['districtwide'][last_name]['party'] = candidate_party

                #UNCONTESTED RACES GET DEFINED ON THE STAEWIDE PAGE, SO THIS HAS TO HAPPEN IN THIS LOOP
                uncontested = row.find('span', class_='eln-uncontested-label')

                if uncontested:
                    race_results[district]['districtwide'][last_name]['votes'] = "Uncontested Race"

            if race_districtwide_soup.find('table', 'eln-county-table'):
                counties_table = race_districtwide_soup.find('table', 'eln-county-table')
                county_rows = counties_table.find_all('tr', class_='eln-row')

                for county_row in county_rows:
                    county = county_row.find('td', 'eln-name'
                                      ).get_text(
                                      ).replace(u'\u2019', "'"
                                      ).replace(u'\u2013', '-'
                                      ).strip()
                    winner = counties_table.find_all('th', class_='eln-candidate'
                                       )[0].get_text(
                                          ).strip(
                                          ).replace(u'\xe1', 'a'
                                          ).replace(u'\xe9', 'e'
                                          ).replace(u'\xed', 'i'
                                          ).replace(u'\xf3', 'o'
                                          ).replace(u'\xed', 'u')
                    winner_votes = county_row.find('td', 'eln-candidate'
                                            ).get_text(
                                            ).strip(
                                            ).replace(',', '')
                    loser = counties_table.find_all('th', class_='eln-candidate'
                                      )[1].get_text(
                                         ).strip(
                                         ).replace(u'\xe1', 'a'
                                         ).replace(u'\xe9', 'e'
                                         ).replace(u'\xed', 'i'
                                         ).replace(u'\xf3', 'o'
                                         ).replace(u'\xed', 'u')
                    loser_votes = county_row.find('td', 'eln-last-candidate'
                                           ).get_text(
                                           ).strip(
                                           ).replace(',', '')

                    race_results[district][county] = {}
                    race_results[district][county][winner] = {}
                    race_results[district][county][loser] = {}

                    race_results[district][county][winner]['name'] = race_results[district]['districtwide'][winner]['name']
                    race_results[district][county][winner]['last'] = race_results[district]['districtwide'][winner]['last']
                    race_results[district][county][winner]['party'] = race_results[district]['districtwide'][winner]['party']
                    race_results[district][county][winner]['votes'] = winner_votes

                    race_results[district][county][loser]['name'] = race_results[district]['districtwide'][loser]['name']
                    race_results[district][county][loser]['last'] = race_results[district]['districtwide'][loser]['last'] 
                    race_results[district][county][loser]['party'] = race_results[district]['districtwide'][loser]['party']
                    race_results[district][county][loser]['votes'] = loser_votes

            elif uncontested is not None:
                race_results[district] = "No county level data from NYT"

    else:
        race_results = "No " + race + " race in" + state + "this election"

    pprint.pprint(race_results)
    return race_results

record()