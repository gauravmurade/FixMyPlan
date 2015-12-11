# Add validations
import os
import urllib
import logging
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)
	
class AppUser(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Resource(ndb.Model):
	"""A main model for representing an individual Guestbook entry."""
	appUser = ndb.StructuredProperty(AppUser)
	content = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)
	name = ndb.StringProperty(required=True)
	startTime = ndb.TimeProperty(required=True)
	endTime = ndb.TimeProperty(required=True)
	tags = ndb.StringProperty(repeated=True)

class Reservation(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    appUser = ndb.StructuredProperty(AppUser)
    resource = ndb.StructuredProperty(Resource)
	startTime = ndb.TimeProperty(required=True)
	endTime = ndb.TimeProperty(required=True)
    date = ndb.DateTimeProperty()
	
class MainPage(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        resources_query = Resource.query(
            ancestor=guestbook_key(guestbook_name)).order(-Resource.date)
        resources = resources_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'resources': resources,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        resource = Resource(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            resource.appUser = AppUser(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        resource.content = self.request.get('content')
        resource.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class NewResources(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('newresources.html')
        self.response.write(template.render())

    def post(self):
		newResource = Resource()
		newResource.name = self.request.get('name')
		newResource.startTime = datetime.datetime.strptime(self.request.get('startTime'), '%H:%M').time()
		newResource.endTime = datetime.datetime.strptime(self.request.get('endTime'), '%H:%M').time()
		newResource.tags = list(self.request.get('tags'))
		newResource.put()
		self.redirect('/resources/' + newResource.name)

class Resources(webapp2.RequestHandler):
    def get(self):
		words = (self.request.url).split("/")		
#		logging.debug("\n" + words[4])
		currResources = Reservation.query(Resource.name == words[4])
#		currResources = Resource.query(Resource.name == words[4])
#		for currResource in currResources:
#			logging.debug("\n" + currResource.name)
		
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/resources', NewResources),
    ('/resources/.+', Resources),
], debug=True)