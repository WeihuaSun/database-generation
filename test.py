    plan_path = Path("./data/plan")
    plan_file = plan_path / "synthetic_planc.csv"
    nodetype = set()
    df = pd.read_csv(plan_file)
    nodes = [json.loads(plan)['Plan'] for plan in df['json']]
    sqls = [str(sql) for sql in df['sql']] 
    typenodes = []
    for sql,node in zip(sqls,nodes):
        check_type(node,'Merge Join',typenodes,sql)
    with open("temp.txt","w") as f:
        f.write("\n".join([str(node) for node in typenodes]))
    """ with open(sacle_file,"rb") as f:
        q,nodes = pickle.load(f)  """
    """ typenodes = []
    constraint,hyper_dict = parse_plan(nodes,constants.ranges,constants.imdb_schema) """
    #draw(hyper_dict['title'])
    #generate_tree(hyper_dict['title'],4,2528312)
    #hist = generate_hist([0,0],[1,1],hyper_dict['title'],2528312)
    """ hist = construct(hyper_dict['title'], [0, 0], [1, 1], 1000)
    print(len(hist.children))
    draw_tree(hist,"title")
    lp(hyper_dict['title'],hist) """
    """ for i,c in enumerate(hist.children) :
        print("num",i)
        draw_tree(c,i) """
    
    """ for i, plan in enumerate(nodes):
        # traversePlan(plan)
        #plan = plan[0]['Plan']
        result = traversePlan(plan, constraint)
        if isinstance(result, JoinNode):
            constraint.add_join_tree(result)
        # check_type(plan,'Bitmap Index Scan' ,typenodes,q[i]) #,Seq Scan,Index Scan,'Sort','Hash','Bitmap Index Scan','Bitmap Heap Scan'
        # check_node(plan,nodetype) """
