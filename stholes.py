import numpy as np
import pandas as pd
import json
from rtree import index

np.random.seed(0)
large_val = 100000




class RTree(object):
    def __init__(self, mins, maxs, freq):
        dim = 2*len(mins)
        self.p = index.Property()
        self.p.dimension = dim
        self.rtree = index.Index(
            'hist', interleaved=True, property=self.p, overwrite=True)
        self.rtree.insert(0, mins+maxs, obj=Bucket(freq))

    def insert(self, coordinates, freq):
        self.rtree.insert(self.rtree.get_size(), coordinates, obj=Bucket(freq))

    def delete(self, id, coordinates):
        self.rtree.delete(id, coordinates)

    def intersection(self, coordinates):
        return self.rtree.intersection(coordinates, objects=True)

    def count(self, coordinates):
        return self.rtree.count(coordinates)


class Box:
    def __init__(self, mins, maxs, freq, children=None):
        self.mins = mins
        self.maxs = maxs
        if children is None:
            self.children = []
        else:
            self.children = children
        self.freq = freq

    def volume_intersection(self, q):
        child_volume = 0
        for i, c in enumerate(self.children):
            if q is None:
                child_volume += np.prod(np.array(c.maxs)-np.array(c.mins))
            else:
                child_volume += get_box_intersection_volume(q, c)
        if q is None:
            parent_volume = np.prod(np.array(self.maxs)-np.array(self.mins))
        else:
            parent_volume = get_box_intersection_volume(q, self)
        return parent_volume - child_volume

    def in_box(self, p):
        if p[0] > self.maxs[0] or p[0] < self.mins[0]:
            return False
        if p[1] > self.maxs[1] or p[1] < self.mins[1]:
            return False
        return True

    def in_bucket(self, p):
        if not self.in_box(p):
            return False

        for c in self.children:
            if c.in_box(p):
                return False

        return True


def a_fully_contains_b(a, b):
    for a_min, b_min in zip(a.mins, b.mins):
        if a_min > b_min:
            return False
    for a_max, b_max in zip(a.maxs, b.maxs):
        if a_max < b_max:
            return False
    return True


def are_disjoint(a, b):
    for a_min, b_max in zip(a.mins, b.maxs):
        if a_min >= b_max:
            return True
    for a_max, b_min in zip(a.maxs, b.mins):
        if a_max <= b_min:
            return True
    return False


def boundary_overlaps(box, query):
    """检查超立方体是否相交

    Args:
        box (Box): 直方图超立方体
        query (Box): 查询超立方体

    Returns:
        bool: 超立方体相交
    """
    if a_fully_contains_b(box, query):
        return False
    if a_fully_contains_b(query, box):
        return False
    if are_disjoint(box, query):
        return False
    return True


def b_intersects_contains_q(b, q):
    for child in b.children:
        if a_fully_contains_b(child, q):
            return False

    if a_fully_contains_b(b, q):
        return True

    if not boundary_overlaps(b, q):
        return False

    return True


def find_intersections(q, curr_root, res):
    if are_disjoint(q, curr_root):
        return

    if b_intersects_contains_q(curr_root, q):
        res.append(curr_root)

    for child in curr_root.children:
        find_intersections(q, child, res)


def get_box_intersection_volume(q, b, should_print=False):
    if are_disjoint(q, b):
        return 0

    mins = [max([q.mins[0], b.mins[0]]), max([q.mins[1], b.mins[1]])]
    maxs = [min([q.maxs[0], b.maxs[0]]), min([q.maxs[1], b.maxs[1]])]
    if should_print:
        print("mins", mins)
        print("maxs", maxs)

    return np.prod(np.array(maxs)-np.array(mins))


