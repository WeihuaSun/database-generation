
import json
from dataset_utils import Constraint, parse_plan, JoinNode
from pathlib import Path
import pandas as pd
import pickle
from debug import check_type,draw
import constants

if __name__ == "__main__":
    plan_path = Path("./data/plan")
    plan_file = plan_path / "train_plan_part0.csv"
    sacle_file = plan_path / "scale.pkl"
    nodetype = set()
    df = pd.read_csv(plan_file)
    nodes = [json.loads(plan)['Plan'] for plan in df['json']]
    """ with open(sacle_file,"rb") as f:
        q,nodes = pickle.load(f)  """
    constraint = Constraint()
    typenodes = []
    constraint,hyper_dict = parse_plan(nodes,constants.ranges,constants.imdb_schema)
    draw(hyper_dict['title'])
    
    
    """ for i, plan in enumerate(nodes):
        # traversePlan(plan)
        #plan = plan[0]['Plan']
        result = traversePlan(plan, constraint)
        if isinstance(result, JoinNode):
            constraint.add_join_tree(result)
        # check_type(plan,'Bitmap Index Scan' ,typenodes,q[i]) #,Seq Scan,Index Scan,'Sort','Hash','Bitmap Index Scan','Bitmap Heap Scan'
        # check_node(plan,nodetype) """

    """ with open("temp.txt","w") as f:
        f.write("\n".join([str(node) for node in typenodes])) """
