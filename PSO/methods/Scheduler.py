import zope.interface
from ..setting.Solution import Solution

class Scheduler(zope.interface.Interface):

    def schedule(self, wf) -> Solution:
        pass