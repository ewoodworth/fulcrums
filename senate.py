from lxml import html
import requests

def get_tree(state):
    '''Given a state name, retreive the tree from the NYT Election coverage 
    pages containing the html for senate races in that state.'''

    state_page = requests.get('http://www.nytimes.com/elections/results/' + state)
    state_tree = html.fromstring(state_page.content)
    senator_1_fullname = state_tree.xpath('//*[@id="ca-8516-2016-11-08"]/div/div[1]/div[2]/table/tbody/tr[1]/td[2]/span/span[4]')
    senator_2_fullname = state_tree.xpath('//*[@id="ca-8516-2016-11-08"]/div/div[1]/div[2]/table/tbody/tr[2]/td[2]/span/span[4]')
    senator_1_last = senator_1_fullname.split()[1:]
    senator_2_last = senator_2_fullname.split()[1:]
    senator1 = "-".join(senator_1_last)
    senator2 = "-".join(senator_2_last)
    #NYT uses two formats for senate races, one with the names of the two top candidates, one ith the district number
    senate_page_names = requests.get('http://www.nytimes.com/elections/results/' + state + '-senate-' + senator1 + '-' + senator2)
    senate_page_districts = requests.get('http://www.nytimes.com/elections/results/' + state + '-senate')
    senate_tree_names = html.fromstring(senate_page_names.content)
    senate_tree_districts = html.fromstring(senate_page_districts.content)
    if senate_tree_names.xpath('//*[@id="abColumn"]/div[1]/h2/text()') != 'Page Not Found':
        tree = senate_tree_names
    else:
        tree = senate_tree_districts
    return tree

def scrape_state_overview(state):
    '''Given a xpath tree, return a dictionary of regional details about a senate 
    race. Dictionary looks like {state:[[candidate_a],[candidate_b]...]}
    Asterisk after candidate name indicates an incumbant.'''

    tree = get_tree(state)
    race_results_state = {}
    race_header = ['~Candidate~', '~Party~', '~Votes~', '~Percent~']
    race_results_state[state] = [race_header]
    for row in input_rows:
        candidate = tree.xpath('//*[@id="eln-election-page"]/div/div[2]/div[1]/div/table/tbody/tr[' + row + ']/td[1]/span/span[4]')
        party = tree.xpath('//*[@id="eln-election-page"]/div/div[2]/div[1]/div/table/tbody/tr[' + row + ']/td[2]/span[2]')
        votes = tree.xpath('//*[@id="eln-election-page"]/div/div[2]/div[1]/div/table/tbody/tr[' + row + ']/td[3]')
        percent = tree.xpath('//*[@id="eln-election-page"]/div/div[2]/div[1]/div/table/tbody/tr[' + row + ']/td[4]')
        race_results_state[state].append([candidate, party, votes, percent])
    return race_results_state

def scrape_regional_details(state):
    '''Given a xpath tree, return a dictionary of regional details about a 
    senate race. Dictionary looks like {state: [town name, winner votes, loser votes]}'''

    tree = get_tree(state)
    race_results_regional = {}
    # senate_votes_by_town = state: [[town, winner, loser], [next], [next]...]
    winner = '//*[@id="eln-election-page"]/div/div[2]/div[4]/div/table/thead/tr/th[2]'
    loser = '//*[@id="eln-election-page"]/div/div[2]/div[4]/div/table/thead/tr/th[3]'
    region_header = ['Town or County Name', winner, loser]
    race_results_regional[state] = [region_header]
    for row in input_rows:
        town = tree.xpath('//*[@id="eln-election-page"]/div/div[2]/div[4]/div/table/tbody/tr[' + row + ']/td[1]')
        winner_votes = tree.xpath('//*[@id="eln-election-page"]/div/div[2]/div[4]/div/table/thead/tr' + row + '/td[2]')
        loser_votes = tree.xpath('//*[@id="eln-election-page"]/div/div[2]/div[4]/div/table/tbody/tr[' + row + ']/td[3]/div')
        race_results_regional[state].append([town, winner_votes, loser_votes])
    return race_results_regional



#INPUT ROWS REMAINS UNDEFINED