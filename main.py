from utils.process import get_plan
import constants
     
if __name__== "__main__":
    #将查询转换为谓词，基数形式
    get_plan(constants.spj,constants.data_root/"plan.pkl")