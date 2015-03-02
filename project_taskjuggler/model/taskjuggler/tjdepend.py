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


class TjDepend(object):
    # Specifies that the task cannot start before the specified tasks
    # have been finished.
    # By using the 'depends' attribute, the scheduling policy is automatically
    # set to asap. If both depends and precedes are used,
    # the last policy counts.

    def __init__(self, task):
        self.task = task
        self.gapduration = False
        self.gaplength = False
        self.onend = False
        self.onstart = False

    def __str__(self):
        """converts to a tjp representation
        """
        from jinja2 import Template
        template = tjptemplates.tjp_depend_template
        jtemplate = Template(template)
        content = jtemplate.render({
            'depend': self,
        })
        return content