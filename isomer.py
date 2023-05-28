from debug import draw_tree


def cacl_volumn(mins, maxs):
    vol = 1.
    for min, max in zip(mins, maxs):
        vol *= (max-min)
    return vol


class SimpleBox(object):
    def __init__(self, mins, maxs, freq=0):
        self.mins = mins
        self.maxs = maxs
        self.freq = freq


class Bucket(object):
    def __init__(self, mins, maxs, freq=0, children=None):
        self.mins = mins
        self.maxs = maxs
        self.freq = freq
        self.children = [] if children is None else children
        self.volume = cacl_volumn(mins, maxs)


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


def are_covered(query, hist: Bucket):
    # 检查当前查询是否被直方图包含
    if are_coincide(query, hist):
        return True
    q_volumn = cacl_volumn(query.mins, query.maxs)
    c_volumn = 0
    for child in hist.children:
        if not are_disjoint(query, child):
            overlap = get_overlap(query, child)
            if not are_covered(overlap, child):
                return False
            c_volumn += overlap.volume
    if abs(c_volumn - q_volumn)>1e-3:
        return False
    return True


def feed_a_query(query, hist):
    father = find_father(query, hist)
    q_box = Bucket(query.mins, query.maxs, 0)
    feed(q_box, father)
    father.children.append(q_box)


def split(hist, overlap, child):
    hist.children+=child.children
    hist.children.remove(child)
    insight_mins = child.mins[:]
    insight_maxs = child.maxs[:]
    for i, (o_min, h_min, o_max, h_max) in enumerate(zip(overlap.mins, child.mins, overlap.maxs, child.maxs)):
        if o_min != h_min:
            box = Bucket(insight_mins[:], insight_maxs[:])
            box.mins[i] = h_min
            box.maxs[i] = o_min
            hist.children.append(box)
        if o_max != h_max:
            box = Bucket(insight_mins[:], insight_maxs[:])
            box.mins[i] = o_max
            box.maxs[i] = h_max
            hist.children.append(box)
        insight_mins[i] = o_min
        insight_maxs[i] = o_max


def feed(query, father):
    for child in father.children:
        if are_contain(query, child):
            query.children.append(child)
            father.children.remove(child)
        elif are_intersect(child, query):
            overlap = get_overlap(query, child)
            query.children.append(overlap)
            feed(overlap, child)
            split(father, overlap, child)


def find_father(query, hist):
    for child in hist.children:
        if are_contain(child, query):
            return find_father(child, query)
        elif are_intersect(child, query):
            return hist
    return hist


def ismoer(queries, table_mins, table_maxs, num_tuples):
    root = Bucket(table_mins, table_maxs, num_tuples)
    for query in queries:
        if not are_covered(query, root):
            feed_a_query(query, root)
    return root


def test():
    queries = [SimpleBox(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
               SimpleBox(mins=[0.3, 0.65], maxs=[0.5, 0.7]), 
               SimpleBox(mins=[0.3, 0.5], maxs=[0.5, 0.8]), 
               SimpleBox(mins=[0.1, 0.1], maxs=[0.6, 0.6]),]
    
    queries = [
               SimpleBox(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
               SimpleBox(mins=[0.3, 0.3], maxs=[0.8, 0.8]),
               SimpleBox(mins=[0.7, 0.1], maxs=[0.8, 0.8]),
               SimpleBox(mins=[0.1, 0.1], maxs=[0.6, 0.6]),
               ]
    hist = ismoer(queries, [0, 0], [1, 1], 1000)
    draw_tree(hist)
    return hist


test()
