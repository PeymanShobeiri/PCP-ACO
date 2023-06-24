
# PCP-ACO

## Table of Contents
- [Introduction](#introduction)
- [Usage](#usage)
- [Classes](#classes)
- [Examples](#examples)
- [Contributing](#contributing)


## Introduction
This repository contains an implementation of the **PCP-ACO** algorithm, which aims to find an optimal workflow schedule on cloud resources. The algorithm minimizes the total execution cost while meeting a user-defined deadline. PCP-ACO utilizes list scheduling with two phases: task prioritization and resource mapping.

In the first phase, the algorithm assigns priorities to each task by using the partial critical path (PCP) to distribute the workflow's overall deadline among its tasks. In the second phase, a topological sort of the workflow tasks is constructed, and each task is mapped to an appropriate resource based on its priority. Finally, the Ant Colony Optimization (ACO) algorithm is employed to select the proper resource for each task while ensuring sub-deadline constraints are met.

## Usage

To use the PCP-ACO algorithm, follow these steps:

1. [Clone](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) or [download](https://github.com/PeymanShobeiri/PCP-ACO/archive/main.zip) the repository.
2. Install the necessary dependencies.
3. Modify the algorithm parameters or settings if needed.
4. Choose your workflow from the workflow file.
5. Execute the program.

## Classes

This repository contains the following classes:

- `CheapestPolicy.py`: Implements the cheapest way to schedule jobs in a workflow.
- `FastestPolicy.py`: Implements the fastest way to schedule jobs by assigning them to the fastest resource.
- `CloudACO.py`: Implements the ACO algorithm for job scheduling on cloud environments. You can adjust parameters such as the number of ants, iteration count, alpha, and beta.
- `CloudResourceSet`: Represents the set of initial resources from which instances are created later.
- `Constants`: Contains constant variables such as bandwidth.
- `InstanceSet`: Represents the set of instances used for scheduling.
- `WorkflowBroker`: Converts the XML workflow file into a Directed Acyclic Graph (DAG) and sets the scheduling algorithm as the policy.
- `WorkflowGraph`: Represents the graph structure of the DAG, including its nodes and maximum parallelism.
- `WorkflowNode`: Represents a node in the DAG. Each node contains variables such as instance size, runtime, and scheduling-related variables like EFT, LST, LFT, AFT, etc.
- And other classes that implement policies such as IC-PCP, IC-PCPD2, and others.

## Examples

Here are a few examples of how to use the PCP-ACO algorithm:



```python
#choose your workflow
workflow_Path = "../Workflows/Epigenomics_24.xml"

# compute the EST, EFT, LST, LFT
wb = WorkflowBroker(workflow_Path, ScheduleType.IC_PCPD2_2)
wb.getPolicy().computeESTandEFT(startTime)
wb.getPolicy().computeLSTandLFT(deadline)

# distribute the deadline and assign sub-deadline to each node
wb.getPolicy().distributeDeadline()

# Finding the Max Parallel 
wb.getGraph().setMaxParallel(wb.getPolicy().FindMaxParallel())

# Create an environment for ants to travel
environment = CloudAcoEnvironment(CloudAcoProblemRepresentation(wb.graph, wb.resources, Constants.BANDWIDTH, deadline, MAX_Parallel))

# Create a PCP_ACO object for scheduling
PCP_ACO = CloudACO(environment.getProblemGraph().getGraphSize())
cost = PCP_ACO.schedule(environment, deadline)
```

## Contributing

Contributions to this repository are welcome. If you find any bugs, have feature requests, or want to contribute enhancements, please open an issue or submit a pull request.

When contributing, please ensure that your changes align with the coding style, conventions, and licensing of this repository. Also, provide a clear description of the problem or enhancement you are addressing.
