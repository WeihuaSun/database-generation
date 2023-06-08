

import docplex.mp.model as cpx
import numpy as np
from debug import draw_tree
import pulp


def cacl_volumn(mins, maxs):
    vol = 1.
    for min, max in zip(mins, maxs):
        vol *= (max-min)
    return vol


class Bucket(object):
    def __init__(self, mins, maxs, card=0, children=None, vol=True):
        self.mins = mins
        self.maxs = maxs
        self.card = card
        self.children = [] if children is None else children
        if vol:
            self.volume = cacl_volumn(mins, maxs)
        else:
            self.volume = 0
        self.id = 0
        self.mark = True
        self.childid = []


def are_coincide(a, b):
    # 两个超立方体是否重合
    if a.mins == b.mins and a.maxs == b.maxs:
        return True
    return False


def are_intersect(a, b):
    # 两个超立方体是否相交
    if are_disjoint(a, b):
        return False
    if are_contain(a, b):
        return False
    if are_contain(b, a):
        return False
    return True


def get_overlap(a, b):
    # 两个超立方体重叠部分
    mins = [max(a_m, b_m) for a_m, b_m in zip(a.mins, b.mins)]
    maxs = [min(a_m, b_m) for a_m, b_m in zip(a.maxs, b.maxs)]
    return Bucket(mins, maxs, 0)


def are_contain(a, b):
    # a是否包含b
    for a_min, b_min in zip(a.mins, b.mins):
        if a_min > b_min:
            return False
    for a_max, b_max in zip(a.maxs, b.maxs):
        if a_max < b_max:
            return False
    return True


def are_disjoint(a, b):
    # 两个立方体是否分离
    for a_min, b_max in zip(a.mins, b.maxs):
        if a_min >= b_max:
            return True
    for a_max, b_min in zip(a.maxs, b.mins):
        if a_max <= b_min:
            return True
    return False


def are_covered(query: Bucket, hist: Bucket):
    # 检查当前查询是否被直方图包含
    def check(query, hist, volume: list):
        if are_coincide(query, hist):
            volume.append(hist.volume)
            return
        for child in hist.children:
            if not are_disjoint(query, child):  # 相交
                overlap = get_overlap(query, child)
                check(overlap, child, volume)
    volume = []
    check(query, hist, volume)
    if abs(np.sum(volume) - query.volume) < 1e-6:
        return True
    return False


def recursive_split(dim, b_min, b_max, father, box):
    to_append = []
    to_remove = []
    for child in father.children:
        cbox = Bucket(child.mins[:], child.maxs[:], vol=False)
        c_min = child.mins[dim]
        c_max = child.maxs[dim]
        if c_min < b_min and c_max > b_min:
            if c_max > b_max:
                cbox.mins[dim] = b_min
                cbox.maxs[dim] = b_max
                cbox.volume = cacl_volumn(cbox.mins, cbox.maxs)
                abox = Bucket(child.mins[:], child.maxs[:], vol=False)
                abox.mins[dim] = b_max
                abox.volume = cacl_volumn(abox.mins, abox.maxs)
                to_append.append(abox)
            else:
                cbox.mins[dim] = b_min
                cbox.volume = cacl_volumn(cbox.mins, cbox.maxs)
            child.maxs[dim] = b_min
            child.volume = cacl_volumn(child.mins, child.maxs)
            recursive_split(dim, b_min, b_max, child, cbox)
            box.children.append(cbox)

        elif c_max > b_max and c_min < b_max:
            cbox.maxs[dim] = b_max
            cbox.volume = cacl_volumn(cbox.mins, cbox.maxs)
            child.mins[dim] = b_max
            child.volume = cacl_volumn(child.mins, child.maxs)

            recursive_split(dim, b_min, b_max, child, cbox)
            box.children.append(cbox)
        elif c_min >= b_min and c_max <= b_max:
            box.children.append(child)
            to_remove.append(child)
    for b in to_remove:
        father.children.remove(b)
    father.children += to_append


def find_father(query, hist):
    for child in hist.children:
        if are_contain(child, query):
            return find_father(query, child)
        elif not are_disjoint(child, query):
            return hist
    return hist


def feed(root: Bucket, query: Bucket):
    to_remove = []
    to_append = []
    for child in root.children:
        if are_contain(query, child):
            query.children.append(child)
            to_remove.append(child)
        elif not are_disjoint(query, child):
            to_remove.append(child)
            overlap = get_overlap(query, child)
            insight_mins = child.mins[:]
            insight_maxs = child.maxs[:]
            for i, (o_min, c_min, o_max, c_max) in enumerate(zip(overlap.mins, child.mins, overlap.maxs, child.maxs)):
                if o_min != c_min:
                    box = Bucket(insight_mins[:], insight_maxs[:], vol=False)
                    box.mins[i] = c_min
                    box.maxs[i] = o_min
                    box.volume = cacl_volumn(box.mins, box.maxs)
                    recursive_split(i, c_min, o_min, child, box)
                    to_append.append(box)
                if o_max != c_max:
                    box = Bucket(insight_mins[:], insight_maxs[:], vol=False)
                    box.mins[i] = o_max
                    box.maxs[i] = c_max
                    box.volume = cacl_volumn(box.mins, box.maxs)
                    recursive_split(i, o_max, c_max, child, box)
                    to_append.append(box)
                insight_mins[i] = o_min
                insight_maxs[i] = o_max
            if a_full_cover_b(overlap, child):
                query.children += child.children
            else:
                overlap.children = child.children
                query.children.append(overlap)
    for b in to_remove:
        root.children.remove(b)
    root.children.append(query)
    root.children += to_append


