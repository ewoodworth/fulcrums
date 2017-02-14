 #US HOUSE OF REPS WITH COUNTY
    while tree.xpath('//*[@id="abColumn"]/div[1]/h2/text()') != 'Page Not Found':
        page = requests.get('http://www.nytimes.com/elections/results/' + state + '-house-district-' + district)
        tree = html.fromstring(page.content)
        district += 1