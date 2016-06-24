"""models.py - This file contains the class definitions for the Datastore
entities used by the Trap. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_trap')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name  = ndb.StringProperty()
    email = ndb.StringProperty(required=True)


class Trap(ndb.Model):
    """Trap object"""
    target             = ndb.IntegerProperty(required=True) # email address
    ## is this a thing I can possibly do? v
    #  target             = ndb.IntegerProperty(required=True, kind='User')
    attempts_allowed   = ndb.IntegerProperty(required=True, default=9)
    attempts_remaining = ndb.IntegerProperty(required=True, default=9)
    closed            = ndb.BooleanProperty(required=True, default=False)
    setter             = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_trap(target, setter):
        """Creates and returns a new trap"""
        # if max < min:
        #     raise ValueError('Maximum must be greater than minimum')
        trap = Trap( target  = target,
                     setter  = setter,
                     closed = False )
        trap.put()
        return trap

    def to_form(self, message):
        """Returns a TrapForm representation of the Trap"""
        form                    = TrapForm()
        form.urlsafe_key        = self.key.urlsafe()
        form.attempts_remaining = self.attempts_remaining
        form.closed             = self.closed
        form.message            = message
        return form

    def close_trap(self, trapped=False):
        """Closes the trap - if trapped is True, the crush has found their trap setter.
         - if trapped is False, the crush could not meet their setter."""
        self.closed = True
        self.put()
        # Add the trap to the score 'board'
        score = Score(user=self.setter, date=date.today(), trapped=trapped,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    trapped = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, trapped=self.trapped,
                         date=str(self.date), guesses=self.guesses)


class TrapForm(messages.Message):
    """TrapForm for outbound trap state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    closed = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)


class NewTrapForm(messages.Message):
    """Used to create a new trap"""
    user_name = messages.StringField(1, required=True)
    min = messages.IntegerField(2, default=1)
    max = messages.IntegerField(3, default=10)
    attempts = messages.IntegerField(4, default=5)


class MakeGuessForm(messages.Message):
    """Used to make a guess in an existing trap"""
    guess = messages.IntegerField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    trapped = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
