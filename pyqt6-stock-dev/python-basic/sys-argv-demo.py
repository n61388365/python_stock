import sys

try:
    print('参数个数为:', len(sys.argv), '个参数。')
    print('参数列表:', str(sys.argv))
    print(sys.argv[1])
except Exception as e:
    print(e)
