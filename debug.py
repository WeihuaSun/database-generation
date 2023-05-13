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