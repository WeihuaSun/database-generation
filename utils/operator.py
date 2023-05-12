# Node type {'Gather Merge', 'Bitmap Heap Scan', 'Materialize', 'Merge Join', 
# 'Seq Scan', 'Nested Loop', 'Bitmap Index Scan', 'Hash Join', 'Index Scan', 'Gather', 'Sort', 'Hash'}
#{'Hash Join', 'Merge Join', 'Gather Merge', 'Materialize', 'Hash', 'Gather', 'Bitmap Heap Scan', 
# 'Nested Loop', 'Seq Scan', 'Bitmap Index Scan', 'Index Scan'}




class Operator:
    def __init__(self) -> None:
        pass

    def step(self, plan, constraints):
        name = plan['Node Type']
        assert name in  ['Gather Merge', 'Bitmap Heap Scan', 'Materialize', 'Merge Join', 
                         'Seq Scan', 'Nested Loop', 'Bitmap Index Scan', 'Hash Join', 'Index Scan', 'Gather', 'Sort', 'Hash']
        name = "_".join(name.split("\s"))
        return getattr(self, name, plan, constraints)
    

    def gather_merge(self,plan,constraints):
        pass
    
    def bitmap_heap_scan(self, plan, constraints):
        cardinality = plan['Actual Rows']
        relation = plan['Relation Name']
        constraint = []
        cond = plan['Recheck Cond']
        constraint.append(cond)
        try:
            filter = plan['Filter']
            remove_by_filter = plan['Rows Removed by Filter']
            constraints.add_single(relation, constraint,
                                   cardinality+remove_by_filter)
            constraint.append(filter)
        except:
            pass
        constraints.add_single(relation, constraint, cardinality)
        return relation
   
    def materialize(self, plan, constraints):
        pass 
    
    def index_scan(self, plan, constraints):
        cardinality = plan['Actual Rows']
        relation = plan['Relation Name']
        cond = plan['Index Cond']
        
        constraint = []
        constraint.append(cond)
        try:
            filter = plan['Filter']
            remove_by_filter = plan['Rows Removed by Filter']
            constraints.add_single(relation, constraint,
                                   cardinality+remove_by_filter)
            constraint.append(filter)
        except:
            pass
        constraints.add_single(relation, constraint, cardinality)
        return relation

    def bitmap_index_scan(self, plan, constraints):
        cardinality = plan['Actual Rows']
        relation = plan['Relation Name']
        constraint = []
        constraint.append(plan['Index Cond'])
        constraints.add_single(relation, constraint, cardinality)
        return relation

    def seq_scan(self, plan, constraints):
        cardinality = plan['Actual Rows']
        relation = plan['Relation Name']
        filter = plan['Filter']
        constraint = filter.split(" AND ")
        constraints.add_single(relation, constraint, cardinality)
        return relation

    def nested_loop(self,plan,constraints,children):
        cardinality = plan['Actual Rows']
        join = []
        for child in children:
            if isinstance(child,tuple):
                cond = child[0]
                conds = cond.split("=")
                left_attr = conds[0]
                right_attr = conds[1].split(".")[1]
                right_relation = child[1]
            else:
                left_relation = child
        join.append((left_relation,left_attr))
        join.append((right_relation,right_attr))
        constraints.add_multi(join,cardinality)
                
        pass

    def merge_join():
        pass

    def hash_join():
        pass
    
    def gather():
        pass
    
    def sort():
        pass
    
    def hash():
        pass