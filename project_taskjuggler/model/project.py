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

from openerp.tools.translate import _
from openerp.osv import fields, orm
import os
import subprocess
import tempfile
import time
import csv
import logging
import datetime
_logger = logging.getLogger(__name__)
from taskjuggler import TjProject, TjInterval2, TjWeekDayInterval, \
    TjTimeInterval, TjWeekDayIntervals, TjTimeIntervals, TjResource, \
    TjWorkingHours, TjWBSElement, TjTask, TjEffort, tjptemplates, TjDepend, \
    TjDepends

_WEEKDAYS = {
    '0': 'mon',
    '1': 'tue',
    '2': 'wed',
    '3': 'thu',
    '4': 'fri',
    '5': 'sat',
    '6': 'sun'
}


class project(orm.Model):
    _inherit = "project.project"

    _columns = {
        'date_start_plan': fields.datetime('Scheduled Starting Date',
                                           select=True),
        'date_end_plan': fields.datetime('Scheduled Ending Date', select=True),
        'importance': fields.integer(
            'Importance', help="Specifies the priority of the task. "
                               "A task with higher priority is more "
                               "likely to get the requested resources."
                               "The default priority value of all tasks "
                               "is 500.")
    }

    def _create_tjp_file(self):
        res = dict()
        res['temp_file_full_path'] = tempfile.mktemp(prefix='project_')
        res['temp_file_name'] = os.path.basename(res['temp_file_full_path'])
        res['tjp_file_full_path'] = res['temp_file_full_path'] + ".tjp"
        res['csv_file_full_path'] = res['temp_file_full_path'] + ".csv"
        return res

    def _get_wbs(self, cr, uid, ids, context=None):
        result = {}
        for project in self.pool.get('project.project').browse(
                cr, uid, ids, context=context):
            result[project.id] = True
            child_ids = self.search(
                cr, uid, [('parent_id', '=', project.analytic_account_id.id)],
                context=context)
            for child_id in child_ids:
                lchild_id = list()
                lchild_id.append(child_id)
                result.update(self._get_wbs(cr, uid, lchild_id, context))
        return result

    def tjp_project(self, cr, uid, proj_id, context=None):
        # Read the project data
        project = self.pool.get('project.project').browse(cr, uid, proj_id,
                                                          context=context)
        date_start = datetime.datetime.strptime(
            project.date_start, "%Y-%m-%d").date()
        date_end = datetime.datetime.strptime(
            project.date, "%Y-%m-%d").date()
        tjproject = TjProject(project.id, project.complete_name, '')
        tjproject.interval2 = TjInterval2(date_start, date_end)
        return tjproject

    def tjp_resources(self, cr, uid, wbs_ids, context=None):
        # Read all the members of the projects in the WBS and
        # obtain the related employee.
        def hours_time_string(hours):
            """ convert a number of hours (float) into a string
            with format '%H:%M' """
            minutes = int(round(hours * 60))
            return "%02d:%02d" % divmod(minutes, 60)

        members = {}
        for project in self.browse(cr, uid, wbs_ids, context=context):
            for user in project.members:
                for employee in user.employee_ids:
                    members[employee.id] = user.id
                    continue
        resources = []
        for employee in self.pool.get('hr.employee').browse(
                cr, uid, members.keys(), context=context):
            rid = members[employee.id]
            rname = employee.resource_id.name
            calendar = employee.resource_id.calendar_id
            workinghours_list = []
            for attendance in calendar.attendance_ids:
                weekday = _WEEKDAYS[attendance.dayofweek]
                weekdayinterval = TjWeekDayInterval(weekday, '')
                timeinterval = TjTimeInterval(
                    hours_time_string(attendance.hour_from),
                    hours_time_string(attendance.hour_to))
                weekdayintervals = TjWeekDayIntervals([weekdayinterval])
                timeintervals = TjTimeIntervals([timeinterval])
                workinghours_list.append(TjWorkingHours(weekdayintervals,
                                                        timeintervals))
            resource = TjResource(rid, rname)
            resource.workinghours = workinghours_list
            resources.append(resource)
        return resources

    def tjp_tasks(self, cr, uid, ids, tjresources, tjwbselements,
                  context=None):
        hierarchy = {}
        tasks = {}
        for project in self.pool.get('project.project').browse(
                cr, uid, ids, context=context):
            tjwbselement = next((tjwbselement for tjwbselement
                                 in tjwbselements if
                                 tjwbselement.internal_id == project.id and
                                 tjwbselement.type == 'project.project'), None)
            if not tjwbselement:
                tjwbselement = TjWBSElement(project.id, project.name,
                                            'project.project')
            hierarchy[tjwbselement] = True
            tasks[tjwbselement] = True
            tjtasks = []
            for task in project.tasks:
                tjtask = TjTask(task.id, task.name, 'project.task')
                tjtask.effort = TjEffort(task.planned_hours, 'h')
                for tjresource in tjresources:
                    if tjresource.internal_id == task.user_id.id:
                        tjtask.allocations = [tjresource]
                tjtasks.append(tjtask)
                tasks[tjtask] = True
            tjwbselement.childs.extend(tjtasks)
            child_ids = self.search(
                cr, uid, [('parent_id', '=', project.analytic_account_id.id)],
                context=context)
            for child in self.pool.get('project.project').browse(
                    cr, uid, child_ids, context=context):
                child_tjwbselement = TjWBSElement(child.id, child.name,
                                                  'project.project')
                tjwbselement.childs.extend([child_tjwbselement])
                lchild_id = list()
                lchild_id.append(child.id)
                child_hier, child_tasks = self.tjp_tasks(
                    cr, uid, lchild_id, tjresources, tjwbselements, context)
                hierarchy.update(child_hier)
                tasks.update(child_tasks)
        return hierarchy, tasks

    def tjp_tasks_depends(self, cr, uid, tjtasks, context=None):
        task_obj = self.pool.get('project.task')
        task_ids = []
        for tjtask in tjtasks:
            if tjtask.type == 'project.task':
                task_ids.append(tjtask.internal_id)

        for task in task_obj.browse(cr, uid, task_ids, context=context):
            tjtask = next((tjtask for tjtask in tjtasks if
                           tjtask.internal_id ==
                           task.id), None)
            tjdepends = []
            for predecessor in task.predecessor_ids:
                for dtjtask in tjtasks:
                    if dtjtask.internal_id == predecessor.id:
                        tjdepends.append(TjDepend(dtjtask))
                        continue
            if tjdepends:
                tjtask.depends = TjDepends(tjdepends)

    def _create_tjp_file_content(self, cr, uid, proj_id, files, context=None):
        """creates the tjp file content
        """
        from jinja2 import Template
        start = time.time()
        num_of_records = 0
        template = tjptemplates.tjp_main_template
        jtemplate = Template(template)

        tjproject = self.tjp_project(cr, uid, proj_id, context=context)
        wbs_ids = self._get_wbs(cr, uid, [proj_id], context=context).keys()
        tjresources = self.tjp_resources(cr, uid, wbs_ids, context=context)
        tjtaskhierd, tjtasksd = self.tjp_tasks(
            cr, uid, [proj_id], tjresources, [], context=context)
        self.tjp_tasks_depends(cr, uid, tjtasksd.keys(), context=context)
        tjtaskhier = tjtaskhierd.keys()
        tjp_content = jtemplate.render({
            'project': tjproject,
            'resources': tjresources,
            'tasks': tjtaskhier,
            'csv_file_full_path': files['temp_file_full_path']
        })

        _logger.debug(
            'total number of records: %s' % num_of_records
        )
        end = time.time()
        _logger.debug(
            'rendering the whole tjp file took : %s seconds' % (end - start)
        )
        return tjp_content

    def _fill_tjp_file(self, tjp_content, files):
        """fills the tjp file with content
        """
        with open(files['tjp_file_full_path'], 'w+') as tjp_file:
            tjp_file.write(tjp_content)

    def _parse_csv_file(self, cr, uid, proj_id, files, context=None):
        """parses back the csv file and fills the tasks with computes_start and
        computed end values
        """
        """parses back the csv file and fills the tasks with computes_start and
        computed end values
        """
        project_obj = self.pool.get('project.project')
        task_obj = self.pool.get('project.task')
        _logger.debug('csv_file_full_path : %s' % files['csv_file_full_path'])
        if not os.path.exists(files['csv_file_full_path']):
            _logger.debug('could not find CSV file, '
                          'returning without updating db!')
            return

        with open(files['csv_file_full_path'], 'r') as csv_file:
            csv_content = csv.reader(csv_file, delimiter=';')
            lines = [line for line in csv_content]
            lines.pop(0)

        for data in lines:
            id_line = data[0]
            entity_name = id_line.split('.')[-1].split('_')[0]
            entity_id = int(id_line.split('.')[-1].split('_')[-1])
            if entity_name == 'WBSElement' and entity_id:
                project_data = {
                    'date_start_plan': datetime.datetime.strptime(
                        data[1], "%Y-%m-%d-%H:%M"),
                    'date_end_plan': datetime.datetime.strptime(
                        data[2], "%Y-%m-%d-%H:%M"),
                    'date_start': datetime.datetime.strptime(
                        data[1], "%Y-%m-%d-%H:%M").date(),
                    'date': datetime.datetime.strptime(
                        data[2], "%Y-%m-%d-%H:%M").date(),

                }
                project_obj.write(cr, uid, [entity_id], project_data,
                                  context=context)
            elif entity_name == 'Task' and entity_id:
                task_data = {
                    'date_start': datetime.datetime.strptime(
                        data[1], "%Y-%m-%d-%H:%M"),
                    'date_end': datetime.datetime.strptime(
                        data[2], "%Y-%m-%d-%H:%M"),
                }
                task_obj.write(cr, uid, [entity_id], task_data,
                               context=context)

    def _delete_tjp_file(self, tjp_file_full_path):
        """deletes the temp tjp file
        """
        try:
            os.remove(tjp_file_full_path)
        except OSError:
            pass

    def _delete_csv_file(self, csv_file_full_path):
        """deletes the temp csv file
        """
        try:
            os.remove(csv_file_full_path)
        except OSError:
            pass

    def _clean_up(self, files):
        """removes the temp files
        """
        self._delete_tjp_file(files['tjp_file_full_path'])
        self._delete_csv_file(files['csv_file_full_path'])

    def action_schedule(self, cr, uid, ids, context=None):
        """Does the scheduling.
        """
        for project in self.browse(cr, uid, ids, context=context):
            # todo: Check that the project should be flagged as parent project

            # Create a tjp file
            files = self._create_tjp_file()

            # create tjp file content
            tjp_content = self._create_tjp_file_content(cr, uid, project.id,
                                                        files, context=context)

            # fill it with data
            self._fill_tjp_file(tjp_content, files)

            _logger.debug('tjp_file_full_path: %s' % files[
                'tjp_file_full_path'])

            # pass it to tj3
            process = subprocess.Popen(
                ['/usr/local/bin/tj3',
                 files['tjp_file_full_path']],
                stderr=subprocess.PIPE
            )
            # loop until process finishes and capture stderr output
            stderr_buffer = []
            while True:
                stderr = process.stderr.readline()

                if stderr == b'' and process.poll() is not None:
                    break

                if stderr != b'':
                    stderr = stderr.strip()
                    stderr_buffer.append(stderr)
                    _logger.debug(stderr.strip())

            # flatten the buffer
            stderr_buffer = '\n'.join(stderr_buffer)

            if process.returncode:
                # there is an error
                raise orm.except_orm(_('Errors'), stderr_buffer)
            # read back the csv file
            self._parse_csv_file(cr, uid, project.id, files, context=context)

            _logger.debug('tj3 return code: %s' % process.returncode)

            # remove the tjp file
            self._clean_up(files)

        return True