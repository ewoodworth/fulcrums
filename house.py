from bs4 import BeautifulSoup
import urllib
import lxml
import requests


def get_district_url(state, district='1',winner='None',loser='None'):
    """Given a state and district (and the candidates' last names), return the 
    url of the webpage outlining the district info for that district"""

    statewide_html = requests.get('http://www.nytimes.com/elections/results/' +  \
                                state.lower())
    statewide_page = BeautifulSoup(statewide_html.content)
    all_races = statewide_page.find("div", id="house"
                                        ).find_all("tr", class_='eln-group-row')
    #some district urls have no names in them
    if (
        state == 'Arizona' and district in ['8']) or (
        state == 'Arkansas' and district in ['1', '3', '4']) or (
        state == 'California' and district in ['12', '17', '29', '32', '34', '37', 
                                               '40', '44', '46']) or (
        state == 'Indiana' and district in ['1']) or (
        state == 'Kansas' and district in ['1']) or (
        state == 'Louisiana') or (
        state == 'Massachusetts' and district in ['1', '2']) or (
        state == 'New-York' and district in ['8', '9', '16']) or (
        state == 'Oregon' and district in ['3']) or (
        state == 'Texas' and district in ['4', '5', '11', '13', '16', '19', '20', 
                                            '32', '36']) or (
        state == 'Washington' and district in ['4', '7']) or (
        state == 'Wisconsin' and district in ['4']): 
        
        district_race_url = ('http://www.nytimes.com/elections/results/' + 
                              state.lower() + '-house-district-' + district)
    #some district urls have the loser's name first, then the winner's
    elif (
        state == 'Arizona' and district in ['5']) or (
        state == 'Florida' and district in ['1', '2', '4', '7', '13', '18', '19']) or (
        state == 'Georgia' and district in ['3']) or (
        state == 'Illinois' and district in ['10']) or (
        state == 'Indiana' and district in ['3', '9']) or (
        state == 'Kentucky' and district in ['1']) or (
        state == 'Minnesota' and district in ['2']) or (
        state == 'Nebraska' and district in ['2']) or (
        state == 'Nevada' and district in ['4']) or (
        state == 'New-Hampshire' and district in ['1']) or (
        state == 'New-York' and district in ['19', '22']) or (
        state == 'North-Carolina' and district in ['13']) or (
        state == 'Pennsylvania' and district in ['8', '16']) or (
        state == 'Tennessee' and district in ['8']) or (
        state == 'Virginia' and district in ['2', '5']) or (
        state == 'Wisconsin' and district in ['8']):
        
        district_race_url = ('http://www.nytimes.com/elections/results/' + 
                            state.lower() + '-house-district-' + district + 
                            '-' + loser.lower() + '-' + winner.lower())
    #some district urls are for 'House at Large' with no way to compose the url from the statewide page
    elif state == 'Delaware':
        district_race_url = ('http://www.nytimes.com/elections/results/delaware-house-district-1-rochester-reigle')
    elif state == 'Alaska':
        district_race_url = ('http://www.nytimes.com/elections/results/alaska-house-district-1-young-lindbeck')
    elif state == 'Montana':
        district_race_url = ('http://www.nytimes.com/elections/results/montana-house-district-1-zinke-juneau')
    elif state == 'North-Dakota':
        district_race_url = ('http://www.nytimes.com/elections/results/north-dakota-house-district-1-cramer-iron-eyes')
    elif state == 'South-Dakota':
        district_race_url = ('http://www.nytimes.com/elections/results/south-dakota-house-district-1-noem-hawks')
    elif state == 'Vermont':
        district_race_url = ('http://www.nytimes.com/elections/results/vermont-house-district-1')
    elif state == 'Wyoming':
        district_race_url = ('http://www.nytimes.com/elections/results/wyoming-house-district-1-greene-cheney')
    #most urls take this form
    else:
        district_race_url = ('http://www.nytimes.com/elections/results/' + 
                            state.lower() + '-house-district-' + district + 
                            '-' + winner.lower() + '-' + loser.lower())
    return district_race_url


