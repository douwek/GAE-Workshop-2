from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2, cgi, os
import urllib
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

providers = {
    'Google'   : 'https://www.google.com/accounts/o8/id',
    'Yahoo'    : 'yahoo.com',
    'MyOpenID' : 'myopenid.com',
}

DEFAULT_PRIKBORD_NAAM = 'default_prikbord'

def prikbord_key(prikbord_naam=DEFAULT_PRIKBORD_NAAM):
    return ndb.Key('Prikbord', prikbord_naam)

class Bericht(ndb.Model):
    gebruiker = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    datum = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        prikbord_naam = self.request.get('prikbord_naam', DEFAULT_PRIKBORD_NAAM)
        berichten_query = Bericht.query(
            ancestor=prikbord_key(prikbord_naam)).order(-Bericht.datum)
        berichten = berichten_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'berichten': berichten,
            'prikbord_naam': urllib.quote_plus(prikbord_naam),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class PrikBord(webapp2.RequestHandler):
    def post(self):
        prikbord_naam = self.request.get('prikbord_naam', DEFAULT_PRIKBORD_NAAM)
        bericht = Bericht(parent=prikbord_key(prikbord_naam))
        if users.get_current_user():
            bericht.gebruiker = users.get_current_user()
        bericht.content = self.request.get('content')
        bericht.put()
        query_params = {'prikbord_naam': prikbord_naam}
        self.redirect('/?' + urllib.urlencode(query_params))

application = webapp2.WSGIApplication([('/', MainPage),('/prik', PrikBord),], debug=True)
