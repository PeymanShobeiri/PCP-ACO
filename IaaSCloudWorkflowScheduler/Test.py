import sys

sys.path.append('/Users/apple/Desktop/Create WS-ACO/MyCode')
from IaaSCloudWorkflowScheduler.Constants import Constants
from OtherCloudWorkflowScheduler.setting.Workflow import Workflow
from IaaSCloudWorkflowScheduler.ACO.CloudAcoEnvironment import CloudAcoEnvironment
from IaaSCloudWorkflowScheduler.ACO.CloudAcoProblemRepresentation import CloudAcoProblemRepresentation
from IaaSCloudWorkflowScheduler.WorkflowBroker import WorkflowBroker
from IaaSCloudWorkflowScheduler.ScheduleType import ScheduleType
from IaaSCloudWorkflowScheduler.ACO.CloudAcoAntForWorkflow import CloudAcoWorkflow
from IaaSCloudWorkflowScheduler.CloudACO import CloudACO
# from OtherCloudWorkflowScheduler.methods.PSO import PSO
from OtherCloudWorkflowScheduler.methods.Scheduler import Scheduler
import time


class test:

    def computeFastest(self, WfFile, startTime, deadline):
        MH = 0
        try:
            wb = WorkflowBroker(WfFile, ScheduleType.Fastest)
            CH = wb.schedule(startTime, deadline)
            wb.getPolicy().computeESTandEFT(startTime)
            wb.getPolicy().computeLSTandLFT(deadline)
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
            wb.getPolicy().computeESTandEFT(startTime)
            wb.getPolicy().computeLSTandLFT(deadline)
            print("Cheapest: cost= " + str(CC) + " time= " + str(MC))
        except Exception as e:
            print("Error in creating workflow broker!!!!" + '  ' + str(e))

        return MC

    def scheduleWorkflow(self):
        workflowPath = "/Users/apple/Desktop/cloud_aco-develop/src/main/resources/WfDescFiles/Montage_25.xml"
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

        alpha = 1.5
        while alpha <= 5:
            # deadline = round(alpha * MH)
            deadline = 71
            try:
                wb = WorkflowBroker(workflowPath, ScheduleType.IC_PCPD2)
            except Exception as e:
                print("Error ?!!" + '  ' + str(e))

            realStartTime = round(time.time() * 1000)
            cost = wb.schedule(startTime, deadline)
            wb.getPolicy().computeESTandEFT(startTime)
            wb.getPolicy().computeLSTandLFT(deadline)
            realFinishTime = round(time.time() * 1000)
            realFinishTime -= realStartTime
            finishTime = wb.graph.getNodes()[wb.graph.getEndId()].getEST()
            message = "\n\nICPC finishT < deadline: " + \
                      str((finishTime < deadline)) + \
                      "\n" + "deadline : " + str(deadline) + \
                      "\t\tcost of icpc: " + str(cost) + "\n" + \
                      "solution: \n"

            #                       str(wb.getPolicy().solutionAsString())
            ######### testing for table

            wb.getPolicy().solutionAsString()
            print(message)

            try:
                wb = WorkflowBroker(workflowPath, ScheduleType.IC_PCPD2_2)
                wb.getPolicy().computeESTandEFT(startTime)
                wb.getPolicy().computeLSTandLFT(deadline)
                wb.getPolicy().distributeDeadline()


                # PSO
                """
                lacoSOL = None
                methods = [PSO(100)]
                for scheduler in methods:
                    wf = Workflow(workflowPath)
                """
                print("=================================MY_ACO")
                problemRepresentation = CloudAcoProblemRepresentation(wb.graph, wb.resources, Constants.BANDWIDTH, deadline, 6)
                environment = CloudAcoEnvironment(problemGraph=problemRepresentation)
                cloudACO = CloudACO()
                cloudACO.schedule(environment, deadline)
                print("==================================MY_ACO")
                return
            except Exception as e:
                print("EEEEEException" + str(e))
                print(e)
                return

            alpha += 1.0

    def printWorkflow(self, g):
        pass

    def main(self):
        self.scheduleWorkflow()
        # CloudAcoWorkflow.printSolution()


x = test()
x.main()
