from utils.process import get_plan, parse_plan
from operators import Operator
import constants
import pickle
import os
class Constraint:
    def __init__(self) -> None:
        self.constraints_single_table = dict()
        self.constraints_multi_table = dict()
    def add_single(self,relation,constraint,cardinality):
        constraint=",".join(constraint)
        if relation in self.constraints_single_table.keys():
            self.constraints_single_table[relation].add(constraint,cardinality)
        else:
            item = Predicate()
            item.add(constraint,cardinality)
            self.constraints_single_table[relation] = item
            
    def add_multi(self,type,constraint,cardinality):
        if type in self.constraints_multi_table.keys():
            self.constraints_multi_table[type].add(constraint,cardinality)
        else:
            item = getattr()
            

class Predicate:
    def __init__(self):
        self.predicates = dict()
    def add(self,predicate,cardinality):
        if predicate not in self.predicates.keys():
            self.predicates[predicate]=cardinality
class Join:
    def __init__(self):
        self.joins = dict()
    def add(self,join,cardinality):
        if join not in self.joins:
            self.joins[join] = cardinality

def check_node(plan,nodetype):
    head = plan['Node Type']
    nodetype.add(head)
    try:
        for child in plan['Plans']:
            check_node(child,nodetype)
    except:
        pass
def check(query,plan,constraints):
    pre_relation = []
    try:
        for child in plan['Plans']:
            pre_relation.append(check(query,child,constraints))
    except:
        pass
    head = plan['Node Type']
    if plan['Parallel Aware'] == False:
        if head == "Bitmap Heap Scan":
            return bitmap_heap_scan(plan,constraints)
        elif head == "Bitmap Index Scan":
            return bitmap_index_scan(plan,constraints)
        elif head == "Seq Scan":
            return seq_scan(plan,constraints)
        elif head == "Hash":
            return pre_relation
        elif head == 'Sort':
            print(query)
            print(plan)
        #Merge Join
        elif head == 'Nested Loop':
            constraints.add_multi(pre_relation)
            return 
        elif head == 'Gather':
            
        , , 'Merge Join', 'Hash Join'
        pass
#索引扫描
def index_scan(plan,constraints,pre_relation=None,join=False):
        cardinality = plan['Actual Rows']
        relation = plan['Relation Name']
        constraint=[]
        cond = plan['Index Cond']
        constraint.append(cond)
        try:
            filter = plan['Filter']
            remove_by_filter = plan['Rows Removed by Filter']
            constraints.add_single(relation,constraint,cardinality+remove_by_filter)
            constraint.append(filter)
        except:
            pass
        constraints.add_single(relation,constraint,cardinality)
        return relation
#位图堆扫描
def bitmap_heap_scan(plan,constraints,pre_relation=None):
    cardinality = plan['Actual Rows']
    relation = plan['Relation Name']
    constraint=[]
    cond = plan['Recheck Cond']
    constraint.append(cond)
    try:
        filter = plan['Filter']
        remove_by_filter = plan['Rows Removed by Filter']
        constraints.add_single(relation,constraint,cardinality+remove_by_filter)
        constraint.append(filter)
    except:
        pass
    constraints.add_single(relation,constraint,cardinality)
    return relation
#位图索引扫描      
def bitmap_index_scan(plan,constraints,pre_relation=None):
    cardinality = plan['Actual Rows']
    relation = plan['Relation Name']
    constraint=[]
    constraint.append(plan['Index Cond'])
    constraints.add_single(relation,constraint,cardinality)
    return relation
#顺序扫描
def seq_scan(plan,constraints,pre_relation=None):
    cardinality = plan['Actual Rows']
    relation = plan['Relation Name']
    filter = plan['Filter']
    constraint = filter.split(" AND ")
    constraints.add_single(relation,constraint,cardinality)
    return relation

def hash(plan,constraints,pre_relation=None):
    return pre_relation



#Join 
#嵌套循环
def nested_loop():
    pass
#归并连接
def merge_join():
    pass
#哈希连接
def hash_join():
    pass
#并行计算
#Gather
def gather():
    pass

if __name__ == "__main__":
    plans_path = constants.data_root/"plan.pkl"
    queries_path = constants.spj
    # 获取查询计划
    if plans_path.exists():
        with open(constants.data_root/"plan.pkl", "rb") as f:
            queries, plans = pickle.load(f)
    else:
        queries, plans = get_plan(queries_path, plans_path)
    
    #debug
    constraints = Constraint()
    nodetype = set()
    for plan,query in zip(plans,queries):
        root =  plan[0]['Plan']['Node Type']
        """ if root =='Hash Join':
            check_node(plan[0]['Plan'],nodetype)
            print(query)
            print(plan) """
        """if root == 'Index Scan':
            index_scan(plan[0]['Plan'],constraints)
        elif root == 'Bitmap Heap Scan':
            bitmap_heap_scan(plan[0]['Plan'],constraints)
        elif root == "Seq Scan":
            seq_scan(plan[0]['Plan'],constraints) """
            
            
           
        check(query,plan[0]['Plan'],constraints)
    #print(constraints.constraints_single_table['cast_info'].predicates)
    print(nodetype)
    #解析查询计划
    #plans = parse_plan(plans)
    
    #查询计划分类
    #1.select/join
    #2. table
    
    #TODO 根据查询计划还原表

