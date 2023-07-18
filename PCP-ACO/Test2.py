from WorkflowBroker import WorkflowBroker
from ypstruct import structure
from math import ceil
import traceback
import time


def computeFastest(WfFile, startTime, deadline):
    MH = 0
    try:
        wb = WorkflowBroker(WfFile, "Fastest")
        CH = wb.schedule(startTime, deadline, None)
        MH = wb.graph.getNodes()[wb.graph.getEndId()].getAST()
        print("Fastest: cost= " + str(CH) + " time= " + str(MH))
    except Exception as e:
        print("Error in creating workflow broker!!!" + '  ' + str(e))

    return MH


def computeCheapest(wfFile, startTime, deadline):
    MC = 0
    try:
        wb = WorkflowBroker(wfFile, "Cheapest")
        CC = wb.schedule(startTime, deadline, None)
        MC = wb.graph.getNodes()[wb.graph.getEndId()].getAST()
        print("Cheapest: cost= " + str(CC) + " time= " + str(MC))
    except Exception as e:
        print("Error in creating workflow broker!!!!" + '  ' + str(e))

    return MC


workflowPath = "../Workflows/Epigenomics_100.xml"
startTime = 0
MH = computeFastest(workflowPath, startTime, 1000)
MC = computeCheapest(workflowPath, startTime, 1000)
deadline_factor = 5

# new deadline for workflow
deadline = ceil(deadline_factor * MH)


wb = WorkflowBroker(workflowPath, "IC_PCP2")
cost, IC_PCP_DIC = wb.schedule(startTime, deadline, None)

finishTime = wb.graph.getNodes()[wb.graph.getEndId()].getEFT()
message = "\n\nICPCP finishT < deadline: " + \
            str((finishTime < deadline)) + " --> " + str(finishTime) + \
            "\n" + "deadline : " + str(deadline) + \
            "\t\tcost of icpc: " + str(cost) + "\n" + \
            "solution: \n"

print(message)

IC_PCP = structure()
IC_PCP.cost = cost
IC_PCP.solution = IC_PCP_DIC

# Create PCP-ACO
try:

    wb = WorkflowBroker(workflowPath, "PCP_ACO")

    # Scheduling using PCP_ACO
    wb.schedule(startTime, deadline, IC_PCP)

except Exception as e:
    print("Error ?!!" + '  ' + str(e))
    traceback.print_exc()
