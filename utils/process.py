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


def get_plan(workload_path,plan_path):
    step = 0
    with open(workload_path) as f:
        workload = f.readlines()
    plans = []
    db = PostgreSQL(db_url)
    for query in workload:
        plan =  db.explain(query)
        plans.append(plan)
        step+=1
        if step%5==0:
            print(step)
    with open(plan_path) as f:
        pickle.dump(plans,f)
    
def parse_plan(plans):
    for plan in plans:
        
        pass
             


    
if __name__ == "__main__":
    pass
   
    