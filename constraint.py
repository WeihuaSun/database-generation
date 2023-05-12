
# 基本约束

#范围约束，包括等值约束

class Range(object):
    
    


class Constraint:
    def __init__(self):

        self.constraints_single_table = dict()
        self.constraints_multi_table = dict()

    def add_single(self, relation, constraint, cardinality):
        constraint = ",".join(constraint)
        if relation in self.constraints_single_table.keys():
            self.constraints_single_table[relation].add(
                constraint, cardinality)
        else:
            item = Predicate()
            item.add(constraint, cardinality)
            self.constraints_single_table[relation] = item

    def add_multi(self, type, constraint, cardinality):
        if type in self.constraints_multi_table.keys():
            self.constraints_multi_table[type].add(constraint, cardinality)
        else:
            item = getattr()


class Predicate:
    def __init__(self):
        self.predicates = dict()

    def add(self, predicate, cardinality):
        if predicate not in self.predicates.keys():
            self.predicates[predicate] = cardinality

#连接子类
class Join(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right
        if self.left is None:
            self.type = 'leaf'
        else:
            self.type = 'inner'
        return self


class Constraint:
    def __init__(self):

        pass
