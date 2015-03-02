__author__ = 'jordi'

from tjproject import *
from tjtask import *
from tjeffort import *
from tjdepends import *
from tjdepend import *
from tjresource import *
from datetime import date, datetime
from jinja2 import Template


project = TjProject('1', 'Project_1', 'v1')
resource_1 = TjResource('1', 'Resource_1')
weekdayinterval_1 = TjWeekDayInterval('mon', 'fri')
timeinterval_1 = TjTimeInterval('9:00', '13:00')
timeinterval_2 = TjTimeInterval('15:00', '19:00')
timeintervals = TjTimeIntervals([timeinterval_1, timeinterval_2])
weekdayintervals = TjWeekDayIntervals([weekdayinterval_1])
resource_1.workinghours = TjWorkingHours(weekdayintervals, timeintervals)
resource_2 = TjResource('2', 'Resource_2')
resource_2.workinghours = TjWorkingHours(weekdayintervals, timeintervals)
resources = [resource_1, resource_2]
wbselement_1 = TjWBSElement('1', 'WBSElement_1')
wbselement_2 = TjWBSElement('2', 'WBSElement_2')
task_1 = TjTask('1', 'Task_1')
task_2 = TjTask('2', 'Task_2')
wbselement_1.childs = [wbselement_2]
wbselement_2.childs = [task_1, task_2]
task_1.effort = TjEffort('1', 'w')
task_1.allocations = [resource_1, resource_2]
task_2.effort = TjEffort('1', 'w')
task_2.allocations = [resource_1, resource_2]
task_2.depends = TjDepends([TjDepend(task_1)])
tasks = [wbselement_1]


template = tjptemplates.tjp_main_template
jtemplate = Template(template)
date_start = date.today()
date_end = datetime.strptime('30-05-15', '%d-%m-%y').date()
project.interval2 = TjInterval2(date_start, date_end)

tjp_content = jtemplate.render({
    'project': project,
    'resources': resources,
    'tasks': tasks,
    'csv_file_full_path': 'temp_file_full_path'
})

print tjp_content