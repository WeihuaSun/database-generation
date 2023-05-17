import matplotlib.pyplot as plt

def draw(rectangle):
    rect = plt.Rectangle((0.1,0.1),0.5,0.3)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i,hyper in enumerate (rectangle):
        xrange = hyper.hyperrange[0]

        yrange = hyper.hyperrange[1]
        site = ((xrange[0],yrange[0]))
        y = yrange[1]-yrange[0]
        x = xrange[1]-xrange[0]
        clos = ['r','g','blue','yellow']
        hatchs = ['/' ,'\\', '|', '-']
        rect = plt.Rectangle(site,x,y,
                             alpha = 0.1,fill=False,lw=1,edgecolor = 'black')#,fc = clos[i%4]hatch=hatchs[i%4]
        ax.add_patch(rect)
    plt.xlim(0,1.1)
    plt.ylim(0,1.1)
    plt.savefig("1.png",dpi = 400)

def draw_tree(hist):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    i=0
    tratree(hist,ax,i=0)
    plt.xlim(0,1.1)
    plt.ylim(0,1.1)
    plt.savefig("2.svg",dpi = 1000,format='svg')
    plt.savefig("2.png",dpi = 200)
    
def tratree(tree,ax,i):
    if i > 5:
        return
    clos = ['r','g','blue','yellow']
    hatchs = ['/' ,'\\', '|', '-']
    site = tuple(tree.mins)
    high = tree.maxs[0]-tree.mins[0]
    width = tree.maxs[1]-tree.mins[1]
    rect = plt.Rectangle(site,high,width,
                             alpha = 0.1,fill=True,lw=1,edgecolor = 'black',fc = clos[i%4])
    
    ax.add_patch(rect)
    for child in tree.children:
        i=i+1
        tratree(child,ax,i)
    


def check_node(plan, nodetype):
    head = plan['Node Type']
    
    if head == 'Hash':
        print(plan)
    nodetype.add(head)
    try:
        for child in plan['Plans']:
            check_node(child, nodetype)
    except:
        pass
    

def check_type(plan, type, nodes,query=None):
    head = plan['Node Type']
    para = plan['Parallel Aware']
    loops = plan ['Actual Loops']
    #if  para and loops!=1:
    
    if head == type and loops!=1:
        #if plan['Index Cond'][-2].isnumeric():
            print(str(plan))
            if query is not None:
                print(query)
            nodes.append(plan)
    try:
        for child in plan['Plans']:
            check_type(child, type, nodes,query)
    except:
        pass