def a_full_cover_b(a, b):
    v = 0
    for c in b.children:
        v += c.volume
    if a.volume == v:
        return True
    return False


def check(root):
    vol = 0
    for child in root.children:
        check(child)
        vol += child.volume
    if abs(vol-root.volume) < 1e-6:
        root.mark = False
        # print("Repeat")


def delete_repeat(root):
    for i in range(len(root.children)-1, -1, -1):
        child = root.children[i]
        delete_repeat(child)
        if child.mark == False:
            root.children.remove(child)
            root.children += child.children


def test():
    queries = [Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
               Bucket(mins=[0.3, 0.65], maxs=[0.5, 0.7]),
               Bucket(mins=[0.3, 0.5], maxs=[0.5, 0.8]),
               Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6]), ]

    queries = [
        Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6], card=100),
        Bucket(mins=[0.3, 0.3], maxs=[0.8, 0.8], card=150),
        Bucket(mins=[0.7, 0.1], maxs=[0.8, 0.8], card=200),
        Bucket(mins=[0.3, 0.2], maxs=[0.6, 0.8], card=250),
        # Bucket(mins=[0.3, 0.2], maxs=[0.6, 0.8]),
        # Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
        # Bucket(mins=[0.1, 0.65], maxs=[0.5, 0.7]),
    ]
    hist = construct(queries, [0, 0], [1, 1], 1000)

    for i, c in enumerate(hist.children):
        print("num", i)
        draw_tree(c, i)
    draw_tree(hist, 100)
    lp(queries, hist)
    return hist


def idhist(hist):
    i = 0
    variables = []
    stack = [hist]
    while stack:
        cur = stack.pop()
        #draw_tree(cur, i+10)
        stack += cur.children
        cur.id = i
        x = pulp.LpVariable(f"x{i}", lowBound=0, cat='Integer')
        variables.append(x)
        i += 1
    # sum_id(hist)
    return variables


def sum_id(hist):
    for child in hist.children:
        hist.childid.append(child.id)
        sum_id(child)
        hist.childid += child.childid[:]


def find_boxs(hist, query, cvals, cboxs):
    if are_coincide(query, hist):
        cvals.append(hist.id)
        cboxs.append(hist)
        # cvals+=hist.childid
    else:
        for child in hist.children:
            if not are_disjoint(query, child):  # 相交
                overlap = get_overlap(query, child)
                find_boxs(child, overlap, cvals, cboxs)


def lp(quries, hist):
    lpn = pulp.LpProblem("hist", sense=pulp.LpMinimize)
    variables = idhist(hist)

    """ for c in hist.children:
        for cc in hist.children:
            if not are_disjoint(c,cc) and c!=cc:
                print("Error") """
    lpn += variables[0]
    num_query = len(quries)
    for i, query in enumerate(quries):
        #print(f"Linner Program Add Constraint Step[{i}/{num_query}]")
        q = Bucket(query.mins, query.maxs)
        cvals = []
        cboxs = []
        #father = find_father(q, hist)
        find_boxs(hist, q, cvals, cboxs)
        vc = 0
        for c in cboxs:
            vc += c.volume
        if vc != q.volume:
            print("ErrorSS")
        k = 0
        for v in cvals:
            k += variables[v]
        lpn += (k == int(query.card))

    lpn.solve()
    print("Status:", pulp.LpStatus[lpn.status])
    vs = []
    for i, x in enumerate(variables):
        vs.append(x.varValue)
    stack = [hist]
    i = 0
    while stack:
        cur = stack.pop()
        stack += cur.children
        cur.card = vs[i]
        i += 1

    print(vs)
    est_error = 0
    err_q = []
    for i, query in enumerate(quries):
        q = Bucket(query.mins, query.maxs)
        est_card = get_card(hist, q)
        real_card = query.card
        if real_card != est_card:
            est_error += 1
            print("Error:", est_card-real_card)
            err_q.append(query)
    if err_q:
        for q in err_q:
            quries.remove(q)
        lp(quries, hist)
    print("EstError:", est_error)


def lp_cpx(queries, hist):
    opt_model = cpx.Model(name="Data Model")
    x_vars  = 
{(i,j): opt_model.integer_var(lb=l[i,j], ub= u[i,j],
                              name="x_{0}_{1}".format(i,j)) 
for i in set_I for j in set_J}

""" def repart(hist):
    freq = 0
    for child in hist.children:
        repart(child)
        freq+=child.card
    hist.card =  """


def get_card(hist, q):
    cvals = []
    father = find_father(q, hist)
    sum_card(father, q, cvals)
    return np.sum(cvals)


def sum_card(hist, query, cvals):
    if are_coincide(query, hist):
        cvals.append(hist.card)
    else:
        for child in hist.children:
            if not are_disjoint(query, child):  # 相交
                overlap = get_overlap(query, child)
                sum_card(child, overlap, cvals)


def construct(queries, table_mins, table_maxs, num_tuples):
    root = Bucket(table_mins, table_maxs, num_tuples)
    num_queries = len(queries)
    for i, q in enumerate(queries):
        print(f"Construct Histogram: Step[{i}/{num_queries}]")
        query = Bucket(q.mins, q.maxs)
        father = find_father(query, root)
        if not are_covered(query, father):
            feed(father, query)
    error = 0
    check(root)
    delete_repeat(root)

    """ for i,q in enumerate(queries):
        query = Bucket(q.mins, q.maxs)
        if query.volume == 0:
            continue
        father = find_father(query, root)
        if not are_covered(query, father):
            error+=1
            print("Error")
    print("Error Count",error)
    check(root) """
    return root


test()
