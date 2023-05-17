from rtree import index

class MyIndex():
    def __init__(self,idx):
        self.id = idx

class Rtree():
    def __init__(self):
        self.p = index.Property()
        self.p.dimension = 4   # 设置 使用的 维度数 (对于地图)
        self.p.dat_extension = 'data'  # 设置存储的后缀名
        self.p.idx_extension = 'index' # 设置存储的后缀名
        ## interleaved=False时，bbox must be [xmin, xmax, ymin, ymax，…,……、kmin kmax]
        self.rtree = index.Index('case',interleaved=False,property=self.p,overwrite=False)
        self.rtree.insert(1, (0, 0, 1,1),obj=MyIndex(1))
        self.rtree.insert(2, (0, 0, 4,4),obj=MyIndex(2))
        self.rtree.insert(3, (0, 0, 5,5),obj=MyIndex(3))
        self.rtree.insert(4, (0, 0, 6,6),obj=MyIndex(4))
        self.rtree.insert(5, (0, 0, 7,7),obj=MyIndex(5))
        
	# objects == True 时,返回包括obj在内的数据，否则只返回目标 id
    def get_nearby_obj(self,width,num):
        res=list(self.rtree.nearest(width,num,objects=True))
        return res

def main():
    ass=Rtree()
    print(ass.rtree.leaves())

    
    
main()
