# Add validations
import os
import urllib
import logging
from datetime import datetime

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
	startTimeHour = ndb.IntegerProperty(required=True)
	startTimeMin = ndb.IntegerProperty(required=True)
	startTime = ndb.DateTimeProperty(required=True)
	startTimeDisp = ndb.StringProperty(required=True)
	endTimeHour = ndb.IntegerProperty(required=True)
	endTimeMin = ndb.IntegerProperty(required=True)
	endTime = ndb.DateTimeProperty(required=True)
	endTimeDisp = ndb.StringProperty(required=True)
	tags = ndb.StringProperty(repeated=True)

class Reservation(ndb.Model):
	"""A main model for representing an individual Guestbook entry."""
	owner = ndb.StringProperty(required=True)
	name = ndb.StringProperty(required=True)
	startTimeHour = ndb.IntegerProperty(required=True)
	startTimeMin = ndb.IntegerProperty(required=True)
	startTime = ndb.DateTimeProperty(required=True)
	startTimeDisp = ndb.StringProperty(required=True)
#	endTimeHour = ndb.IntegerProperty(required=True)
#	endTimeMin = ndb.IntegerProperty(required=True)
	durationHour = ndb.IntegerProperty(required=True)
	durationMin = ndb.IntegerProperty(required=True)
	durationTime = ndb.DateTimeProperty(required=True)
	durationDisp = ndb.StringProperty(required=True)
	dateDay = ndb.IntegerProperty(required=True)
	dateMonth = ndb.IntegerProperty(required=True)
	dateYear = ndb.IntegerProperty(required=True)
	date = ndb.DateTimeProperty(required=True)
	dateDisp = ndb.StringProperty(required=True)
	
