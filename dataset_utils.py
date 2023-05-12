# Node type {'Gather Merge', 'Bitmap Heap Scan', 'Materialize', 'Merge Join', 
# 'Seq Scan', 'Nested Loop', 'Bitmap Index Scan', 'Hash Join', 'Index Scan', 'Gather', 'Sort', 'Hash'}
#{'Hash Join', 'Merge Join', 'Gather Merge', 'Materialize', 'Hash', 'Gather', 'Bitmap Heap Scan', 
# 'Nested Loop', 'Seq Scan', 'Bitmap Index Scan', 'Index Scan'}


class Constraint:
    def __init__(self):
        self.filter = dict()
        self.join = dict()
    def add_filter(self, table, constraint, card):
        constraint = ",".join(constraint)
        if table in self.filter:
            self.filter[table].add(constraint, card)
        else:
            item = Filter()
            item.add(constraint, card)
            self.filter[table] = item

    def add_join(self, type, constraint, card):
        if type in self.constraints_multi_table.keys():
            self.constraints_multi_table[type].add(constraint, card)
        else:
            item = getattr()


class Filter:
    def __init__(self):
        self.predicates = dict()

    def add(self, predicate, card):
        if predicate not in self.predicates.keys():
            self.predicates[predicate] = card


class Join:
    def __init__(self):
        self.joins = dict()

    def add(self, join, card):
        if join not in self.joins:
            self.joins[join] = card

class Operator:
    def __init__(self) -> None:
        pass

    def step(self, plan, constraints):
        name = plan['Node Type']
        assert name in  ['Gather Merge', 'Bitmap Heap Scan', 'Materialize', 'Merge Join', 
                         'Seq Scan', 'Nested Loop', 'Bitmap Index Scan', 'Hash Join', 'Index Scan', 'Gather', 'Sort', 'Hash']
        name = "_".join(name.split("\s"))
        return getattr(self, name, plan, constraints)
    
    #顺序扫描Seq Scan
    def seq_scan(self, plan, constraints):
        card = plan['Actual Rows']
        table = plan['Relation Name']
        filter = plan['Filter'].split(" AND ") # keyword_id > 2484 [AND ...]
        constraints.add_filter(table, filter, card)
        return table
    
    #索引扫描Index Scan
    def index_scan(self, plan, constraints):
        card = plan['Actual Rows']
        table = plan['Relation Name']
        cond = plan['Index Cond']
        constraint = []
        constraint.append(cond)
        try:
            filter = plan['Filter']
            remove_by_filter = plan['Rows Removed by Filter']
            constraints.add_filter(table, constraint, card+remove_by_filter)
            constraint.append(filter)
        except:
            pass
        constraints.add_filter(table, constraint, card)
        return table
    
    
    
    
    
    
    
    
    
    def gather_merge(self,plan,constraints):
        pass
    
    def bitmap_heap_scan(self, plan, constraints):
        card = plan['Actual Rows']
        table = plan['Relation Name']
        constraint = []
        cond = plan['Recheck Cond']
        constraint.append(cond)
        try:
            filter = plan['Filter']
            remove_by_filter = plan['Rows Removed by Filter']
            constraints.add_single(table, constraint,
                                   card+remove_by_filter)
            constraint.append(filter)
        except:
            pass
        constraints.add_single(table, constraint, card)
        return table
   
    def materialize(self, plan, constraints):
        pass 
    
    def index_scan(self, plan, constraints):
        card = plan['Actual Rows']
        table = plan['Relation Name']
        constraint = []
        cond = plan['Index Cond']
        constraint.append(cond)
        try:
            filter = plan['Filter']
            remove_by_filter = plan['Rows Removed by Filter']
            constraints.add_single(table, constraint,
                                   card+remove_by_filter)
            constraint.append(filter)
        except:
            pass
        constraints.add_single(table, constraint, card)
        return table

    def bitmap_index_scan(self, plan, constraints):
        card = plan['Actual Rows']
        table = plan['Relation Name']
        constraint = []
        constraint.append(plan['Index Cond'])
        constraints.add_single(table, constraint, card)
        return table



    def nested_loop(self,plan,constraints,children):
        card = plan['Actual Rows']
        join = []
        for child in children:
            if isinstance(child,tuple):
                cond = child[0]
                conds = cond.split("=")
                left_attr = conds[0]
                right_attr = conds[1].split(".")[1]
                right_table = child[1]
            else:
                left_table = child
        join.append((left_table,left_attr))
        join.append((right_table,right_attr))
        constraints.add_multi(join,card)
                
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