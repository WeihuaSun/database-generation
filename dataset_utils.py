
import re


class Constraint:
    def __init__(self):
        self.filter = dict()
        self.join = []
        self.join_tree = []
        self.norm_filter = []

    def add(self, node):
        if isinstance(node, FilterNode):
            if node.table in self.filter:
                self.filter[node.table].append(node)
            else:
                self.filter[node.table] = [node]

        if isinstance(node, JoinNode):
            self.join.append(node)

    def add_join_tree(self, node):
        self.join_tree.append(node)


class FilterNode(object):
    def __init__(self, table, cond, card):
        self.table = table
        self.cond = cond
        self.card = card
        self.mins = []
        self.maxs = []


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
    """
    实现了将部分操作符转换为约束的功能，这个版本不包括并行操作
    """

    def __init__(self):
        pass

    def step(self, plan, children, constraint):
        name = plan['Node Type']
        assert name in ['Sort', 'Bitmap Index Scan', 'BitmapAnd', 'Index Scan', 'Nested Loop',
                        'Materialize', 'Merge Join', 'Bitmap Heap Scan', 'Seq Scan', 'Hash', 'Hash Join']
        name = "_".join(name.split(" ")).lower()
        return getattr(self, name)(plan, children, constraint)

    # 顺序扫描Seq Scan
    def seq_scan(self, plan, children, constraint):
        cond = []
        table = plan['Relation Name']
        card = plan['Actual Rows']
        if 'Filter' in plan:
            cond = plan['Filter'].split(" AND ")
        node = FilterNode(table, cond, card)
        if cond:
            constraint.add(node)
        return node

    # 索引扫描Index Scan
    def index_scan(self, plan, children, constraint):
        table = plan['Relation Name']
        if 'Index Cond' in plan:
            cond = plan['Index Cond']
            card = plan['Actual Rows']
            if cond[-2].isnumeric():
                cond = [cond]
                if 'Filter' in plan:
                    remove_by_filter = plan['Rows Removed by Filter']
                    node = FilterNode(table, cond, card+remove_by_filter)
                    constraint.add(node)
                    cond = cond[:]+ plan['Filter'].split(" AND ")
                node = FilterNode(table, cond, card)
                constraint.add(node)
            else:  # Nested Loop Join condition
                node = LeafNode(table, cond)
        else:  # Other Join condition
            node = LeafNode(table)
        return node

    # 位图哈希扫描
    def bitmap_heap_scan(self, plan, child, constraint):
        card = plan['Actual Rows']
        table = plan['Relation Name']
        cond = plan['Recheck Cond'].split(" AND ")
        if 'Filter' in plan:
            remove_by_filter = plan['Rows Removed by Filter']
            node = FilterNode(table, cond, card+remove_by_filter)
            constraint.add(node)
            cond = cond[:]+plan['Filter'].split(" AND ")
        node = FilterNode(table, cond, card)
        constraint.add(node)
        return node

    # 位图索引扫描
    def bitmap_index_scan(self, plan, child, constraint):
        card = plan['Actual Rows']
        #table = plan['Relation Name']
        cond = plan['Index Cond'].split(" AND ")
        node = FilterNode(None, cond, card)
        # constraint.add(node)
        return node

    # 嵌套循环连接
    def nested_loop(self, plan, child, constraint):
        card = plan['Actual Rows']
        node = JoinNode(card, child[0], child[1], child[1].cond)
        constraint.add(node)
        return node

    # 归并连接
    def merge_join(self, plan, child, constraint):
        card = plan['Actual Rows']
        cond = plan['Merge Cond']
        node = JoinNode(card, child[0], child[1], cond)
        constraint.add(node)
        return node

    # 哈希连接
    def hash_join(self, plan, child, constraint):
        card = plan['Actual Rows']
        cond = plan['Hash Cond']
        node = JoinNode(card, child[0], child[1], cond)
        constraint.add(node)
        return node

    # 排序
    def sort(self, plan, child, constraint):
        #child[0].card = plan['Actual Rows']
        return child[0]

    # 哈希
    def hash(self, plan, child, constraint):
        #child[0].card = plan['Actual Rows']
        return child[0]

    #
    def gather_merge(self, plan, child, constraint):
        #child[0].card = plan['Actual Rows']
        return child[0]

    #
    def gather(self, plan, child, constraint):
        #child[0].card = plan['Actual Rows']
        return child[0]

    # 物化
    def materialize(self, plan, child, constraint):
        #child[0].card = plan['Actual Rows']
        return child[0]

    # 位图和
    def bitmapand(self, plan, child, constraint):
        return None




