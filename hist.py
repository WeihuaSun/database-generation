# 输入[l,r]^n
# 输出 hist - tree
from rtree import index


class Bucket(object):
    def __init__(self, freq):
        self.freq = freq



class RTree(object):
    def __init__(self, dim, n):
        self.p = index.Property()
        self.p.dimension = dim   # 设置 使用的 维度数
        self.rtree = index.Index(
            'hist', interleaved=False, property=self.p, overwrite=True)
        init = []
        for _ in range(int(dim/2)):
            init+=[0,1]
        self.rtree.insert(0,tuple(init), obj=Bucket(n))

    def insert(self, coordinates, freq):
        # interleaved=False时，bbox must be [xmin, xmax, ymin, ymax，…,……、kmin kmax]
        self.rtree.insert(self.rtree.get_size(), coordinates, obj=Bucket(freq))

    def delete(self, id, coordinates):
        self.rtree.delete(id, coordinates)
        
    def intersection(self,coordinates):
        return self.rtree.intersection(coordinates,objects=True)
    def count(self,coordinates):
        return self.rtree.count(coordinates)


def overleap(ranges, hist):
    """输入一个超多边形，在现有的直方图中寻找与这个多边形相交的多边形

    Args:
        ranges (_type_): _description_
        hist (_type_): _description_
    """
    return


class STHoles(object):
    def __init__(self) -> None:
        hist_Tree = RTree()

    def insert(coordinates, card):
        # 输入一个查询的超立方体，将其插入到Rtree中，然后更新桶
        return


def generate_hist(hyper_dict):
    return



def generate_tree(rectangle,dim,n):
    rtree = RTree(dim,n)
    for hyper in rectangle:
        coordinates = []
        for item in hyper.hyperrange:
            coordinates.append(item[0])
            coordinates.append(item[1])
        rtree.insert(coordinates,hyper.card)
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

if __name__ == "__main__":
    rtree = RTree()