def get_race_results_by_district(state):
    """Returns a string formatted for csv upload into excel for a given state. 
    Lines are 'state, district, candidate, party, districtwide votes (repated for 
    all candidates in that district) """

    results_by_district = ("State, District, Candidate, Party, Votes\n")

    statewide_html = requests.get('http://www.nytimes.com/elections/results/' + 
                                state.lower())
    statewide_page = BeautifulSoup(statewide_html.content)
    all_races = statewide_page.find("div", id="house"
                            ).find_all("tr", class_='eln-group-row')
    #House at Large races have one url that covers the entire state and a single district
    if str(state) in ['Alaska', 'Delaware','Montana','North-Dakota',
                        'South-Dakota','Vermont','Wyoming']:
        district_race_url = get_district_url(state)
        r = requests.get(district_race_url)
        district_house_soup = BeautifulSoup(r.content)
        district = "1"

        district_candidates = district_house_soup.find("table", 
                                        class_="eln-results-table").find_all("tr", 
                                        class_="eln-row")
        results_by_district += state + ',1'
        for row in district_candidates:
            candidate = row.find("span", class_="eln-name-display"
                        ).get_text(
                        ).strip(
                        ).replace(u"\u00E1", "a"
                        ).replace(u"\u00FA", "u"
                        ).replace(u"\u00E9", "e"
                        )
            party =  row.find("span", class_="eln-party-abbr").get_text().strip()
            votes = row.find("td", class_="eln-votes").get_text().strip(
                    ).replace(',', '')
            results_by_district += ',' + candidate + ',' + party + ',' + votes + '\n'
        return results_by_district
    #'Normal' races have a page per district, from which we want the data
    else:
        for district_row in all_races:
            district = district_row.find("td", class_='eln-seat'
                                    ).get_text(
                                    ).strip()
            candidates = district_row.find_all("td", class_="eln-candidate")
            winner =  candidates[0].find("span", class_="eln-name"
                                    ).get_text(
                                    ).strip(
                                    ).replace("*", ""
                                    ).replace(" ", "-"
                                    ).replace("'", ""
                                    ).replace(u"\u00E1", "a"
                                    ).replace(u"\u00FA", "u"
                                    ).replace(u"\u00E9", "e")
            winner_party = candidates[0].find("span", "eln-party"
                                        ).get_text(
                                        ).strip()

            is_uncontested = district_row.find("span", class_="eln-uncontested-label")
            if is_uncontested:
                results_by_district += (state + ',' + district + ',' + winner+ ',' 
                                        + winner_party + ',uncontested race\n')
            else:
                loser = candidates[1].find("span", class_="eln-name"
                                    ).get_text(
                                    ).strip(
                                    ).replace("*", ""
                                    ).replace(" ", "-"
                                    ).replace("'", ""
                                    ).replace(u"\u00E1", "a"
                                    ).replace(u"\u00FA", "u"
                                    ).replace(u"\u00E9", "e")

                district_race_url = get_district_url(state, district,winner,loser)
                r = requests.get(district_race_url)
                district_house_soup = BeautifulSoup(r.content)

                district_candidates = district_house_soup.find("table", class_="eln-results-table"
                                                        ).find_all("tr", class_="eln-row")
                
                for row in district_candidates:
                    candidate = row.find("span", class_="eln-name-display"
                                ).get_text(
                                ).strip(
                                ).replace(u"\u00E1", "a"
                                ).replace(u"\u00FA", "u"
                                ).replace(u"\u00E9", "e"
                                )
                    party =  row.find("span", class_="eln-party-abbr").get_text().strip()
                    votes = row.find("td", class_="eln-votes").get_text().strip(
                            ).replace(',', '')
                    results_by_district += state + ',' + district + ',' + candidate + ',' + party + ',' + votes + '\n'
        return results_by_district

