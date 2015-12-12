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


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.
	
class AppUser(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty()
    email = ndb.StringProperty()

class Resource(ndb.Model):
	"""A main model for representing an individual Guestbook entry."""
	owner = ndb.StringProperty(required=True)
	name = ndb.StringProperty(required=True)
	startTime = ndb.TimeProperty(required=True)
	endTime = ndb.TimeProperty(required=True)
	tags = ndb.StringProperty(repeated=True)

class Reservation(ndb.Model):
	"""A main model for representing an individual Guestbook entry."""
	owner = ndb.StringProperty(required=True)
	name = ndb.StringProperty(required=True)
	startTime = ndb.TimeProperty(required=True)
	endTime = ndb.TimeProperty(required=True)
	date = ndb.DateProperty(required=True)
	
class MainPage(webapp2.RequestHandler):
    def get(self):
		
		myReservations = Reservation.query(Reservation.owner == users.get_current_user().user_id()).get()
#		logging.debug(users.get_current_user().user_id())
		
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		template_values = {
            'myReservations': myReservations,
            'user': user,
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
            resource.owner = AppUser(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        resource.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class NewResources(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('newresources.html')
        self.response.write(template.render())

    def post(self):
		newResource = Resource()
		newResource.owner = users.get_current_user().user_id()
		newResource.name = self.request.get('name')
		newResource.startTime = datetime.datetime.strptime(self.request.get('startTime'), '%H:%M').time()
		newResource.endTime = datetime.datetime.strptime(self.request.get('endTime'), '%H:%M').time()
		newResource.tags = list(set(self.request.get('tags')))
		newResource.put()
		self.redirect('/resources/' + newResource.name)

class Resources(webapp2.RequestHandler):
    def get(self):
		words = (self.request.url).split("/")
		thisResource = Resource.query(Resource.name == words[4]).get()
		allReservations = Reservation.query(Reservation.name == words[4])
		activeReservations = allReservations.filter(ndb.OR(Reservation.date > datetime.date.today(), ndb.AND(Reservation.date == datetime.datetime.now().date(), Reservation.startTime >= datetime.datetime.now().time())))
#		logging.debug(thisResource.count())
		createReservationURL = '/reservations/' + words[4]
		template_values = {
			'thisResource': thisResource,
			'activeReservations': activeReservations,
			'createReservationURL' : createReservationURL,
		}
		
		template = JINJA_ENVIRONMENT.get_template('resources.html')
		self.response.write(template.render(template_values))
		
class NewReservations(webapp2.RequestHandler):
    def get(self):
		template_values = {
			'resourceName': self.request.url,
		}
		template = JINJA_ENVIRONMENT.get_template('newReservations.html')
		self.response.write(template.render(template_values))

    def post(self):
		words = (self.request.url).split("/")
		newReservation = Reservation()
		newReservation.owner = users.get_current_user().user_id()
		newReservation.name = words[4]
		newReservation.startTime = datetime.datetime.strptime(self.request.get('startTime'), '%H:%M').time()
		newReservation.endTime = datetime.datetime.strptime(self.request.get('endTime'), '%H:%M').time()
		newReservation.date = datetime.datetime.strptime(self.request.get('date'), '%d%m%Y').date()
		newReservation.put()
		self.redirect('/resources/' + words[4])

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/resources', NewResources),
    ('/resources/.+', Resources),
    ('/reservations/.+', NewReservations),
], debug=True)