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
from tjworkinghours import *


class TjResource(object):
    # Tasks that have an effort specification need to have at least one
    # resource assigned to do the work.
    # Use this property to define resources or groups of resources.

    def __init__(self, id, name):
        self.id = 'Resource_%s' % (id,)
        self.internal_id = id
        self.name = name
        self.efficiency = 1.0
        self.email = ''
        self.__workinghours = []

    @property
    def workinghours(self):
        return self.__workinghours

    @workinghours.setter
    def workinghours(self, workinghours):
        for workinghour in workinghours:
            if not isinstance(workinghour, TjWorkingHours):
                raise ValueError("This is not a valid working hour")
        self.__workinghours = workinghours

    def __str__(self):
        """converts to a tjp representation
        """
        from jinja2 import Template
        template = tjptemplates.tjp_tjresource_template
        jtemplate = Template(template)
        content = jtemplate.render({
            'resource': self,
        })
        return content