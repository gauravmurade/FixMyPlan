# Punctuation in string inputs
# Check for inequality in filters
# Deploy
# No tag on resource if owner

import os
import urllib
import logging
from datetime import datetime, timedelta
from xml.etree import ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment
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
	
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

class AppUser(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty()
    email = ndb.StringProperty()

class Resource(ndb.Model):
	"""A main model for representing an individual Guestbook entry."""
	owner = ndb.StringProperty(required=True)
	name = ndb.StringProperty(required=True)
	startTimeHour = ndb.StringProperty(required=True)
	startTimeMin = ndb.StringProperty(required=True)
	startTimeFormat = ndb.StringProperty(required=True)
	startTime = ndb.DateTimeProperty(required=True)
	startTimeDisp = ndb.StringProperty(required=True)
	endTimeHour = ndb.StringProperty(required=True)
	endTimeMin = ndb.StringProperty(required=True)
	endTimeFormat = ndb.StringProperty(required=True)
	endTime = ndb.DateTimeProperty(required=True)
	endTimeDisp = ndb.StringProperty(required=True)
	tags = ndb.StringProperty(repeated=True)

class Reservation(ndb.Model):
	"""A main model for representing an individual Guestbook entry."""
	owner = ndb.StringProperty(required=True)
	name = ndb.StringProperty(required=True)
	startTime = ndb.DateTimeProperty(required=True)
	startTimeDisp = ndb.StringProperty(required=True)
	durationTime = ndb.DateTimeProperty(required=True)
	durationDisp = ndb.StringProperty(required=True)
	endTime = ndb.DateTimeProperty(required=True)
	date = ndb.DateTimeProperty(required=True)
	dateDisp = ndb.StringProperty(required=True)
	
class Guestbook(webapp2.RequestHandler):
    def post(self):
 
        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class MainPage(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)

			myReservations = Reservation.query(Reservation.owner == user.email(), ancestor=guestbook_key(guestbook_name))
			myActiveReservations = myReservations.filter(ndb.OR(
				Reservation.date > datetime.today(),
				ndb.AND(Reservation.date == datetime.today(), 
				Reservation.endTime > datetime.now()),
				)).order(Reservation.date).order(Reservation.endTime)
			myResources = Resource.query(Resource.owner == user.email(), ancestor= guestbook_key(guestbook_name))
			allResources = Resource.query(ancestor=guestbook_key(guestbook_name))
			template_values = {
				'myResources': myResources,
				'myActiveReservations': myActiveReservations,
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

class User(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
			myReservations = Reservation.query(Reservation.owner == user.email(), ancestor=guestbook_key(guestbook_name))
			myActiveReservations = myReservations.filter(ndb.OR(
				Reservation.date > datetime.today(),
				ndb.AND(Reservation.date == datetime.today(), 
				Reservation.endTime > datetime.now()),
				)).order(Reservation.date).order(Reservation.endTime)
			myResources = Resource.query(Resource.owner == user.email(), ancestor= guestbook_key(guestbook_name))
			allResources = Resource.query(ancestor=guestbook_key(guestbook_name))
			template_values = {
				'homePage': 0,
				'myResources': myResources,
				'myActiveReservations': myActiveReservations,
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

class NewResources(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			errorNo = 0
			template_values = {
				'errorNo': errorNo,
				'url': url,
				'url_linktext': url_linktext,
			}
			
			template = JINJA_ENVIRONMENT.get_template('newresources.html')
			self.response.write(template.render(template_values))
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

    def post(self):
		# While adding a new resource, name must be entered
		# Resource end time cannot be smaller than start time
		# Resource name should be unique
		ResourceName = self.request.get('name').strip()

		StartTimeHour = self.request.get('StartTimeHour')
		StartTimeMin = self.request.get('StartTimeMin')
		StartTimeFormat = self.request.get('StartTimeFormat')
		StartTime = StartTimeHour + ':' + StartTimeMin + ':' + StartTimeFormat
		ResourceStartTime = datetime.strptime(StartTime, "%I:%M:%p")

		EndTimeHour = self.request.get('EndTimeHour')
		EndTimeMin = self.request.get('EndTimeMin')
		EndTimeFormat = self.request.get('EndTimeFormat')
		EndTime = EndTimeHour + ':' + EndTimeMin + ':' + EndTimeFormat
		ResourceEndTime = datetime.strptime(EndTime, "%I:%M:%p")

		ResourceTags = self.request.get('tags').strip()
		guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)

		checkIfResourceAlreadyExists = Resource.query(Resource.name == ResourceName, ancestor=guestbook_key(guestbook_name))
		
		logging.debug(ResourceName)
		logging.debug(StartTimeHour)
		logging.debug(StartTimeMin)
		logging.debug(StartTimeFormat)
		logging.debug(EndTimeHour)
		logging.debug(EndTimeMin)
		logging.debug(EndTimeFormat)
		logging.debug(ResourceTags)

		errorNo = 0
		if ResourceName == "":
			logging.debug("No name specified")
			errorNo = 1
		elif ResourceEndTime <= ResourceStartTime:
			logging.debug(ResourceEndTime)
			logging.debug(ResourceStartTime)
			errorNo = 2
		elif checkIfResourceAlreadyExists.count() > 0:
			errorNo = 3
		
		if errorNo > 0:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			logging.debug("Yes, there is an error")
			template_values = {
				'errorNo': errorNo,
				'url': url,
				'url_linktext': url_linktext,
				'ResourceName': ResourceName,
				'StartTimeHour': StartTimeHour,
				'StartTimeMin': StartTimeMin,
				'StartTimeFormat': StartTimeFormat,
				'EndTimeHour': EndTimeHour,
				'EndTimeMin': EndTimeMin,
				'EndTimeFormat': EndTimeFormat,
				'ResourceTags': ResourceTags,
			}
			template = JINJA_ENVIRONMENT.get_template('newresources.html')
			self.response.write(template.render(template_values))
		else:
			newResource = Resource(parent=guestbook_key(guestbook_name))
			newResource.owner = users.get_current_user().email()
			newResource.name = ResourceName

			newResource.startTimeHour = StartTimeHour
			newResource.startTimeMin = StartTimeMin
			newResource.startTimeFormat = StartTimeFormat
			newResource.startTime = ResourceStartTime
			newResource.startTimeDisp = datetime.strftime(newResource.startTime, "%I:%M %p")
			
			newResource.endTimeHour = EndTimeHour
			newResource.endTimeMin = EndTimeMin
			newResource.endTimeFormat = EndTimeFormat
			newResource.endTime = ResourceEndTime
			newResource.endTimeDisp = datetime.strftime(newResource.endTime, "%I:%M %p")

			newResource.tags = ResourceTags.split()
			newResource.put()
			self.redirect('/resources/' + newResource.name)

class Resources(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		
		if user:
			words = (self.request.url).split("/")
			guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)

			thisResource = Resource.query(Resource.name == words[4], ancestor=guestbook_key(guestbook_name)).get()
			tagString = ''
			for tag in thisResource.tags:
				tagString += tag + ' '
			tagString.strip()
			logging.debug(tagString)

			allReservations = Reservation.query(Reservation.name == words[4], ancestor=guestbook_key(guestbook_name))
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
				Reservation.date > datetime.today(),
				ndb.AND(Reservation.date == datetime.today(), 
				Reservation.endTime > datetime.now()),
				))
			logging.debug(words)
			logging.debug(allReservations.count())
			logging.debug(activeReservations.count())
			createReservationURL = '/reservations/' + words[4]

			if thisResource.owner == user.email() :
				owner = 1
			else:
				owner = 0

			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			template_values = {
				'owner': owner,
				'user': user,
				'thisResource': thisResource,
				'tagString': tagString,
				'activeReservations': activeReservations,
				'createReservationURL' : createReservationURL,
				'url': url,
				'url_linktext': url_linktext,
			}
			template = JINJA_ENVIRONMENT.get_template('resources.html')
			self.response.write(template.render(template_values))

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

    def post(self):
		# While adding a new resource, name must be entered
		# Resource end time cannot be smaller than start time
		# Resource name should be unique
		guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
		ResourceName = self.request.get('name').strip()
		StartTimeHour = self.request.get('StartTimeHour')
		StartTimeMin = self.request.get('StartTimeMin')
		StartTimeFormat = self.request.get('StartTimeFormat')
		StartTime = StartTimeHour + ':' + StartTimeMin + ':' + StartTimeFormat
		ResourceStartTime = datetime.strptime(StartTime, "%I:%M:%p")

		EndTimeHour = self.request.get('EndTimeHour')
		EndTimeMin = self.request.get('EndTimeMin')
		EndTimeFormat = self.request.get('EndTimeFormat')
		EndTime = EndTimeHour + ':' + EndTimeMin + ':' + EndTimeFormat
		ResourceEndTime = datetime.strptime(EndTime, "%I:%M:%p")

		ResourceTags = self.request.get('tags').strip()

		checkIfResourceAlreadyExists = Resource.query(Resource.name == ResourceName, ancestor=guestbook_key(guestbook_name))
		
		logging.debug(ResourceName)
		logging.debug(StartTimeHour)
		logging.debug(StartTimeMin)
		logging.debug(StartTimeFormat)
		logging.debug(EndTimeHour)
		logging.debug(EndTimeMin)
		logging.debug(EndTimeFormat)
		logging.debug(ResourceTags)

		errorNo = 0
		if ResourceName == "":
			logging.debug("No name specified")
			errorNo = 1
		elif ResourceEndTime <= ResourceStartTime:
			logging.debug(ResourceEndTime)
			logging.debug(ResourceStartTime)
			errorNo = 2
		elif checkIfResourceAlreadyExists.count() > 0:
			errorNo = 3
		
		if errorNo > 0:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			logging.debug("Yes, there is an error")
			template_values = {
				'errorNo': errorNo,
				'url': url,
				'url_linktext': url_linktext,
				'ResourceName': ResourceName,
				'StartTimeHour': StartTimeHour,
				'StartTimeMin': StartTimeMin,
				'StartTimeFormat': StartTimeFormat,
				'EndTimeHour': EndTimeHour,
				'EndTimeMin': EndTimeMin,
				'EndTimeFormat': EndTimeFormat,
				'ResourceTags': ResourceTags,
			}
			template = JINJA_ENVIRONMENT.get_template('newresources.html')
			self.response.write(template.render(template_values))
		else:
			guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
			newResource = Resource(parent=guestbook_key(guestbook_name))
			newResource.owner = users.get_current_user().email()
			newResource.name = ResourceName

			newResource.startTimeHour = StartTimeHour
			newResource.startTimeMin = StartTimeMin
			newResource.startTimeFormat = StartTimeFormat
			newResource.startTime = ResourceStartTime
			newResource.startTimeDisp = datetime.strftime(newResource.startTime, "%I:%M %p")
			
			newResource.endTimeHour = EndTimeHour
			newResource.endTimeMin = EndTimeMin
			newResource.endTimeFormat = EndTimeFormat
			newResource.endTime = ResourceEndTime
			newResource.endTimeDisp = datetime.strftime(newResource.endTime, "%I:%M %p")

			newResource.tags = ResourceTags.split()
			newResource.put()
			self.redirect('/resources/' + newResource.name)

class NewReservations(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			errorNo = 0
			template_values = {
				'resourceName': self.request.url,
				'errorNo': errorNo,
				'url': url,
				'url_linktext': url_linktext,
			}
			template = JINJA_ENVIRONMENT.get_template('newReservations.html')
			self.response.write(template.render(template_values))
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

    def post(self):
		words = (self.request.url).split("/")

		StartTimeHour = self.request.get('StartTimeHour')
		StartTimeMin = self.request.get('StartTimeMin')
		StartTimeFormat = self.request.get('StartTimeFormat')
		StartTime = StartTimeHour + ':' + StartTimeMin + ':' + StartTimeFormat
		ReservationStartTime = datetime.strptime(StartTime, "%I:%M:%p")

		DurationHour = self.request.get('DurationHour')
		DurationMin = self.request.get('DurationMin')
		DurationTime = DurationHour + ':' + DurationMin
		ReservationDuration = datetime.strptime(DurationTime, "%H:%M")

		ReservationEndTime = ReservationStartTime + timedelta(hours=int(DurationHour), minutes=int(DurationMin))

		DateDay = self.request.get('DateDay')
		DateMonth = self.request.get('DateMonth')
		DateYear = self.request.get('DateYear')
		Date = DateDay + ':' + DateMonth + ':' + DateYear
		errorNo = 0
		try:
			ReservationDate = datetime.strptime(Date, "%d:%m:%Y")
		except ValueError:
			errorNo = 7
		# While adding a new reservation, all values  must be selected
		# Only allow future reservations
		# Start time + duration cannot exceed 12 am
		# Cannot overlap with an existing reservation
		# Should fall in resource availability times
		# Date Validation
		guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)

		thisResource = Resource.query(Resource.name == words[4], ancestor=guestbook_key(guestbook_name)).get()

		if errorNo == 7:
			logging.debug("")
		elif DurationHour == "0" and DurationMin == "00":
			errorNo = 1
		elif (ReservationDate.date() < datetime.today().date()) or (ReservationDate.date() == datetime.today().date() and ReservationStartTime.time() < datetime.now().time()):
			errorNo = 2
		elif ReservationEndTime.date() > ReservationStartTime.date():
			errorNo = 3
		elif ReservationEndTime <= ReservationStartTime:
			errorNo = 6
		elif (ReservationStartTime < thisResource.startTime or ReservationEndTime > thisResource.endTime):
			errorNo = 5
		else:
			myReservations = Reservation.query(Reservation.name == words[4], Reservation.date == ReservationDate, Reservation.startTime <= ReservationEndTime, ancestor=guestbook_key(guestbook_name))

			for myReservation in myReservations:
				if(myReservation.endTime >= ReservationStartTime):
					errorNo = 4
					break

		if errorNo > 0:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			logging.debug("Yes, there is an error")
			template_values = {
				'errorNo': errorNo,
				'url': url,
				'url_linktext': url_linktext,
				'StartTimeHour': StartTimeHour,
				'StartTimeMin': StartTimeMin,
				'StartTimeFormat': StartTimeFormat,
				'DurationHour': DurationHour,
				'DurationMin': DurationMin,
				'DateDay': DateDay,
				'DateMonth': DateMonth,
				'DateYear': DateYear,
			}
			template = JINJA_ENVIRONMENT.get_template('newReservations.html')
			self.response.write(template.render(template_values))
		else:
			guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)

			newReservation = Reservation(parent=guestbook_key(guestbook_name))
			newReservation.owner = users.get_current_user().email()
			newReservation.name = words[4]

			newReservation.startTime = ReservationStartTime
			newReservation.startTimeDisp = datetime.strftime(newReservation.startTime, "%I:%M %p")

			newReservation.durationTime = ReservationDuration
			newReservation.durationDisp = datetime.strftime(newReservation.durationTime, "%H hrs %M mins")

			newReservation.endTime = ReservationEndTime

			newReservation.date = ReservationDate
			newReservation.dateDisp = datetime.strftime(newReservation.date, "%a, %d %b, %Y")

			newReservation.put()
			self.redirect('/resources/' + words[4])

class Tags(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		if user:
			words = (self.request.url).split("/")
			tag = words[4]
			guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
			taggedResources = Resource.query(Resource.tags == words[4], ancestor=guestbook_key(guestbook_name))
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			template_values = {
				'tag': tag,
				'taggedResources': taggedResources,
				'url': url,
				'url_linktext': url_linktext,
			}
			
			template = JINJA_ENVIRONMENT.get_template('tags.html')
			self.response.write(template.render(template_values))
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

class DelReservations(webapp2.RequestHandler):
	def post(self):
		reservationKey = ndb.Key(urlsafe=self.request.get('reservationKey'))
		logging.debug(reservationKey)
		reservationKey.delete()
		self.redirect('/')
		
class RSS(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()		
		if user:
			words = (self.request.url).split("/")
			tag = words[4]

			guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)

			allReservations = Reservation.query(Reservation.name == words[4], ancestor=guestbook_key(guestbook_name))
			user = users.get_current_user()
			logging.debug(allReservations.count())

			top = Element('channel')
			title = SubElement(top, 'title')
			title.text = 'Reservations for ' + words[4]
			for reservation in allReservations:
				item = SubElement(top, 'item')
				ReservedBy = SubElement(item, 'ReservedBy')
				ReservedBy.text = user.email()
				ResourceName = SubElement(item, 'ResourceName')
				ResourceName.text = reservation.name
				StartTime = SubElement(item, 'StartTime')
				StartTime.text = reservation.startTimeDisp + ' on ' + reservation.dateDisp
				Duration = SubElement(item, 'Duration')
				Duration.text = reservation.durationDisp
			self.response.headers['Content-Type'] = 'text/xml'
			self.response.headers['Content-Disposition'] = 'attachment; filename=myfile.xml'
			self.response.write(prettify(top))
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

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/user', User),
    ('/resources', NewResources),
    ('/resources/.+', Resources),
    ('/reservations', DelReservations),
    ('/reservations/.+', NewReservations),
    ('/tags/.+', Tags),
    ('/rss/.+', RSS),
], debug=True)