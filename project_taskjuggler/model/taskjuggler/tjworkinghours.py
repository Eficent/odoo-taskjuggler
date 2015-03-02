# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#               Jordi Ballester Alomar <jordi.ballester@eficent.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from tjptemplates import tjptemplates
from datetime import datetime

_WEEKDAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


class TjWeekDayInterval(object):
    def __init__(self, start_weekday, end_weekday):
        if start_weekday not in _WEEKDAYS or \
                (end_weekday and end_weekday not in _WEEKDAYS):
            raise ValueError("Invalid weekday")
        self.start_weekday = start_weekday
        self.end_weekday = end_weekday

    def __str__(self):
        """converts to a tjp representation
        """
        if self.end_weekday:
            return '%s - %s' % (self.start_weekday, self.end_weekday)
        else:
            return self.start_weekday


class TjWeekDayIntervals(object):
    def __init__(self, list):
        self.__intervals = list

    @property
    def intervals(self):
        return self.__intervals

    @intervals.setter
    def intervals(self, intervals):
        for interval in intervals:
            if not isinstance(interval, TjWeekDayInterval):
                raise ValueError("This is not a valid weekday interval format")
        self.__intervals = intervals

    def __str__(self):
        """converts to a tjp representation
        """
        if self.intervals:
            return ', '.join(str(x) for x in self.intervals)
        else:
            return ''


class TjTimeInterval(object):

    @staticmethod
    def validate_time(date):
        try:
            datetime.strptime(date, '%H:%M')
            return True
        except ValueError:
            return False

    def __init__(self, start_time, end_time):
        if start_time and not self.validate_time(start_time):
            raise ValueError("Invalid start date format")
        if end_time and not self.validate_time(end_time):
            raise ValueError("Invalid end time format")
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        """converts to a tjp representation
        """
        if self.end_time:
            return '%s - %s' % (self.start_time, self.end_time)
        else:
            return self.start_time


class TjTimeIntervals(object):
    def __init__(self, intervals):
        self.__intervals = intervals

    @property
    def intervals(self):
        return self.__intervals

    @intervals.setter
    def intervals(self, intervals):
        for interval in intervals:
            if not isinstance(interval, TjTimeInterval):
                raise ValueError("This is not a valid time interval format")
        self.__intervals = intervals

    def __str__(self):
        """converts to a tjp representation
        """
        if self.intervals:
            return ', '.join(str(x) for x in self.intervals)
        else:
            return ''


class TjWorkingHours(object):
    # There are two ways to specify a date interval. The first is the most
    # obvious.
    # A date interval consists of a start and end DATE.
    # Watch out for end dates without a time specification!
    # Date specifications are 0 extended. An end date without a time is
    # expanded to midnight that day.
    # So the day of the end date is not included in the interval!
    # The start and end dates must be separated by a hyphen character.
    # In the second form specifies the start date and an interval duration.
    # The duration must be prefixed by a plus character.

    def __init__(self, weekdayintervals, timeintervals):
        self.__weekdayintervals = weekdayintervals
        self.__timeintervals = timeintervals
        self.off = False

    @property
    def weekdayintervals(self):
        return self.__weekdayintervals

    @weekdayintervals.setter
    def weekdayintervals(self, weekdayintervals):
        if not isinstance(weekdayintervals, TjWeekDayIntervals):
            raise ValueError("This is not a valid weekday intervals format")
        self.__weekdayintervals = weekdayintervals

    @property
    def timeintervals(self):
        return self.__timeintervals

    @timeintervals.setter
    def timeintervals(self, timeintervals):
        if not isinstance(timeintervals, TjTimeIntervals):
            raise ValueError("This is not a valid time intervals format")
        self.__timeintervals = timeintervals

    def __str__(self):
        """converts to a tjp representation
        """
        from jinja2 import Template
        template = tjptemplates.tjp_tjworkinghours_template
        jtemplate = Template(template)
        content = jtemplate.render({
            'weekdayintervals': self.weekdayintervals,
            'timeintervals': self.timeintervals,
            'off': self.off,
        })
        return content