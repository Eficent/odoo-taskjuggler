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
from tjresource import *
from tjallocate import *
from tjdepends import *


class TjTask(object):

    def __init__(self, id, name, type):
        self.id = 'Task_%s' % (id,)
        self.internal_id = id
        self.type = type
        self.absolute_id = self.id
        self.name = name
        self.effort = False
        self.__childs = []
        self.__allocations = False
        self.__depends = False

    @property
    def allocations(self):
        return self.__allocations

    @allocations.setter
    def allocations(self, values):
        for value in values:
            if type(value) is not TjResource:
                raise ValueError("This is not a resource")
        self.__allocations = TjAllocate(values)

    @property
    def depends(self):
        return self.__depends

    @depends.setter
    def depends(self, value):
        if value and type(value) is not TjDepends:
            raise ValueError("This is not a list of dependencies")
        self.__depends = value

    @property
    def childs(self):
        return self.__childs

    @childs.setter
    def childs(self, tasks):
        for task in tasks:
            if not isinstance(task, TjTask):
                raise ValueError("This is not a list of tasks")
            task.absolute_id = '%s.%s' % (self.absolute_id, task.id)
            self.__childs.append(task)

    def __str__(self):
        """converts the interval2 to a tjp representation
        """
        from jinja2 import Template
        template = tjptemplates.tjp_tjtask_template
        jtemplate = Template(template)
        content = jtemplate.render({
            'task': self,
        })
        return content


class TjWBSElement(TjTask):

    def __init__(self, id, name, type):
        super(TjWBSElement, self).__init__(id, name, type)
        self.id = 'WBSElement_%s' % (id,)
        self.absolute_id = self.id
