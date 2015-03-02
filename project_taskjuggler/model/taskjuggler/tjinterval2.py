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
from datetime import date


class TjInterval2(object):
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

    def __init__(self, date_start, date_end):
        if type(date_start) is not date:
            raise ValueError("Invalid start date")
        if type(date_end) is not date:
            raise ValueError("Invalid end date")
        if date_end < date_end:
            raise ValueError("Invalid interval %s - %s"
                             % (date_start, date_end))

        self.date_start = date_start.isoformat()
        self.date_end = date_end.isoformat()
        # The end must not be before the start.

    def __str__(self):
        """converts the interval2 to a tjp representation
        """
        from jinja2 import Template
        template = tjptemplates.tjp_tjinterval2_template
        jtemplate = Template(template)
        content = jtemplate.render({
            'interval': self,
        })
        return content