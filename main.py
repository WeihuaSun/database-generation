
import json
from dataset_utils import Operator,Constraint
from pathlib import Path
import pandas as pd


def check_node(plan, nodetype):
    head = plan['Node Type']
    
    if head == 'Hash':
        print(plan)
    nodetype.add(head)
    try:
        for child in plan['Plans']:
            check_node(child, nodetype)
    except:
        pass
    

def check_type(plan, type, nodes,query=None):
    head = plan['Node Type']
    para = plan['Parallel Aware']
    loops = plan ['Actual Loops']
    #if  para and loops!=1:
    
    if head == type and loops!=1 and "Parallel False': False" in str(plan):
        #if plan['Index Cond'][-2].isnumeric():
            print(str(plan))
            if query is not None:
                print(query)
            nodes.append(plan)
    try:
        for child in plan['Plans']:
            check_type(child, type, nodes,query)
    except:
        pass


def traversePlan(plan, constraint):
    children = []
    try:
        for child in plan['Plans']:
            children.append(traversePlan(child, constraint))
    except:
        pass
    return Operator.step(plan, constraint, children)
import pickle

if __name__ == "__main__":
    plan_path = Path("./data/plan")
    plan_file = plan_path / "train_plan_part0.csv"
    sacle_file = plan_path / "scale.pkl"
    nodetype  = set()
    df = pd.read_csv(plan_file)
    nodes = [json.loads(plan)['Plan'] for plan in df['json']]
    with open(sacle_file,"rb") as f:
        q,nodes = pickle.load(f) 
    constraint = Constraint()
    typenodes = []
    for i,plan in enumerate(nodes):
        #traversePlan(plan)
        plan = plan[0]['Plan']
        check_type(plan,'Nested Loop' ,typenodes,q[i])#,Seq Scan,Index Scan,'Sort','Hash','Bitmap Index Scan','Bitmap Heap Scan'
        #check_node(plan,nodetype)
    with open("temp.txt","w") as f:
        f.write("\n".join([str(node) for node in typenodes]))
    



