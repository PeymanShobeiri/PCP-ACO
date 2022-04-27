from math import floor
from unittest import removeResult
from numpy import outer
from ..setting.Solution import Solution
from ..setting.Task import Task
from ..setting.VM import VM
from . import Scheduler
from ..setting.Workflow import Workflow
import random
import zope

@zope.interface.implementer(Scheduler)
class PSO(object):

    def __init__(self, itr):
        self.__E = 0.0000001
        self.__POPSIZE = 200
        self.__NO_OF_ITE = itr
        self.__W = 0.5
        self.__C1 = 2.0
        self.__C2 = 2.0

        self.__wf = None
        self.__range = 0
        
        self.__dimension = 0
        self.__vmPool = []
    
    def createParticle(self ,vMax,xMin, xMax):
        return PSO.Particle(self,vMax,xMin, xMax)

    def schedule(self, wf):
        self.__wf = wf
        self.__dimension = len(wf.Array)
        self.__range = wf.getMaxParallel() * VM.TYPE_NO
        self.__vmPool = [None] * self.__range
        i = 0
        while i < len(self.__vmPool):
            self.__vmPool[i] = VM(i /wf.getMaxParallel())
            i += 1
        
        xMin = 0.0
        xMax = self.__range - 1
        vMax = xMax
        globalBestPos = [None] * self.__dimension
        globalBestSol = None
        particles = [None] * self.__POPSIZE
        for i in range(self.__POPSIZE):
            particles[i] = self.createParticle(vMax, xMin , xMax)
            particles[i].generateSolution()

            if globalBestSol == None or particles[i].sol.isBetterThan(globalBestSol , self.__wf.getDeadline()):
                for j in self.__dimension:
                    globalBestPos[j] = particles[i].position[j]
                globalBestSol = particles[i].sol
        
        print("the best initial solution:" + globalBestSol.calcCost() + ";\t" + globalBestSol.calcMakespan())

        iteIndex = 0
        while iteIndex < self.__NO_OF_ITE:
            for i in range(self.__POPSIZE):
                for j in range(self.__dimension):
                    particles[i].speed[j] = self.__W * particles[i].speed[j] + self.__C1 * random.random() * (particles[i].bestPos[j] - particles[i].position[j]) + self.__C2 * random.random() * (globalBestPos[j] - particles[i].position[j])
                    particles[i].speed[j] = min(particles[i].speed[j], vMax)

                    particles[i].position[j] = particles[i].position[j] + particles[i].speed[j]
                    particles[i].position[j] = max(particles[i].position[j], xMin)
                    particles[i].position[j] = min(particles[i].position[j], xMax)
                particles[i].generateSolution()
                if globalBestSol == None or particles[i].sol.isBetterThan(globalBestSol, wf.getDeadline()):
                    for j in range(self.__dimension):
                        globalBestPos[j] = particles[i].position[j]
                    globalBestSol = particles[i].sol
                    print("Iteration index:", iteIndex,globalBestSol.calcCost(), globalBestSol.calcMakespan())
            iteIndex += 1
        
        print("Globle best is :" + globalBestSol.calcCost() + ";\t" + globalBestSol.calcMakespan())
        return globalBestSol
            


            


    class Particle(object):

        def __init__(self, outer ,vMax , xMin, xMax):
            self.outer = outer
            self.position = [None] * outer.__dimension
            self.speed = [None] * outer.__dimension
            self.bestPos = [None] * outer.__dimension
            self.sol = None
            self.bestSol = None

            for i in range(outer.__dimension):
                self.position[i] = random.random() * (xMax - xMin) + xMin
                self.speed[i] = vMax * random.random() - vMax/2
                self.bestPos[i] = self.position[i]
            
        def generateSolution(self):
            self.sol = Solution()
            for i in range(len(self.position)):
                task = self.outer.Array[i]
                vmIndex = int(floor(self.position[i]))
                vm = self.outer.__vmPool[vmIndex]
                startTime = self.sol.calcEST(task, vm)
                self.sol.addTaskToVM(vm, task , startTime , True)
            
            if self.bestSol == None or self.sol.isBetterThan(self.bestSol , self.outer.__wf.getDeadline()):
                for j in range(self.outer.__dimension):
                    self.bestPos[j] = self.position[j]
                self.bestSol = self.sol
            
        def __str__(self):
            if self.sol != None:
                return "Particle [" + self.sol.calcCost() + ", " + self.sol.calcMakespan() + "]"
            return ""


