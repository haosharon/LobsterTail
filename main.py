import categories
import urllib2
from BeautifulSoup import BeautifulStoneSoup

from google.appengine.ext import webapp

class MainHandler(webapp.RequestHandler):
    API_KEY = 'MDA5NTMyMTcyMDEzMzgzMTYwMTU1ZDhlOA001'
    BASE_URL = 'http://api.npr.org/query?'
    FIELDS = 'title,audio'
    OUTPUT = 'NPRML'
    
    def post(self):
        if self.request.get('topic'):
            # user wants to hear a topic.
        elif self.request.get('lat') and self.request.get('long'):
            # user wants to hear local news.
    
    ## Given a topic (must be one of a predefined list)
    ## Will generate an an npr api query for that topic.
    ## Outputs a list of stories with a title and a link to the audio file.
    def findTopic(topic):
        query = {}
        topic_id = categories.get_id(topic)
        query['id'] = topic_id
        query['fields'] = FIELDS
        query['output'] = OUTPUT
        query['apiKey'] = API_KEY
        url = buildQuery(query)
        
    def fetchResults(url):
        file = urllib2.urlopen(url)
        data = file.read()
        file.close()
        
    
    def buildQuery(query):
        url = ''
        url += BASE_URL
        count = 0
        for key in query.keys():
            if count > 0:
                url += '&'
            url += key
            url += '='
            url += query[key]
            count ++
        return url
        
            
        
    
    