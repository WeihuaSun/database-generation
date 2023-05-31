a = [1,2,3,4,4,4]
print(a)
for k,i in enumerate(a) :
    if i!=3:
        a.remove(4)
        a.append(3)
    print(k,i)