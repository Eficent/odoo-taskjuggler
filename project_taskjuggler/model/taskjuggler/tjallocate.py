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


class TjAllocate(object):
    # Specify which resources should be allocated to the task. The attributes
    # provide numerous ways to control which resource is used and when exactly
    # it will be assigned to the task. Shifts and limits can be used to
    # restrict the allocation to certain time intervals or to limit them
    # to a certain maximum per time period. The purge statement can be used
    # to remove inherited allocations or flags.

    def __init__(self, resource_list):
        self.resource_list = resource_list

    def __str__(self):
        """converts to a tjp representation
        """
        res = ''
        if self.resource_list:
            res = ', '.join([x.id for x in self.resource_list])
        return res