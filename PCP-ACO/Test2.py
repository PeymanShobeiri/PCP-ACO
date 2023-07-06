from WorkflowBroker import WorkflowBroker
from math import ceil
import traceback
import time


def computeFastest(WfFile, startTime, deadline):
    MH = 0
    try:
        wb = WorkflowBroker(WfFile, "Fastest")
        CH = wb.schedule(startTime, deadline)
        MH = wb.graph.getNodes()[wb.graph.getEndId()].getAST()
        print("Fastest: cost= " + str(CH) + " time= " + str(MH))
    except Exception as e:
        print("Error in creating workflow broker!!!" + '  ' + str(e))

    return MH


def computeCheapest(wfFile, startTime, deadline):
    MC = 0
    try:
        wb = WorkflowBroker(wfFile, "Cheapest")
        CC = wb.schedule(startTime, deadline)
        MC = wb.graph.getNodes()[wb.graph.getEndId()].getAST()
        print("Cheapest: cost= " + str(CC) + " time= " + str(MC))
    except Exception as e:
        print("Error in creating workflow broker!!!!" + '  ' + str(e))

    return MC


workflowPath = "/Users/apple/Desktop/make_fast/Workflows/Montage_25.xml"
startTime = 0
MH = computeFastest(workflowPath, startTime, 1000)
deadline_factor = 1.5

# new deadline for workflow
deadline = ceil(deadline_factor * MH)

# Create PCP-ACO
try:
    wb = WorkflowBroker(workflowPath, "PCP_ACO")

    # Scheduling using PCP_ACO

    wb.schedule(startTime, deadline)


except Exception as e:
    print("Error ?!!" + '  ' + str(e))
    traceback.print_exc()