def normalize_filter(constraint, ranges):
    filters = constraint.filter
    regex = r"([a-z_]*)\s(<|>|<=|>=|=|!=)\s([0-9]*)"
    for t in ranges.keys():  # constraint list
        curcon = []
        t_filter = []
        for f in filters[t][:]:
            conds = f.cond[:]
            f.cond = []
            for cond in conds:
                rm = re.search(regex, cond)
                col, op, val = rm.group(1), rm.group(2), rm.group(3)
                val = int(val)
                f.cond.append([col, op, val])
            f.cond.sort()
            if f.cond not in curcon:
                curcon.append(f.cond)
                t_filter.append(f)
        filters[t] = t_filter


""" def fill_hypercube(hyper, op, val, i):
    min_val, max_val = hyper[i]
    if op == "=":
        if val < min_val or val > max_val:
            return False
        else:
            hyper[i] = (val, val)
    elif op == ">":
        if val < min_val:
            hyper[i] = (min_val, max_val)
        elif val >= max_val:
            return False
        else:
            hyper[i] = (val+1, max_val)

    elif op == "<":
        if val > max_val:
            hyper[i] = (min_val, max_val)
        elif val <= min_val:
            return False
        else:
            hyper[i] = (min_val, val-1)
    return True """

def fill_hypercube(hyper, op, val, i):
    min_val, max_val = hyper[i]
    if op == "=":
        if val < min_val+1 or val > max_val:
            return False
        else:
            hyper[i] = (val-1, val)
    elif op == ">":
        if val < min_val+1:
            hyper[i] = (min_val, max_val)
        elif val >= max_val:
            return False
        else:
            hyper[i] = (val, max_val)

    elif op == "<":
        if val > max_val:
            hyper[i] = (min_val, max_val)
        elif val <= min_val+1:
            return False
        else:
            hyper[i] = (min_val, val-1)
    return True


def package_filter(filter, schema, ranges):
    
    for t in schema.keys():
        to_remove = []
        attrs = schema[t]
        for f in filter[t]:
            range = [ranges[t][a] for a in attrs]
            flag = True
            for cond in f.cond:
                col, op, val = cond[0], cond[1], cond[2]
                i = attrs.index(col)
                if not fill_hypercube(range, op, val, i):
                    flag = False
                    break
            if flag:
                for r,mr in zip(range,ranges[t].values()):
                    min, max = mr
                    """ f.mins.append((r[0]-min)/(max-min))
                    f.maxs.append((r[1]-min)/(max-min)) """
                    f.mins.append(r[0])
                    f.maxs.append(r[1])
            else:
                to_remove.append(f)
        for rf in to_remove:
            filter[t].remove(rf)
        
                

def traverse_plan(plan, constraint):
    children = []
    if 'Plans' in plan:
        for child in plan['Plans']:
            ret = traverse_plan(child, constraint)
            children.append(ret)
    ret = Operator().step(plan, children, constraint)
    return ret

from data_prepare import valid_filter


def parse_plan(nodes, ranges, schema):
    # 解析查询计划，将其转换为约束
    constraint = Constraint()
    for plan in nodes:
        ret = traverse_plan(plan, constraint)
        if isinstance(ret, JoinNode):
            constraint.add_join_tree(ret)
    normalize_filter(constraint, ranges)
    
    package_filter(constraint.filter, schema, ranges)
    #valid_filter(constraint.filter)
    return constraint
