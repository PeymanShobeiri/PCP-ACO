import sys
import traceback
from Constants import Constants
from ACO.CloudAcoEnvironment import CloudAcoEnvironment
from ACO.CloudAcoProblemRepresentation import CloudAcoProblemRepresentation
from WorkflowBroker import WorkflowBroker
from ScheduleType import ScheduleType
from CloudACO import CloudACO
from math import ceil
import time



class test:

    def computeFastest(self, WfFile, startTime, deadline):
        MH = 0
        try:
            wb = WorkflowBroker(WfFile, ScheduleType.Fastest)
            CH = wb.schedule(startTime, deadline)
            # wb.getPolicy().computeESTandEFT(startTime)
            # wb.getPolicy().computeLSTandLFT(deadline)
            MH = wb.graph.getNodes()[wb.graph.getEndId()].getAST()
            print("Fastest: cost= " + str(CH) + " time= " + str(MH))
        except Exception as e:
            print("Error in creating workflow broker!!!" + '  ' + str(e))

        return MH

    def computeCheapest(self, wfFile, startTime, deadline):
        MC = 0
        try:
            wb = WorkflowBroker(wfFile, ScheduleType.Cheapest)
            CC = wb.schedule(startTime, deadline)
            MC = wb.graph.getNodes()[wb.graph.getEndId()].getAST()
            # wb.getPolicy().computeESTandEFT(startTime)
            # wb.getPolicy().computeLSTandLFT(deadline)
            print("Cheapest: cost= " + str(CC) + " time= " + str(MC))
        except Exception as e:
            print("Error in creating workflow broker!!!!" + '  ' + str(e))

        return MC

    def scheduleWorkflow(self):
        workflowPath = "../Workflows/Montage_25.xml"

        startTime = 0
        deadline = 1000
        finishTime = None
        MH = 0
        MC = 0
        cost = 0.0
        CC = 0.0
        CH = 0.0
        wb = None
        out = None
        realStartTime = 0
        realFinishTime = 0

        MH = self.computeFastest(workflowPath, startTime, deadline)
        MC = self.computeCheapest(workflowPath, startTime, deadline)

        alpha = 3
        while alpha <= 5:
            deadline = ceil(alpha * MH)

            try:
                wb = WorkflowBroker(workflowPath, ScheduleType.IC_PCP2)
            except Exception as e:
                print("Error ?!!" + '  ' + str(e))
                traceback.print_exc()

            realStartTime = round(time.time() * 1000)
            cost = wb.schedule(startTime, deadline)
            realFinishTime = round(time.time() * 1000)
            realFinishTime -= realStartTime
            finishTime = wb.graph.getNodes()[wb.graph.getEndId()].getEFT()
            message = "\n\nICPCP finishT < deadline: " + \
                      str((finishTime < deadline)) + " --> " + str(finishTime) + \
                      "\n" + "deadline : " + str(deadline) + \
                      "\t\tcost of icpc: " + str(cost) + "\n" + \
                      "solution: \n"


            # wb.getPolicy().solutionAsString()
            print(message)

            ######################## first one done starting the sceond one

            try:
                wb = WorkflowBroker(workflowPath, ScheduleType.IC_PCPD2)
            except Exception as e:
                print("Error ?!!" + '  ' + str(e))
                traceback.print_exc()

            realStartTime = round(time.time() * 1000)
            cost = wb.schedule(startTime, deadline)
            realFinishTime = round(time.time() * 1000)
            realFinishTime -= realStartTime
            finishTime = wb.graph.getNodes()[wb.graph.getEndId()].getEST()
            message = "\n\nICPCPD2 finishT < deadline: " + \
                      str((finishTime < deadline)) + " --> " + str(finishTime) +\
                      "\n" + "deadline : " + str(deadline) + \
                      "\t\tcost of icpc: " + str(cost) + "\n" + \
                      "solution: \n"

            # wb.getPolicy().solutionAsString()
            print(message)

            summ = 0
            for xxx in range(5):
                print("evaloation itr : " + str(xxx))
                try:
                    wb = WorkflowBroker(workflowPath, ScheduleType.IC_PCPD2_2)
                    wb.getPolicy().computeESTandEFT(startTime)
                    wb.getPolicy().computeLSTandLFT(deadline)

                    wb.getGraph().getNodes()[wb.getGraph().getStartId()].setDeadline(0)
                    wb.getGraph().getNodes()[wb.getGraph().getStartId()].setAFT(0)
                    wb.getGraph().getNodes()[wb.getGraph().getEndId()].setDeadline(deadline)
                    wb.getGraph().getNodes()[wb.getGraph().getStartId()].setScheduled()
                    wb.getGraph().getNodes()[wb.getGraph().getEndId()].setScheduled()

                    wb.getPolicy().distributeDeadline()
                    # wb.getPolicy().setEndNodeEST()

                    print("=================================MY_ACO")
                    MAX_Parallel = wb.getPolicy().FindMaxParallel()
                    wb.getGraph().setMaxParallel(MAX_Parallel)
                    problemRepresentation = CloudAcoProblemRepresentation(wb.graph, wb.resources, Constants.BANDWIDTH, deadline, MAX_Parallel)
                    environment = CloudAcoEnvironment(problemGraph=problemRepresentation)
                    cloudACO = CloudACO(environment.getProblemGraph().getGraphSize())
                    OptimalCost = cloudACO.schedule(environment, deadline)
                    summ += OptimalCost
                    # x.append(alpha)
                    # y.append(OptimalCost)
                    print("==================================MY_ACO")
                except Exception as e:
                    print("EEEEEException" + str(e))
                    traceback.print_exc()
                    print(e)

            print("average : " + str(summ / 5))
            return
            alpha += 1.0
        # plt.plot(x, y)
        # plt.plot(x, y2)
        # plt.xlabel('Deadline Factor')
        # plt.ylabel('Normalized Cost')
        # plt.title('My ACO')
        # plt.show()

    def printWorkflow(self, g):
        pass

    def main(self):
        self.scheduleWorkflow()
        # CloudAcoWorkflow.printSolution()


if __name__ == '__main__':
    x = test()
    x.main()
