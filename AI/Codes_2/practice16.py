# 경로를 입력으로 사용하는 함수 Smooth를 정의합니다.
# (weight_data, Weight_smooth에 대한 선택적 매개변수 포함,
# 및 허용 오차) 및 부드러운 경로를 반환합니다. 첫 번째와 
# 마지막 포인트는 변경되지 않고 그대로 유지되어야 합니다.
#
# 스무딩은 반복적인 업데이트를 통해 구현되어야 합니다.
# 원하는 정확도 수준까지 newpath의 각 항목
#에 도달했습니다. 업데이트는 다음 지침에 따라 수행되어야 합니다.
# 경사 하강 방정식
# ----------

from copy import deepcopy

def printpaths(path,newpath):
    for old,new in zip(path,newpath):
        print( '['+ ', '.join('%.3f'%x for x in old) + '] -> ['+ ', '.join('%.3f'%x for x in new) +']')

path = [[0, 0],
        [0, 1],
        [0, 2],
        [1, 2],
        [2, 2],
        [3, 2],
        [4, 2],
        [4, 3],
        [4, 4]]

def smooth(path, weight_data = 0.5, weight_smooth = 0.1, tolerance = 0.000001):
    # Make a deep copy of path into newpath
    newpath = deepcopy(path)

    change = tolerance

    while change >= tolerance:
        change = 0
        for i in range(1, len(path) - 1):
            for j in range(len(path[0])):
                d1 = weight_data*(path[i][j] - newpath[i][j])
                d2 = weight_smooth*(newpath[i-1][j] + newpath[i+1][j] - 2*newpath[i][j])
                change += abs(d1 + d2)
                newpath[i][j] += d1 + d2
    
    return newpath

printpaths(path,smooth(path))