def get_race_results_by_county(state):
    """Returns a string formatted for csv upload into excel for a given state. 
    Lines are 'state, district, candidate, party, districtwide votes (repated for 
    all candidates in that district' """

    results_by_county = "State, District, County, Winner, Winning Party,  \
                        Winning Votes, Runner Up, Runner Up Party, Runner Up Votes\n"
    r = requests.get('http://www.nytimes.com/elections/results/' + state.lower())
    statewide_page = BeautifulSoup(r.content)
    all_races = statewide_page.find("div", id="house"
                                ).find_all("tr", class_='eln-group-row')

    #"House at Large" races have one district covering the whole state. URL not composable from statewide page
    if str(state) in ['Alaska', 'Delaware','Montana','North-Dakota',
                        'South-Dakota','Vermont','Wyoming']:
        district_race_url = get_district_url(state)
        district = "1"
        r = requests.get(district_race_url)
        house_soup = BeautifulSoup(r.content)

        county_table = house_soup.find("table", 
                                       class_="eln-county-table")
        district_candidates_table = house_soup.find("table", 
                                        class_="eln-results-table").find_all("tr", 
                                        class_="eln-row")

        party_affiliation_dict = {}
        for candidate in district_candidates_table:
            full_name = candidate.find("span", class_="eln-name-display"
                                ).get_text(
                                ).strip()
            last_name = ""
            for name_segment in full_name.split(" ")[-1]:
                if len(name_segment.replace(".", "")) == len(name_segment):
                    last_name += name_segment
            last_name = last_name.replace("*", ""
                                ).replace("'", ""
                                ).replace(u"\u00E1", "a"
                                ).replace(u"\u00FA", "u"
                                ).replace(u"\u00E9", "e")
            party =  candidate.find("span", class_="eln-party-abbr"
                                ).get_text(
                                ).strip()
            party_affiliation_dict[last_name] = party
        print party_affiliation_dict

        if county_table:

            county_header = county_table.find_all("th", class_="eln-header")
            winner = county_header[1].get_text().strip()
            loser = county_header[2].get_text().strip()

            county_rows = county_table.find_all("tr", class_="eln-row")

            for row in county_rows:
                county = row.find("td", class_="eln-name"
                            ).get_text(
                            ).strip()
                winner_votes =  row.find("td", class_="eln-candidate"
                                    ).get_text(
                                    ).strip(
                                    ).replace(',', '')
                if winner == "Renacci":
                    winner_party = "Rep."
                else:
                    winner_party = party_affiliation_dict[winner]
                if loser == "Putman":
                    loser_party = "Dem."
                elif loser == "Iron Eyes":
                    loser_party = "Dem."
                else:
                    loser_party = party_affiliation_dict[loser]
                loser_votes = row.find("td", class_="eln-last-candidate"
                                ).get_text(
                                ).strip(
                                ).replace(',', '')
                results_by_county += state + ',' + district + ',' + county + ',' + \
                                    winner+ ',' + winner_party + ',' + winner_votes + \
                                    ',' + loser + ',' + loser_party+ ',' + loser_votes + '\n'
        else:
            results_by_county += state + ',' + district + ',,no county data at NYT\n'
    else:
        for district_row in all_races:
            district = district_row.find("td", class_='eln-seat'
                                    ).get_text(
                                    ).strip()
            candidates = district_row.find_all("td", class_="eln-candidate")
            winner =  candidates[0].find("span", class_="eln-name"
                                    ).get_text(
                                    ).strip(
                                    ).replace("*", ""
                                    ).replace(" ", "-"
                                    ).replace("'", ""
                                    ).replace(u"\u00E1", "a"
                                    ).replace(u"\u00FA", "u"
                                    ).replace(u"\u00E9", "e")
            winner_party = candidates[0].find("span", "eln-party"
                                        ).get_text(
                                        ).strip() #necessary for uncontested info next
            uncontested = district_row.find("span", class_="eln-uncontested-label")
            if uncontested:
                results_by_county += state + ',' + district + ',,' + winner+ ',' + \
                                        winner_party + ',uncontested race\n'
            else:
                loser = candidates[1].find("span", class_="eln-name"
                                    ).get_text(
                                    ).strip(
                                    ).replace("*", ""
                                    ).replace(" ", "-"
                                    ).replace("'", ""
                                    ).replace(u"\u00E1", "a"
                                    ).replace(u"\u00FA", "u"
                                    ).replace(u"\u00E9", "e")
                district_race_url = get_district_url(state, district, winner, loser)
                r = requests.get(district_race_url)
                house_soup = BeautifulSoup(r.content)

                county_table = house_soup.find("table", 
                                               class_="eln-county-table")
                district_candidates_table = house_soup.find("table", class_="eln-results-table"
                                                        ).find_all("tr", class_="eln-row")

                party_affiliation_dict = {}
                for candidate in district_candidates_table:
                    full_name = candidate.find("span", class_="eln-name-display"
                                        ).get_text(
                                        ).strip()
                    last = []
                    for name_segment in full_name.split(" ")[1:]:
                        if len(name_segment.replace(".", "")) == len(name_segment):
                            last.append(name_segment)
                    last_name = " ".join(last)
                    last_name = last_name.replace("*", ""
                                        # ).replace("'", ""
                                        ).replace(u"\u00E1", "a"
                                        ).replace(u"\u00FA", "u"
                                        ).replace(u"\u00E9", "e")
                    party =  candidate.find("span", class_="eln-party-abbr"
                                        ).get_text(
                                        ).strip()
                    party_affiliation_dict[last_name] = party
                print party_affiliation_dict

                if county_table:

                    county_header = county_table.find_all("th", class_="eln-header")
                    winner = county_header[1].get_text().strip()
                    loser = county_header[2].get_text().strip()

                    county_rows = county_table.find_all("tr", class_="eln-row")

                    for row in county_rows:
                        county = row.find("td", class_="eln-name"
                                    ).get_text(
                                    ).strip()
                        winner_votes =  row.find("td", class_="eln-candidate"
                                            ).get_text(
                                            ).strip(
                                            ).replace(',', '')
                        if winner == "Renacci":
                            winner_party = "Rep."
                        elif winner in ["Ruppersberger", "Clay", "Cleaver", 
                                        "Kuster", "Lujan", "Maloney", "Woolridge"]:
                            winner_party = "Dem."
                        else:
                            winner_party = party_affiliation_dict[winner]
                        if loser in ["Putman", "Iron Eyes", "Kemper", "Dugas", 
                                    "Soules", "Casteen", "Balchunis", "Woolridge"]:
                            loser_party = "Dem."
                        elif loser == "Dew":
                            loser_party = "Rep."
                        else:
                            loser_party = party_affiliation_dict[loser]
                        loser_votes = row.find("td", class_="eln-last-candidate"
                                        ).get_text(
                                        ).strip(
                                        ).replace(',', '')
                        results_by_county += state + ',' + district + ',' + county + ',' + winner+ ',' + winner_party + ',' + winner_votes + ',' + loser + ',' + loser_party+ ',' + loser_votes + '\n'
                else:
                    results_by_county += state + ',' + district + ",,no county data at NYT\n"
    return results_by_county

# get_race_results_by_district('California')
# get_race_results_by_county('California')
# get_district_url('California')