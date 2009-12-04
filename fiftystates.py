"""Python library for interacting with the Fifty State Project API.

The Fifty State Project provides data on state legislative activities,
including bill summaries, votes, sponsorships and state legislator
information.
"""

__author__ = "Michael Stephens <mstephens@sunlightfoundation.com>"
__copyright__ = "Copyright (c) 2009 Sunlight Labs"
__license__ = "BSD"
__version__ = "0.1"

import urllib, urllib2
import datetime
try:
    import json
except ImportError:
    import simplejson as json

class FiftyStatesApiError(Exception):
    pass
    
def apicall(func, params={}):
    params['format'] = 'json'
    url = 'http://fiftystates-dev.sunlightlabs.com/api/%s/?%s' % (func,
                                              urllib.urlencode(params))
    try:
        response = urllib2.urlopen(url).read()
        obj = json.loads(response)
        return obj
    except urllib2.HTTPError, e:
        raise FiftyStatesApiError(e.read())
    except ValueError, e:
        raise FiftyStatesApiError('Invalid Response')

def parse_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

class FiftyStatesApiObject(object):
    
    def __init__(self, obj):
        self.__dict__.update(obj)
    
class Role(FiftyStatesApiObject):

    class ContactInfo(FiftyStatesApiObject):
        pass

    def __init__(self, obj):
        super(Role, self).__init__(obj)
        self.contact_info = map(self.ContactInfo, self.contact_info)

    def __str__(self):
        return '%s %s %s district %s' % (self.state, self.chamber,
                                         self.session, self.district)
    
class Legislator(FiftyStatesApiObject):

    @staticmethod
    def get(id):
        func = 'legislators/%d' % id
        obj = apicall(func)
        return Legislator(obj)

    @staticmethod
    def search(**kwargs):
        func = 'legislators/search'
        obj = apicall(func, kwargs)
        return map(Legislator, obj)

    def __init__(self, obj):
        super(Legislator, self).__init__(obj)
        self.roles = map(Role, self.roles)

    def __str__(self):
        return self.full_name

class District(FiftyStatesApiObject):

    @staticmethod
    def get(state, session, chamber, district):
        func = '%s/%s/%s/districts/%s' % (state, session, chamber, district)
        obj = apicall(func)
        return District(obj)

    @staticmethod
    def geo(state, session, chamber, lat, long):
        func = '%s/%s/%s/districts/geo' % (state, session, chamber)
        params = {'lat': lat, 'long': long}
        obj = apicall(func, params)
        return District(obj)

    def __init__(self, obj):
        super(District, self).__init__(obj)
        self.legislators = map(Legislator, self.legislators)

class Vote(FiftyStatesApiObject):

    class SpecificVote(FiftyStatesApiObject):

        def __str__(self):
            return "%s voted %s" % (self.full_name, self.type)
    
    def __init__(self, obj):
        super(Vote, self).__init__(obj)
        self.date = parse_date(self.date)

        if 'roll' in obj:
            self.roll = map(self.SpecificVote, self.roll)

    @staticmethod
    def get(id):
        func = 'votes/%d' % id
        obj = apicall(func)
        return Vote(obj)

    def __str__(self):
        return "Vote on '%s'" % self.motion

class Sponsor(FiftyStatesApiObject):
    
    def get_legislator(self):
        return Legislator.get(self.leg_id)

    def __str__(self):
        return self.full_name

class Action(FiftyStatesApiObject):
    
    def __init__(self, obj):
        super(Action, self).__init__(obj)
        self.date = parse_date(self.date)

    def __str__(self):
        return '%s: %s' % (self.actor, self.action)

class Session(FiftyStatesApiObject):

    def __str__(self):
        return self.name
    
class State(FiftyStatesApiObject):

    @staticmethod
    def get(abbrev):
        obj = apicall(abbrev)
        return State(obj)

    def __init__(self, obj):
        super(State, self).__init__(obj)
        self.sessions = map(Session, self.sessions)

    def __str__(self):
        return self.name

class Bill(FiftyStatesApiObject):

    @staticmethod
    def get(state, session, chamber, bill_id):
        func = '%s/%s/%s/bills/%s' % (state, session, chamber, bill_id)
        obj = apicall(func)
        return Bill(obj)

    @staticmethod
    def search(query, **kwargs):
        kwargs['q'] = query
        func = 'bills/search'
        obj = apicall(func, kwargs)
        return map(Bill, obj)

    def __init__(self, obj):
        super(Bill, self).__init__(obj)
        self.last_action = parse_date(self.last_action)
        self.first_action = parse_date(self.first_action)
        self.actions = map(Action, self.actions)
        self.sponsors = map(Sponsor, self.sponsors)
        self.votes = map(Vote, self.votes)

    def __str__(self):
        return '%s: %s' % (self.bill_id, self.title)
