import copy
from debug import draw_tree


def cacl_volumn(mins, maxs):
    vol = 1.
    for min, max in zip(mins, maxs):
        vol *= (max-min)
    return vol


class Bucket(object):
    def __init__(self, mins, maxs, freq=0, children=None, vol=True):
        self.mins = mins
        self.maxs = maxs
        self.freq = freq
        self.children = [] if children is None else children
        if vol:
            self.volume = cacl_volumn(mins, maxs)
        else:
            self.volume = 0


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
    if are_coincide(query, hist):
        return True
    c_volumn = 0
    for child in hist.children:
        if not are_disjoint(query, child):  # 相交
            overlap = get_overlap(query, child)
            if not are_covered(overlap, child):
                return False
            c_volumn += overlap.volume
    if abs(c_volumn - query.volume) > 1e-10:
        return False
    return True


def recursive_split(dim, b_min, b_max, father, box):
    to_append = []
    to_remove = []
    for child in father.children:
        cbox = Bucket(child.mins[:], child.maxs[:],vol=False)
        c_min = child.mins[dim]
        c_max = child.maxs[dim]
        if c_min < b_min and c_max > b_min:
            if c_max > b_max:
                cbox.mins[dim] = b_min
                cbox.maxs[dim] = b_max
                cbox.volume = cacl_volumn(cbox.mins,cbox.maxs)
                abox = Bucket(child.mins[:], child.maxs[:],vol=False)
                abox.mins[dim] = b_max
                abox.volume = cacl_volumn(abox.mins, abox.maxs)
                to_append.append(abox)
            else:
                cbox.mins[dim] = b_min
                cbox.volume = cacl_volumn(cbox.mins,cbox.maxs)
            child.maxs[dim] = b_min
            child.volume = cacl_volumn(child.mins,child.maxs)
            box.children.append(cbox)
            recursive_split(dim, b_min, b_max, child, cbox)
        elif c_max > b_max and c_min < b_max:
            cbox.maxs[dim] = b_max
            cbox.volume = cacl_volumn(cbox.mins,cbox.maxs)
            child.mins[dim] = b_max
            child.volume = cacl_volumn(child.mins,child.maxs)
            box.children.append(cbox)
            recursive_split(dim, b_min, b_max, child, cbox)
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


def construct(queries, table_mins, table_maxs, num_tuples):
    root = Bucket(table_mins, table_maxs, num_tuples)
    for query in queries:
        q_min = [query.hyperrange[0][0],query.hyperrange[1][0]]
        q_max = [query.hyperrange[0][1],query.hyperrange[1][1]]
        query = Bucket(q_min,q_max)
        #print(query.mins, query.maxs)
        father = find_father(query, root)
        if not are_covered(query, father):
            feed(father, query)
    to_remove = []
    check(root, to_remove)
    print(len(to_remove))
    #delete_repeat(root, to_remove)
    return root


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
            query.children.append(overlap)

            insight_mins = child.mins[:]
            insight_maxs = child.maxs[:]

            for i, (o_min, c_min, o_max, h_max) in enumerate(zip(overlap.mins, child.mins, overlap.maxs, child.maxs)):
                if abs(o_min - c_min) > 1e-10:
                    box = Bucket(insight_mins[:], insight_maxs[:],vol=False)
                    box.mins[i] = c_min
                    box.maxs[i] = o_min
                    box.volume = cacl_volumn(box.mins,box.maxs)
                    recursive_split(i, c_min, o_min, child, box)
                    to_append.append(box)
                if abs(o_max - h_max) > 1e-10:
                    box = Bucket(insight_mins[:], insight_maxs[:],vol=False)
                    box.mins[i] = o_max
                    box.maxs[i] = h_max
                    box.volume = cacl_volumn(box.mins,box.maxs)
                    recursive_split(i, o_max, h_max, child, box)
                    to_append.append(box)
                insight_mins[i] = o_min
                insight_maxs[i] = o_max
            """ if not are_covered(overlap, child):
                overlap.children = child.children """
    root.children.append(query)
    root.children += to_append
    for b in to_remove:
        root.children.remove(b)


def check(root, to_remove):
    vol = 0
    for child in root.children[:]:
        check(child, to_remove)
        vol += child.volume
    if abs(vol-root.volume) < 1e-10:
        to_remove.append(root)
def delete_repeat(root,to_remove):
    for child in root.children[:]:
        delete_repeat(child,to_remove)
        if child in to_remove:
            root.children.remove(child)
            root.children+=child.children
    
    

def test():
    queries = [Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
               Bucket(mins=[0.3, 0.65], maxs=[0.5, 0.7]),
               Bucket(mins=[0.3, 0.5], maxs=[0.5, 0.8]),
               Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6]), ]

    queries = [
        Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
        Bucket(mins=[0.3, 0.3], maxs=[0.8, 0.8]),
        Bucket(mins=[0.7, 0.1], maxs=[0.8, 0.8]),
        Bucket(mins=[0.3, 0.2], maxs=[0.6, 0.8]),
        Bucket(mins=[0.3, 0.2], maxs=[0.6, 0.8]),
        Bucket(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
        Bucket(mins=[0.1, 0.65], maxs=[0.5, 0.7]),
    ]
    hist = construct(queries, [0, 0], [1, 1], 1000)
    

    for i, c in enumerate(hist.children):
        print("num", i)
        draw_tree(c, i)
    draw_tree(hist, 100)
    return hist


#test()
