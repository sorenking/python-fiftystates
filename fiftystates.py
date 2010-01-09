"""Python library for interacting with the Fifty State Project API.

The Fifty State Project provides data on state legislative activities,
including bill summaries, votes, sponsorships and state legislator
information.
"""

__author__ = "Michael Stephens <mstephens@sunlightfoundation.com>"
__copyright__ = "Copyright (c) 2009 Sunlight Labs"
__license__ = "BSD"
__version__ = "0.1"

from remoteobjects import RemoteObject, fields, ListObject
import urllib

FIFTYSTATES_URL = "http://fiftystates-dev.sunlightlabs.com/api/"

class FiftystatesDatetime(fields.Datetime):
    dateformat = '%Y-%m-%d %H:%M:%S'

class FiftystatesObject(RemoteObject):
    @classmethod
    def get(cls, func, params={}):
        params['format'] = 'json'
        url = "%s%s/?%s" % (FIFTYSTATES_URL, func,
                            urllib.urlencode(params))
        return super(FiftystatesObject, cls).get(url)
    
class Session(FiftystatesObject):
    start_year = fields.Field()
    end_year = fields.Field()
    name = fields.Field()

    def __str__(self):
        return self.name

class State(FiftystatesObject):
    name = fields.Field()
    abbreviation = fields.Field()
    legislature_name = fields.Field()
    upper_chamber_name = fields.Field()
    lower_chamber_name = fields.Field()
    upper_chamber_term = fields.Field()
    lower_chamber_term = fields.Field()
    upper_chamber_title = fields.Field()
    lower_chamber_title = fields.Field()
    sessions = fields.List(fields.Object(Session))

    @classmethod
    def get(cls, abbrev):
        return super(State, cls).get(abbrev)

    def __str__(self):
        return self.name

class Action(FiftystatesObject):
    date = FiftystatesDatetime()
    actor = fields.Field()
    action = fields.Field()

    def __str__(self):
        return '%s: %s' % (self.actor, self.action)

class Sponsor(FiftystatesObject):
    leg_id = fields.Field()
    full_name = fields.Field()
    type = fields.Field()

    def __str__(self):
        return self.full_name

class Vote(FiftystatesObject):
    vote_id = fields.Field()
    date = FiftystatesDatetime()
    chamber = fields.Field()
    motion = fields.Field()
    yes_count = fields.Field()
    no_count = fields.Field()
    other_count = fields.Field()
    passed = fields.Field()

    @classmethod
    def get(cls, id):
        func = 'vote/%d' % id
        return super(Vote, cls).get(func)

    def __str__(self):
        return "Vote on '%s'" % self.motion

class Version(FiftystatesObject):
    url = fields.Field()
    name = fields.Field()

def ListOf(cls):
    class List(ListObject, FiftystatesObject):
        entries = fields.List(fields.Object(cls))
    return List
    
class Bill(FiftystatesObject):
    title = fields.Field()
    state = fields.Field()
    session = fields.Field()
    chamber = fields.Field()
    bill_id = fields.Field()
    actions = fields.List(fields.Object(Action))
    sponsors = fields.List(fields.Object(Sponsor))
    votes = fields.List(fields.Object(Vote))
    versions = fields.List(fields.Object(Version))

    @classmethod
    def get(cls, state, session, chamber, bill_id):
        func = "%s/%s/%s/bills/%s" % (state, session, chamber, bill_id)
        return super(Bill, cls).get(func)

    @classmethod
    def search(cls, query, **kwargs):
        kwargs['q'] = query
        func = 'bills/search'
        return ListOf(cls).get(func, kwargs).entries

    def __str__(self):
        return '%s: %s' % (self.bill_id, self.title)

class Role(FiftystatesObject):
    state = fields.Field()
    session = fields.Field()
    chamber = fields.Field()
    district = fields.Field()
    contact_info = fields.List(fields.Dict(fields.Field()))

    def __str__(self):
        return '%s %s %s district %s' % (self.state, self.chamber,
                                         self.session, self.district)
    
class Legislator(FiftystatesObject):
    leg_id = fields.Field()
    full_name = fields.Field()
    first_name = fields.Field()
    last_name = fields.Field()
    middle_name = fields.Field()
    suffix = fields.Field()
    party = fields.Field()
    roles = fields.List(fields.Object(Role))

    @classmethod
    def get(cls, id):
        func = 'legislator/%d' % id
        return super(Legislator, cls).get(func)

    @classmethod
    def search(cls, **kwargs):
        return ListOf(cls).get('legislators/search', kwargs).entries

    def __str__(self):
        return self.full_name
    
class District(FiftystatesObject):
    state = fields.Field()
    session = fields.Field()
    chamber = fields.Field()
    name = fields.Field()
    legislators = fields.List(fields.Object(Legislator))

    @classmethod
    def get(cls, state, session, chamber, district):
        func = '%s/%s/%s/districts/%s' % (state, session, chamber, district)
        return super(District, cls).get(func)

    @classmethod
    def geo(cls, state, session, chamber, lat, long):
        func = '%s/%s/%s/districts/geo' % (state, session, chamber)
        params = {'lat': lat, 'long': long}
        return super(District, cls).get(func, params)
