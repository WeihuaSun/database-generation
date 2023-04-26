#处理查询
#运行查询，解析查询执行计划树，将查询执行计划转换为元组[predicate,limit]

import psycopg2
import pickle

db_url = "postgres://postgres:1@localhost:5432/imdb19"


class PostgreSQL:
    def __init__(self, database_url):
        self.conn = psycopg2.connect(database_url)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
    
    def run(self, sql):
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        return rows
    
    def explain(self, sql):
        sql = "explain (analyse,format json)  " + sql
        result = self.run(sql)[0][0]
        return result
    
    def estimate(self,sql):
        sql = "explain (format json) " + sql
        result = self.run(sql)[0][0]
        return result


def get_plan(queries_path,plan_path):
    step = 0
    with open(queries_path) as f:
        workload = f.readlines()
    plans = []
    queries = []
    db = PostgreSQL(db_url)
    for query in workload:
        estimate = db.estimate(query)
        if estimate[0]['Plan']['Total Cost'] < 1e6:
            print(step,query)
            plan =  db.explain(query)
            plans.append(plan)
            queries.append(query)
            step+=1
    with open(plan_path,"wb") as f:
        pickle.dump((queries,plans),f)
    return 
    
def parse_plan(plans):
    for plan in plans:
        traverse_plan(plan)
        pass
#Node type {'Gather Merge', 'Bitmap Heap Scan', 'Materialize', 'Merge Join', 'Seq Scan', 'Nested Loop', 'Bitmap Index Scan', 'Hash Join', 'Index Scan', 'Gather', 'Sort', 'Hash'}
#Root node type {'Nested Loop', 'Gather', 'Merge Join', 'Index Scan', 'Hash Join', 'Seq Scan', 'Bitmap Heap Scan'}
# TODO root #Root node type {'Nested Loop', 'Gather', 'Merge Join', 'Hash Join' } 
# Join 
def traverse_plan(plan):
    
    print(plan[0]['Plan']['Node Type'])

    
if __name__ == "__main__":
    pass
   
    