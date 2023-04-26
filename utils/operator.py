#Node type {'Gather Merge', 'Bitmap Heap Scan', 'Materialize', 'Merge Join', 'Seq Scan', 'Nested Loop', 'Bitmap Index Scan', 'Hash Join', 'Index Scan', 'Gather', 'Sort', 'Hash'}


#
class Operator:
    def __init__(self) -> None:
        pass
    def step(self,name,child,constraint,cardinality):
        name = "_".join(name.split("\s"))
        return getattr(self,name,child,constraint,cardinality)
    