def get_overlap_amount(q, b, dim):
    if q.mins[dim] >= b.maxs[dim]:
        return large_val
    if q.maxs[dim] <= b.mins[dim]:
        return large_val

    if q.mins[dim] >= b.mins[dim] and q.maxs[dim] <= b.maxs[dim]:
        return large_val

    if q.mins[dim] <= b.mins[dim] and q.maxs[dim] >= b.maxs[dim]:
        return b.maxs[dim]-q.mins[dim]

    if q.mins[dim] >= b.mins[dim]:
        return b.maxs[dim]-q.mins[dim]

    if q.maxs[dim] <= b.maxs[dim]:
        return b.maxs[dim]-q.mins[dim]


def get_q_res(q, D):
    count = 0
    for i in range(D.shape[0]):
        if not q.in_box(D[i]):
            continue
        count += 1

    return count


def count_int_points(q, b, noise_scale, D, remove=False):
    """_summary_

    Args:
        q (_type_): _description_
        b (_type_): _description_
        noise_scale (_type_): _description_
        D (_type_): _description_
        remove (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if are_disjoint(q, b):
        return 0, D
    count = 0
    keep_points = []
    for i in range(D.shape[0]):
        if not q.in_box(D[i]):
            keep_points.append(i)
            continue
        if not b.in_bucket(D[i]):
            keep_points.append(i)
            continue
        count += 1

    if remove:
        D = D[keep_points]
    else:
        i += 1

    return count + np.random.laplace(0, noise_scale), D


def get_intersecting_box(query, bucket):
    """ 获得两个超立方体相交产生的超立方体

    Args:
        query (Bucket): 查询超立方体
        bucket (Bucket): 直方图超立方体

    Returns:
        Bucket: 
    """
    mins = [max(q, b) for q, b in zip(query.mins, bucket.mins)]
    maxs = [min(q, b) for q, b in zip(query.maxs, bucket.maxs)]
    return Box(mins, maxs, 0)


def shrink_box(c, b, dim):
    if c.mins[dim] >= b.mins[dim]:
        c.mins[dim] = b.maxs[dim]
    else:
        c.maxs[dim] = b.mins[dim]


def shrink(query, box, dims):
    c = get_intersecting_box(query, box)  # 查询和直方图相交产生的超立方体
    participants = []  # Box的孩子节点
    for b_child in box.children:
        if boundary_overlaps(b_child, c):
            participants.append(b_child)

    while len(participants) != 0:
        min_size_change = large_val
        best_index = -1
        best_dim = -1
        for i, participant in enumerate(participants):
            for dim in range(dims):
                overlap = get_overlap_amount(c, participant, dim)
                if overlap < min_size_change:
                    min_size_change = overlap
                    best_index = i
                    best_dim = dim

        shrink_box(c, participants[best_index], best_dim)

        participants = []
        for b_child in box.children:
            if boundary_overlaps(b_child, c):
                participants.append(b_child)

    for b_child in b.children:
        if a_fully_contains_b(b_child, c):
            return None, 0

    if count_while_building:
        count = count_int_points(c, b, D)
        if t_bq == 0 or b.volume_intersection(q) == 0:
            count = 0
        else:
            count = t_bq*b.volume_intersection(c)/b.volume_intersection(q)
    else:
        count = 0

    return c, count


def drill_hole(b, shrunk_box, t_bc, q):
    children_to_move = []
    for i, c in enumerate(b.children):
        if a_fully_contains_b(shrunk_box, c):
            children_to_move.append(i)
            shrunk_box.children.append(c)
    for i in reversed(children_to_move):
        b.children.pop(i)

    b.children.append(shrunk_box)
    b.freq = max([0, b.freq-t_bc])
    shrunk_box.freq = t_bc


def set_freq(curr_root, noise_scale, D):
    bucket_count = 1
    q = box([-5, -5], [5, 5], 0)
    curr_root.freq, D = count_int_points(q, curr_root, noise_scale, D, True)
    # print(D.shape)

    for c in curr_root.children:
        c, D = set_freq(c, noise_scale, D)
        bucket_count += c

    return bucket_count, D


def get_answer(curr_root, q):
    if are_disjoint(q, curr_root):
        return 0

    ans = 0
    for c in curr_root.children:
        ans += get_answer(c, q)

    if curr_root.volume_intersection(None) != 0:
        ans += curr_root.freq * \
            (curr_root.volume_intersection(q)/curr_root.volume_intersection(None))
    return ans


def generate_tree(rectangle, dim, n):
    rtree = RTree(dim, n)
    for hyper in rectangle:
        coordinates = []
        for item in hyper.hyperrange:
            coordinates.append(item[0])
            coordinates.append(item[1])
        rtree.insert(coordinates, hyper.card)
    overleap = []
    for hyper in rectangle:
        coordinates = []
        for item in hyper.hyperrange:
            coordinates.append(item[0])
            coordinates.append(item[1])
        overleap.append(rtree.count(coordinates))
        print(rtree.count(coordinates))
    print(min(overleap))

    return rtree


def contains(hist, query):
    return True


def generate_hist(mins, maxs, queries, freq):
    rtree = RTree(mins, maxs, freq)
    root = Box(mins, maxs, freq)
    for q in queries:
        qmins = [c[0] for c in q.hyperrange]
        qmaxs = [c[1] for c in q.hyperrange]

        hits = rtree.intersection(qmins+qmaxs)
        q = Box(qmins, qmaxs, q.card)
        intersecting_boxes = []
        find_intersections(q, root, intersecting_boxes)
        for b in hits:
            shrink(b, q, t_bq, False)
        for j, b in enumerate(intersecting_boxes):
            t_bq = 0
            shrunk_box, t_bc = shrink(b, q, t_bq, count_while_building)
            if shrunk_box is None:
                continue

            drill_hole(b, shrunk_box, t_bc, q)
    return root


# mins = [-5, -5]
# maxs = [5, 5]
eps = 0.2
n = 1000
smooth = 0.001

D = np.random.rand(n, 2)*10-5
# q_size = 100
# test_q_size = 100
# #qs = [[min x min y], [max x, max y]]
# qs = np.sort(np.random.rand(q_size, 2, 2)*10-5, axis=1)
# test_qs = np.sort(np.random.rand(test_q_size, 2, 2)*10-5, axis=1)

# qs = [box([qs[i, 0, 0], qs[i, 0, 1]], [qs[i, 1, 0], qs[i, 1, 1]], 0) for i in range(q_size)]
# test_qs = [box([test_qs[i, 0, 0], test_qs[i, 0, 1]], [test_qs[i, 1, 0], test_qs[i, 1, 1]], 0) for i in range(test_q_size)]

# test_ress = [get_q_res(q, D) for q in qs]

count_while_building = False


# if count_while_building:
#     q_intersects = []
#     for i in range(len(qs)):
#         count = 0
#         for j in range(len(qs)):
#             if are_disjoint(qs[i], qs[j]):
#                 continue
#             count += 1

#         q_intersects.append(count)


# root = box(mins, maxs, n)
# for i, q in enumerate(qs):
#     print("processing q", i)
#     intersecting_boxes = []
#     find_intersections(q, root, intersecting_boxes)

#     for j, b in enumerate(intersecting_boxes):
#         t_bq = 0
#         if count_while_building:
#             noise_scale = q_intersects[i]/eps
#             t_bq = count_int_points(q, b, D, noise_scale)

#         shrunk_box, t_bc = shrink(b, q, t_bq, count_while_building)
#         if shrunk_box is None:
#             continue

#         drill_hole(b, shrunk_box, t_bc, q)

# if not count_while_building:
#     noise_scale = 1/eps
#     set_freq(root, noise_scale, D)


# err = 0
# for i, q in enumerate(qs):
#     res = get_answer(root, q)
#     err += abs(res-test_ress[i])/np.maximum(test_ress[i],smooth*n)
# print(err/q_size)


def rebuild(hist, query, box):
    overlap = get_intersecting_box(query, box)
    query.children.append(overlap)
    hist.insert(query)
    hist.delete(box)
    hist.insert()
    hist.insert()


def intersect(query, box):
    return


def feed(query, hist):
    find_intersection(query, hist)


def find_intersection(query, box):
    if intersect(query, box):
        rebuild()
        for child in box.children:
            find_intersection(query, box)


class Bucket(object):
    def __init__(self, mins, maxs, freq, children=None) -> None:
        self.mins = mins
        self.maxs = maxs
        self.freq = freq
        self.children = [] if children is not None else children
        self.volume = cacl_volumn(mins, maxs)


def cacl_volumn(mins, maxs):
    vol = 1.
    for min, max in zip(mins, maxs):
        vol *= (max-min)
    return vol


def get_overlap(a, b):

    return


# 两个超立方体的关系：1.相交（intersection） 2.包含(cover) 3.分离(disjoint)
def contains(a, b):

    for a_min, b_min in zip(a.mins, b.mins):
        if a_min > b_min:
            return False
    for a_max, b_max in zip(a.maxs, b.maxs):
        if a_max < b_max:
            return False
    return True


def coincide(self, a, b):
    if a.mins == b.mins and a.maxs == b.maxs:
        return True
    return False


class SimpleBox(object):
    def __init__(self, mins, maxs):
        self.mins = mins
        self.maxs = maxs


def intersect(query, box):
    return


class Isomer(object):
    def __init__(self, queries, table_mins, table_maxs, num_tuples):
        self.root = Bucket(table_mins, table_maxs, num_tuples)
        for query in queries:
            if self.contains(queries):
                continue
            self.feed_a_query(query)

    def find_father(self, query, box):
        if cover(box, query):  # 下降桶树
            for child in box.children:
                ret = self.find_father(child)
                if ret:
                    return box
        elif intersect():
            return True
        else:
            return False

    def rebuild(self, query, box):
        return

    def feed_a_query(self, query, box):
        father = self.find_father(query, box)  # 从father处开始建立新的Bucket
        q_box = Bucket(query.mins, query.maxs, 0)
        father.children.append(q_box)
        q_box.volume = cacl_volumn(query.mins, query.maxs)
        for child in father.children:
            overlap = get_overlap(query, child)
            if overlap:  # 有交集
                qc_box = Bucket(overlap.mins, overlap.maxs, 0)
                q_box.children.append(qc_box)
                self.feed_a_query(qc_box, box)
        self.rebuild(qc_box, box)

        return
    # 输入的查询是否被已经存在的直方图覆盖
    def check_cover(self, query, hist):
        if 
        q_volumn = cacl_volumn(query.mins, query.maxs)
        if hist.volume == q_volumn:
            return True
        c_volumn = 0
        for child in self.root.children:
            overlap = get_overlap(query, hist)
            if overlap:  # 有交集
                if self.cover(overlap, child) == False:
                    return False
                c_volumn += cacl_volumn(overlap.mins, overlap.maxs)
        if c_volumn != q_volumn:
            return False
        return True


class Histogram(object):
    def __init__(self, mins, maxs, queries, num_tuples):
        self.dim = len(mins)*2
        self.hist = RTree(mins, maxs, num_tuples)
        for query in queries:
            qmins = [c[0] for c in q.hyperrange]
            qmaxs = [c[1] for c in q.hyperrange]
            if contains(self.hist, query):
                continue
            hits = self.hist.intersection(qmins+qmaxs)
            q = Box(qmins, qmaxs, q.card)
            for b in hits:
                shrink(b, q, False)

    def generate_hist(self, mins, maxs, queries, freq):
        rtree = RTree(mins, maxs, freq)
        root = Box(mins, maxs, freq)
        for q in queries:
            qmins = [c[0] for c in q.hyperrange]
            qmaxs = [c[1] for c in q.hyperrange]
            hits = rtree.intersection(qmins+qmaxs)
            q = Box(qmins, qmaxs, q.card)
            intersecting_boxes = []
            find_intersections(q, root, intersecting_boxes)
            for b in hits:
                shrink(b, q, t_bq, False)
            for j, b in enumerate(intersecting_boxes):
                t_bq = 0
                shrunk_box, t_bc = shrink(b, q, t_bq, count_while_building)
                if shrunk_box is None:
                    continue

                drill_hole(b, shrunk_box, t_bc, q)
        return root
