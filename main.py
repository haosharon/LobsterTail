import categories
from BeautifulSoup import BeautifulStoneSoup as bss
import logging
import re
import string

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api import mail


class Twitter(webapp.RequestHandler):
    def get(self):
        self.post()
        
    def post(self):
        STATION = 1111
        STORY = 2222
        if self.request.get('title') and self.request.get('mp3'):
            title = self.request.get('title')
            mp3 = self.request.get('mp3')
            mode = STORY
        elif self.request.get('station') and self.request.get('freq'):
            station = self.request.get('station')
            freq = self.request.get('freq')
            mode = STATION
        else:
            mode = STORY
            title = 'How+the+world+celebrates+national+groundhog+day'
            mp3 = 'mp3link.mp3'
            station = 'WVTF-FM'
            freq = 'FM 89.1'
        
        tweet = ''
        if mode == STATION:
            tweet = 'I am listening to ' + station + ' at ' + freq + '! I found this via StarNews!'
        else:
            title = title.replace('+', ' ')
            tweet = 'I just listened to "' + title + '" via StarNews! You can listen as well at this link: ' + mp3           
        self.response.out.write(tweet)
        mail.send_mail(sender="lmsstarnews@gmail.com",
                       to="tweet@tweetymail.com",
                       subject="",
                       body=tweet)
        self.response.out.write('email sent')

class Facebook(webapp.RequestHandler):
    def get(self):
        self.post()
    
    def post(self):
        #title = self.request.get('title')
        title = 'How+the+world+celebrates+national+groundhog+day'
        title = title.replace('+', ' ')
        mp3 = 'mp3link.mp3'
        string = 'I just listened to "' + title + '" via StarNews! You can listen as well at this link: ' + mp3
        mail.send_mail(sender="lmsstarnews@gmail.com",
                       to="tweet@tweetymail.com",
                       subject="",
                       body=string)
        self.response.out.write('email sent')

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
            self.findTopic(self.request.get('topic'))
        elif self.request.get('lat') and self.request.get('long'):
            self.findLocal(self.request.get('lat'), self.request.get('long'))
        elif self.request.get('zip'):
            self.findLocalZip(self.request.get('zip'))
        elif self.request.get('city'):
            self.findLocalCity(self.request.get('city'))
        else:
            topic = 'art'
            self.findTopic(topic)
            self.p('error')
    
    # Given a location, will find a list of radio stations
    # that have recorded mp3 stories, and another list of radio
    # stations that can be tuned in to.
    def findLocal(self, lat, lon):
        if lat < 0:
            lat += 360
        if lon < 0:
            lon += 360
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
            result += '\n'
        
        self.response.out.write(result)    

def main():
    application = webapp.WSGIApplication([('/', MainHandler), ('/twitter', Twitter)], debug = True)        
    util.run_wsgi_app(application)

if __name__=='__main__':
    main()
