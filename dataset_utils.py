
class Constraint:
    def __init__(self):
        self.all_filter = dict()
        self.filter = dict()
        self.join = []
        self.join_tree = []

    def add(self, node):
        if isinstance(node, FilterNode):
            if node.type:
                if node.table in self.filter:
                    self.filter[node.table].append(node)
                else:
                    self.filter[node.table] = [node]

            if node.table in self.all_filter:
                self.all_filter[node.table].append(node)
            else:
                self.all_filter[node.table] = [node]

        if isinstance(node, JoinNode):
            self.join.append(node)

    def add_join_tree(self, node):
        self.join_tree.append(node)

class FilterNode(object):
    def __init__(self, table, cond, card, type=True):
        self.table = table
        self.cond = cond
        self.card = card
        self.type = type

class JoinNode(object):
    def __init__(self, card, left=None, right=None, cond=None):
        self.left = left
        self.right = right
        self.cond = cond
        self.card = card
        if self.left is None:
            self.type = 'leaf'
        else:
            self.type = 'inner'

class LeafNode(object):
    def __init__(self, table, cond=None):
        self.table = table
        self.cond = cond

class Operator:
    def __init__(self) -> None:
        pass

    def step(self, plan, child, constraint):
        name = plan['Node Type']
        assert name in ['Gather Merge', 'Bitmap Heap Scan', 'Materialize', 'Merge Join',
                        'Seq Scan', 'Nested Loop', 'Bitmap Index Scan', 'Hash Join', 'Index Scan', 'Gather', 'Sort', 'Hash']
        name = "_".join(name.split(" ")).lower()
        return getattr(self, name)(plan, child, constraint)

    # 顺序扫描Seq Scan
    def seq_scan(self, plan, child, constraint):
        cond = []
        table = plan['Relation Name']
        if plan['Parallel Aware']:  # 并行
            card = plan['Actual Rows']*plan['Actual Loops']
            est = True
        else:
            card = plan['Actual Rows']
            est = False
        if 'Filter' in plan:
            cond = plan['Filter'].split(" AND ")
        node = FilterNode(table, cond, card, est)
        if len(cond)>0:
            constraint.add(node)
        return node

    # 索引扫描Index Scan
    def index_scan(self, plan, child, constraint):
        table = plan['Relation Name']
        if 'Index Cond' in plan:
            cond = plan['Index Cond']
            card = plan['Actual Rows']

            if plan['Parallel Aware']:  # 并行
                est = True
                factor = plan['Actual Loops']
            else:
                est = False
                factor = 1

            if cond[-2].isnumeric():
                cond = [cond]
                if 'Filter' in plan:
                    remove_by_filter = plan['Rows Removed by Filter']
                    node = FilterNode(
                        table, cond, (card+remove_by_filter)*factor,est)
                    constraint.add(node)
                    cond += plan['Filter'].split(" AND ")
                node = FilterNode(table, cond, card*factor, est)
                constraint.add(node)
            else:  # Nested Loop Join condition
                node = LeafNode(table, cond)
        else:  # Other Join condition
            node = LeafNode(table)
        return node

    # 位图哈希扫描
    def bitmap_heap_scan(self, plan, child, constraint):
        card = child[0].card
        table = plan['Relation Name']
        cond = [plan['Recheck Cond']]
        if 'Filter' in plan:
            filter = plan['Filter'].split(" AND ")
            remove_by_filter = plan['Rows Removed by Filter']
            node = FilterNode(table, cond, card+remove_by_filter)
            constraint.add(node)
            cond += filter
        node = FilterNode(table, cond, card)
        if len(cond)>0:
            constraint.add(node)
        return node

    # 位图索引扫描
    def bitmap_index_scan(self, plan, child, constraint):
        card = plan['Actual Rows']
        #table = plan['Relation Name']
        cond = [plan['Index Cond']]
        node = FilterNode(None, cond, card)
        #constraint.add(node)
        return node

    # 嵌套循环连接
    def nested_loop(self, plan, child, constraint):
        if "Parallel False': False" in str(plan):
            factor = 1
        else:
            factor = plan['Actual Loops']
        card = plan['Actual Rows']*factor
        node = JoinNode(card, child[0], child[1], child[1].cond)
        constraint.add(node)
        return node

    def merge_join(self, plan, child, constraint):
        if "Parallel False': False" in str(plan):
            factor = 1
        else:
            factor = plan['Actual Loops']
        card = plan['Actual Rows']*factor
        cond = plan['Merge Cond']
        node = JoinNode(card, child[0], child[1], cond)
        constraint.add(node)
        return node

    def hash_join(self, plan, child, constraint):
        if "Parallel False': False" in str(plan):
            factor = 1
        else:
            factor = plan['Actual Loops']
        card = plan['Actual Rows']*factor
        cond = plan['Hash Cond']
        node = JoinNode(card, child[0], child[1], cond)
        constraint.add(node)
        return node

    # 排序
    def sort(self, plan, child, constraint):
        child[0].card = plan['Actual Rows']
        return child[0]

    # 哈希
    def hash(self, plan, child, constraint):
        child[0].card = plan['Actual Rows']
        return child[0]

    #
    def gather_merge(self, plan, child, constraint):
        child[0].card = plan['Actual Rows']
        return child[0]

    #
    def gather(self, plan, child, constraint):
        child[0].card = plan['Actual Rows']
        return child[0]

    # 物化
    def materialize(self, plan, child, constraint):
        child[0].card = plan['Actual Rows']
        return child[0]

def traversePlan(plan, constraint):
    children = []
    if 'Plans' in plan:
        for child in plan['Plans']:
            ret = traversePlan(child, constraint)
            children.append(ret)
    result = Operator().step(plan, children, constraint)

    return result