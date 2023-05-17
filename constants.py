from pathlib import Path

data_root = Path("/data")
workload_root = Path("/workload")

spj = workload_root / "sql"

imdb_schema = {
    'title': ['kind_id', 'production_year'],
    'movie_info': ["info_type_id"],
    'movie_keyword': ['keyword_id'],
    'movie_info_idx': ['info_type_id'],
    'movie_companies': ['company_id', 'company_type_id'],
    'cast_info': ['role_id', 'person_id'], 
    }

ranges = {
    'title': {'kind_id': (1, 7), 'production_year': (1880, 2019)},
    'movie_info': {"info_type_id": (1, 110)},
    'movie_keyword': {'keyword_id': (1, 134170)},
    'movie_info_idx': {'info_type_id': (99, 113)},
    'movie_companies': {'company_id': (1, 234997), 'company_type_id': (1, 2)},
    'cast_info': {'role_id': (1, 11), 'person_id': (1, 4061926), }
}



t2alias = {'title': 't', 'movie_companies': 'mc', 'cast_info': 'ci',
           'movie_info_idx': 'mi_idx', 'movie_info': 'mi', 'movie_keyword': 'mk'}
