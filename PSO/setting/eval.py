from Workflow import Workflow
from PSO import PSO

workflowPath = "/Users/apple/Desktop/ws_cloud_aco-develop/src/main/resources/WfDescFiles/Sipht_100.xml"
wf = Workflow(workflowPath)
wf.setDeadline(11457)
tmpc = 0
for i in range(5):
    ps = PSO(500)
    tmpc += ps.schedule(wf)

print("ave :  " + str(tmpc/5))
