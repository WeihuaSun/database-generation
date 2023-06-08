
import json
from dataset_utils import parse_plan
from pathlib import Path
from debug import check_type,draw,draw_tree,check_node
import constants
from data_prepare import get_plan
from isomer import construct,lp

def run(plan_file,ranges,schema):
    df = get_plan(plan_file)
    plans = [json.loads(plan)['Plan'] for plan in df['json']]
    constraint = parse_plan(plans,ranges,schema,)
    hist = construct(constraint.filter['cast_info'],[0,0], [11,4061926], 1000)
    print("construct_over")
    #draw_tree(hist,"mi")
    lp(constraint.filter['cast_info'],hist)


if __name__ == "__main__":
    plan_path = Path("./data/plan")
    plan_file = plan_path / "synthetic_plan.csv"
    run(plan_file,constants.imdb_ranges,constants.imdb_schema)
    

    