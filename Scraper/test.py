

for i in range(10):
    x = 5
    try:
        if x == 5:
            raise ValueError
        print(5 + x)
    except:
        continue

print('DONE')