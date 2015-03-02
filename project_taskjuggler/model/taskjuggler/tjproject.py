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
from tjinterval2 import TjInterval2
from datetime import date


class TjProject(object):
    # The project property is mandatory and should be the first property in a
    # project file.
    # It is used to capture basic attributes such as the project id,
    # name and the expected time frame.
    # Be aware that the dates for the project period default to UTC times.
    # See interval2 for details.

    def __init__(self, id, name, version):
        self.id = 'Project_%s' % (id,)
        self.internal_id = id
        self.name = name
        self.version = version
        self.interval2 = TjInterval2(date.today(), date.today())

    def __str__(self):
        """converts to a tjp representation
        """
        from jinja2 import Template
        template = tjptemplates.tjp_tjproject_template
        jtemplate = Template(template)
        content = jtemplate.render({
            'project': self,
        })
        return content
