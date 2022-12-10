import zope.interface
from Solution import Solution

class Scheduler(zope.interface.Interface):

    def schedule(self, wf) -> Solution:
        pass