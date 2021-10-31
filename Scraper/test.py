test = {'ere':1, 'aaa':2 }

for key, value in test.items():
    print(key)
    print(value)
    print()


l1 = [1,2,3,4]
l2 = ['a','b','c','d']

zipped = zip(l1,l2)

zipped = zipped[1:]