
from .Adag import Adag
# from DAG.Adag import Adag
from lxml import etree , objectify
from .FilenameType import FilenameType

class DagUtils:
    
    def readWorkflowDescription(wfdescFile) -> Adag:
        dag = Adag()
        with open(wfdescFile, 'rb') as f:
            try:
                xml = f.read()
            except FileNotFoundError:
                print("File not found! ")

        root = objectify.fromstring(xml)

        dag.setVersion(root.attrib['version'])
        dag.setName(root.attrib['name'])
        dag.setIndex(root.attrib['index'])
        dag.setCount(root.attrib['count'])
        dag.setJobCount(root.attrib['jobCount'])
        dag.setFileCount(root.attrib['fileCount'])
        dag.setChildCount(root.attrib['childCount'])

        jlist = []
        for i in range(int(dag.getJobCount())):
            tmp = Adag.Job()
            tmp.setId(root.job[i].attrib['id'])
            tmp.setNamespace(root.job[i].attrib['namespace'])
            tmp.setName(root.job[i].attrib['name'])
            tmp.setVersion(root.job[i].attrib['version'])
            tmp.setRuntime(root.job[i].attrib['runtime'])
            tmp2 = []
            for use in root.job[i].uses:
                file_t = FilenameType()
                file_t.setLink(use.attrib['link'])
                file_t.setOptional(use.attrib['optional'])
                file_t.setRegister(use.attrib['register'])
                file_t.setTransfer(use.attrib['transfer'])
                file_t.setType(use.attrib['type'])
                file_t.setSize(use.attrib['size'])
                tmp2.append(file_t)
            tmp.setUseList(tmp2)
            jlist.append(tmp)

        dag.setJobList(jlist)

        child_l = []
        for ch in root.child:
            tmp_child = Adag.Child()
            tmp_child.setRef(ch.attrib['ref'])
            parent_l= []
            for p in ch.parent:
                tmp_parent = Adag.Child.Parent()
                tmp_parent.setRef(p.attrib['ref'])
            parent_l.append(tmp_parent)
            tmp_child.setParentList(parent_l)
            child_l.append(tmp_child)

        dag.setChildList(child_l)

        return  dag












