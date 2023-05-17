""" import re
regex = r"([a-z_]*)\s(<|>|<=|>=|=|!=)\s([0-9]*)"

test = '(production_year > 2010)'
test1 = '(production_year > 2010)'
test2 = '(production_year < 2010)'
test3 = '(production_year < 2010)'

list.remove()
l = []
id1 = []
rm = re.search(regex,test)
col1,op1,val1 = rm.group(1),rm.group(2),rm.group(3)

rm = re.search(regex,test2)
col2,op2,val2 = rm.group(1),rm.group(2),rm.group(3)

id1.append([col1,op1,int(val1)])
id1.append([col2,op2,int(val2)])
id1.sort()
l.append(id1)

id2 = [[col2,op2,int(val2)],[col1,op1,int(val1)]]

print(id2 in l)
print(float('2')) """
print(tuple([1,2,]+[1,2]))