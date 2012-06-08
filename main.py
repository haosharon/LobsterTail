import categories
from BeautifulSoup import BeautifulStoneSoup as bss
from django.utils import simplejson
import logging
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
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
        self.p('<html>')
        if self.request.get('topic'):
            self.findTopic(self.request.get('topic'))
        elif self.request.get('lat') and self.request.get('long'):
            self.findLocal(self.request.get('lat'), self.request.get('long'))
        elif self.request.get('zip'):
            self.findLocalZip(self.request.get('zip'))
        elif self.request.get('city'):
            self.findLocalCity(self.request.get('city'))
        else:
            self.p('error')
        self.p('</html>')
    
    # Given a location, will find a list of radio stations
    # that have recorded mp3 stories, and another list of radio
    # stations that can be tuned in to.
    def findLocal(self, lat, lon):
        # Get url to query given the lat & long.
        url = self.BASE_URL + 'stations?' + 'lat=' + str(lat) + '&lon=' + str(lon) + '&apiKey=' + self.API_KEY
        result = self.fetchLocalResults(url)
        self.printListToCSV(result)
    
    def findLocalZip(self, zipcode):
        url = self.BASE_URL + 'stations?' + 'zip=' + str(zipcode) + '&apiKey=' + self.API_KEY
        logging.info('url: ' + url)
        result = self.fetchLocalResults(url)
        self.printListToCSV(result)
    
    ## Given a topic (must be one of a predefined list)
    ## Will generate an npr api query for that topic.
    ## Outputs a list of stories with a title and a link to the audio file.
    def findTopic(self, topic):
        query = {}
        topic_id = categories.get_id(topic)
        url = self.BASE_URL + 'query?' + 'id=' + topic_id + '&fields=' + self.FIELDS + '&output=' + self.OUTPUT + '&apiKey=' + self.API_KEY 
        logging.info('url: ' + url)
        result = self.fetchCategoryResults(url)
        self.printListToCSV(result)
    
    # Returns a list of stations that one can tune in to. 
    # List is of the form [[station name, frequency], ...]
    def fetchLocalResults(self, url):
        result = []
        xml = urlfetch.fetch(url).content
        soup = bss(xml)
        stations = soup.findAll('station')
        logging.info('found %s stations' % len(stations))
        for station in stations:
            name = station.find('name')
            band = station.find('band')
            freq = station.find('frequency')
            if name and band and freq:
                logging.info('in')
                res = []
                res.append(str(name.contents[0]))
                channel = band.contents[0] + ' ' + freq.contents[0]
                res.append(str(channel))
                result.append(res)
        return result
                        
    ## Given a query url, takes relevant information from resulting xml.
    ## Returns a list of the form [[title, mp3], [title, mp3], [title, mp3], ...]
    def fetchCategoryResults(self, url):
        result = []
        xml = urlfetch.fetch(url).content
        logging.error('fetched')
        soup = bss(xml)
        stories = soup.findAll('story')
        logging.info('found stories')
        for story in stories:
            story_id = story['id']
            titles = story.findAll('title')
            if len(titles) > 0:
                title = titles[0].contents[0]
                mp3_tag = story.findAll('mp3')
                if len(mp3_tag) > 0:
                    mp3 = mp3_tag[0].contents[0]
                    res = []
                    res.append(str(title + ''))
                    res.append(str(mp3))
                    result.append(res)
        return result
        
    def p(self, string):
        self.response.out.write(string)
                        

    ## Given a list of the form [[..], [..], [..], [..], ...]
    ## prints the items as a csv.
    def printListToCSV(self, items):
        result = ''
        for item in items:
            i = 0
            while i < len(item):
                if i > 0:
                    result += ', '
                result += '"' + item[i] + '"'
                i += 1
            result += '</br>'
        self.response.out.write(result)    

def main():
    application = webapp.WSGIApplication([('/', MainHandler)], debug = True)        
    util.run_wsgi_app(application)

if __name__=='__main__':
    main()
