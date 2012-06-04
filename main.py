import categories
from BeautifulSoup import BeautifulStoneSoup as bss

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class MainHandler(webapp.RequestHandler):
    API_KEY = 'MDA5NTMyMTcyMDEzMzgzMTYwMTU1ZDhlOA001'
    BASE_URL = 'http://api.npr.org/'
    FIELDS = 'title,audio'
    OUTPUT = 'NPRML'
    
    ## Mimics post()
    def get(self):
        self.post()
    
    ## Given a method of searching (topic / location) 
    ## finds the results of that search query.
    def post(self):
        if self.request.get('topic'):
            findTopic(self.request.get('topic'))
        elif self.request.get('lat') and self.request.get('long'):
            # user wants to hear local news.
    
    def findLocal(lat, lon):
        query = {}
        query['lat'] = lat
        query['lon'] = lon
        url = buildStationFinder(query)
        result = fetchLocalResults(url)
    
    ## Given a dictionary with latitude and longitude
    ## information, builds a request for a list of stations
    ## nearby.
    def buildStationFinder(dic):
        url = ''
        url += BASE_URL
        url += 'stations?'
        url += 'lat='
        url += dic['lat']
        url += '&lon='
        url += dic['lon']
        url += '&apiKey='
        url += API_KEY
        return url
    
    ## Given a topic (must be one of a predefined list)
    ## Will generate an npr api query for that topic.
    ## Outputs a list of stories with a title and a link to the audio file.
    def findTopic(topic):
        query = {}
        topic_id = categories.get_id(topic)
        query['id'] = topic_id
        query['fields'] = FIELDS
        query['output'] = OUTPUT
        query['apiKey'] = API_KEY
        url = buildQuery(query)
        result = fetchCategoryResults(url)
    
    def fetchLocalResults(url):
        xml = urlfetch.fetch(url).content
        soup = bss(xml)
        
    ## Given a query url, takes relevant information from resulting xml.
    ## Returns a list of the form [[...], [...], [....], [...], ...]
    def fetchCategoryResults(url):
        result = []
        xml = urlfetch.fetch(url).content
        soup = bss(xml)
        stories = soup.findAll('story')
        for story in stories:
            story_id = story['id']
            titles = story.findAll('title')
            if len(titles) > 0:
                title = titles[0].contents[0]
                mp3_tag = story.findAll('mp3')
                if len(mp3_tag) > 0:
                    mp3 = mp3_tag[0].contents[0]
                    res = []
                    res.append(title)
                    res.append(mp3)
                    result.append(res)
        return result
                        

    ## Given a list of the form [[..], [..], [..], [..], ...]
    ## prints the items as a csv.
    def printListToCSV(items):
        result = ''
        for item in items:
            i = 0
            while i < len(item):
                if i > 0:
                    result += ','
                result += item[i]
                i ++
            result += '\n'
        self.response.out.write(result)
        
    ## Builds query given a dictionary of fields.
    def buildQuery(query):
        url = ''
        url += BASE_URL
        url += 'query?'
        count = 0
        for key in query.keys():
            if count > 0:
                url += '&'
            url += key
            url += '='
            url += query[key]
            count ++
        return url
        
            
        
    
    