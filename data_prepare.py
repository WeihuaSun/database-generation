# 处理查询
# 运行查询，解析查询执行计划树，将查询执行计划转换为元组[predicate,limit]

import os
import psycopg2
import csv
import pandas as pd
import json
db_url = "postgres://postgres:1@localhost:5432/imdb19"
ban_parallel = "set max_parallel_workers_per_gather = 0;"


class PostgreSQL:
    def __init__(self, database_url):
        self.conn = psycopg2.connect(database_url)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def run(self, sql):
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        return rows

    def explain(self, sql, parallel=False):
        if not parallel:
            self.cur.execute(ban_parallel)
        sql = "explain (analyse,format json)  " + sql
        result = self.run(sql)[0][0]
        return result


def get_plan(plan_file, query_file=None):
    if os.path.exists(plan_file):
        return pd.read_csv(plan_file)
    db = PostgreSQL(db_url)

    assert query_file is not None
    with open(query_file, "r") as f:
        queries = f.readlines()

    with open(plan_file, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "json", "sql"])
        num_query = len(queries)
        for i, query in enumerate(queries):
            plan = db.explain(query)
            writer.writerow([i, json.dumps(plan[0]), str(query[:-1])])
            print(f"Parse Plan: Step[{i} / {num_query}]")
    return pd.read_csv(plan_file)
import constants
def valid_filter(filter):
    db = PostgreSQL(db_url)
    # for t,fs in filter.items():
    t= 'cast_info'
    fs = filter[t]
    num_filter = len(fs)
    for i,f in enumerate(fs):
        print(f"Table {t} Check Step :[{i}/{num_filter}]")
        cond = []
        for i,a in enumerate(constants.imdb_schema[t]):
            cond.append(f"{a}>{f.mins[i]} AND {a}<={f.maxs[i]}")
        #sql = f"SELECT COUNT(*) FROM {t} WHERE {' AND '.join([' '.join([str(cc) for cc in c]) for c in  f.cond])}"
        sql = f"SELECT COUNT(*) FROM {t} WHERE {' AND '.join(cond)}"
        ret = db.run(sql)
        if ret[0][0] !=f.card:
            print("Error")
            print(sql)
            print("R:",ret[0][0])
            print("F:",f.card)
        

""" if __name__ == "__main__":
    query_file = "data/workload/synthetic.sql"
    plan_file = "data/plan/synthetic_plan.csv"
    df = get_plan(query_file, plan_file)
    nodes = [json.loads(plan)['Plan'] for plan in df['json']] """