class MainPage(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			myReservations = Reservation.query(Reservation.owner == users.get_current_user().user_id()).order(Reservation.date).order(Reservation.startTime)
			myResources = Resource.query(Resource.owner == users.get_current_user().user_id())
			allResources = Resource.query()
			logging.debug(users.get_current_user().user_id())
			template_values = {
				'myResources': myResources,
				'myReservations': myReservations,
				'allResources': allResources,
				'user': user,
				'url': url,
				'url_linktext': url_linktext,
			}
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
			template_values = {
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

		StartTimeHour = self.request.get('StartTimeHour')
		StartTimeMin = self.request.get('StartTimeMin')
		StartTimeFormat = self.request.get('StartTimeFormat')
		if StartTimeFormat == 'AM' and StartTimeHour == '12':
			StartTimeHour = '00'
		if StartTimeFormat == 'PM' and StartTimeHour != '12':
			StartTimeHour = str(int(StartTimeHour) + 12)
		newResource.startTimeHour = int(StartTimeHour)
		newResource.startTimeMin = int(StartTimeMin)
		StartTime = StartTimeHour + ':' + StartTimeMin + ':' + StartTimeFormat
		newResource.startTime = datetime.strptime(StartTime, "%H:%M:%p")
		newResource.startTimeDisp = datetime.strftime(newResource.startTime, "%H:%M %p")
		
		EndTimeHour = self.request.get('EndTimeHour')
		EndTimeMin = self.request.get('EndTimeMin')
		EndTimeFormat = self.request.get('EndTimeFormat')	
		if EndTimeFormat == 'AM' and EndTimeHour == '12':
			EndTimeHour = '00'
		if EndTimeFormat == 'PM' and EndTimeHour != '12':
			EndTimeHour = str(int(EndTimeHour) + 12)
		newResource.endTimeHour = int(EndTimeHour)
		newResource.endTimeMin = int(EndTimeMin)
		EndTime = EndTimeHour + ':' + EndTimeMin + ':' + EndTimeFormat
		newResource.endTime = datetime.strptime(EndTime, "%H:%M:%p")
		newResource.endTimeDisp = datetime.strftime(newResource.endTime, "%H:%M %p")

		newResource.tags = (self.request.get('tags')).split()
		newResource.put()
		self.redirect('/resources/' + newResource.name)

class Resources(webapp2.RequestHandler):
    def get(self):
		words = (self.request.url).split("/")
		user = users.get_current_user()

		thisResource = Resource.query(Resource.name == words[4]).get()
		allReservations = Reservation.query(Reservation.name == words[4])
		'''		
		activeReservations = allReservations.filter(ndb.OR(
			Reservation.dateYear > datetime.now().year,
			ndb.AND(Reservation.dateYear == datetime.now().year, 
			Reservation.dateMonth > datetime.now().month),
			ndb.AND(Reservation.dateYear == datetime.now().year, 
			Reservation.dateMonth == datetime.now().month,
			Reservation.dateDay > datetime.now().day),
			ndb.AND(Reservation.dateYear == datetime.now().year, 
			Reservation.dateMonth == datetime.now().month,
			Reservation.dateDay == datetime.now().day,
			Reservation.startTimeHour > datetime.now().hour),
			ndb.AND(Reservation.dateYear == datetime.now().year, 
			Reservation.dateMonth == datetime.now().month,
			Reservation.dateDay == datetime.now().day,
			Reservation.startTimeHour == datetime.now().hour,
			Reservation.startTimeMin == datetime.now().minute),
			))
			'''
		activeReservations = allReservations.filter(ndb.OR(
			Reservation.date > datetime.now(),
			ndb.AND(Reservation.date == datetime.now(), 
			Reservation.startTime > datetime.now()),
			))

		logging.debug(words)
		logging.debug(allReservations.count())
		logging.debug(activeReservations.count())
		createReservationURL = '/reservations/' + words[4]
		template_values = {
			'user': user,
			'thisResource': thisResource,
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

		StartTimeHour = self.request.get('StartTimeHour')
		StartTimeMin = self.request.get('StartTimeMin')
		StartTimeFormat = self.request.get('StartTimeFormat')
		if StartTimeFormat == 'AM' and StartTimeHour == '12':
			StartTimeHour = '00'
		if StartTimeFormat == 'PM' and StartTimeHour != '12':
			StartTimeHour = str(int(StartTimeHour) + 12)
		newReservation.startTimeHour = int(StartTimeHour)
		newReservation.startTimeMin = int(StartTimeMin)
		StartTime = StartTimeHour + ':' + StartTimeMin + ':' + StartTimeFormat
		newReservation.startTime = datetime.strptime(StartTime, "%H:%M:%p")
		newReservation.startTimeDisp = datetime.strftime(newReservation.startTime, "%H:%M %p")

		DurationHour = self.request.get('DurationHour')
		DurationMin = self.request.get('DurationMin')
		newReservation.durationHour = int(DurationHour)
		newReservation.durationMin = int(DurationMin)
		DurationTime = DurationHour + ':' + DurationMin
		newReservation.durationTime = datetime.strptime(DurationTime, "%H:%M")
		newReservation.durationDisp = datetime.strftime(newReservation.durationTime, "%H hrs %M mins")


		DateDay = self.request.get('DateDay')
		DateMonth = self.request.get('DateMonth')
		DateYear = self.request.get('DateYear')
		newReservation.dateDay = int(DateDay)
		newReservation.dateMonth = int(DateMonth)
		newReservation.dateYear = int(DateYear)
		Date = DateDay + ':' + DateMonth + ':' + DateYear
		newReservation.date = datetime.strptime(Date, "%d:%m:%Y")
		newReservation.dateDisp = datetime.strftime(newReservation.date, "%a, %d %b, %Y")

		newReservation.put()
		self.redirect('/resources/' + words[4])

class Tags(webapp2.RequestHandler):
    def get(self):
		words = (self.request.url).split("/")
		user = users.get_current_user()
		tag = words[4]

		taggedResources = Resource.query(Resource.tags == words[4])
		
		template_values = {
			'tag': tag,
			'taggedResources': taggedResources,
		}
		
		template = JINJA_ENVIRONMENT.get_template('tags.html')
		self.response.write(template.render(template_values))

class DelReservations(webapp2.RequestHandler):
	def post(self):
		reservationKey = ndb.Key(urlsafe=self.request.get('reservationKey'))
		logging.debug(reservationKey)
		reservationKey.delete()
		self.redirect('/')
		
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/resources', NewResources),
    ('/resources/.+', Resources),
    ('/reservations', DelReservations),
    ('/reservations/.+', NewReservations),
    ('/tags/.+', Tags),
], debug=True)