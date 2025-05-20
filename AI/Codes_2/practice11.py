def sense(p, measurement, colors, sensor_right):
    a=[]
    for i in range(len(p)):
        q = []
        for j in range(len(p[0])):
            hit = (measurement == colors[i][j])
            q.append(p[i][j] * (hit * sensor_right + (1-hit) * (1-sensor_right)))
        a.append(q)
    si = sum(sum(a, []))
    for i in range(len(a)): # Normalizing the distribution
        for j in range(len(a[0])):
            a[i][j] = a[i][j] / si
    return a

def move(p, motion, p_move):
    dy = motion[0]
    dx = motion[1]
    b = [[0.0 for row in range(len(p[0]))] for col in range(len(p))]
    for i in range(len(p)):
        for j in range(len(p[0])):
            s = p_move * (p[(i-dy) % len(p)][(j-dx) % len(p[i])]) # Movement takes place
            s += (1 - p_move) * p[i][j] # Movement doesn't take place
            b[i][j] = s
    return b

def localize(colors,measurements,motions,sensor_right,p_move):
    # initializes p to a uniform distribution over a grid of the same dimensions as colors
    pinit = 1.0 / float(len(colors)) / float(len(colors[0]))
    p = [[pinit for row in range(len(colors[0]))] for col in range(len(colors))]
    # >>> Insert your code here <<<

    # def sense(p, Z):
    for k in range(len(measurements)):
        p = move(p, motions[k], p_move)
        p = sense(p, measurements[k], colors, sensor_right)

    return p

def show(p):
    rows = ['[' + ','.join(map(lambda x: '{0:.5f}'.format(x),r)) + ']' for r in p]
    print ('[' + ',\n '.join(rows) + ']')

# test 1
colors = [['G', 'G', 'G'],
        ['G', 'R', 'G'],
        ['G', 'G', 'G']]
measurements = ['R']
motions = [[0,0]]
sensor_right= 1.0
p_move= 1.0
p = localize(colors,measurements,motions,sensor_right,p_move)
print("test1")
show(p)
print("\n")

# test 2
colors = [['G', 'G', 'G'],
        ['G', 'R', 'R'],
        ['G', 'G', 'G']]
measurements = ['R']
motions = [[0,0]]
sensor_right= 1.0
p_move= 1.0
p = localize(colors,measurements,motions,sensor_right,p_move)
print("test2")
show(p)
print("\n")

# test 3
colors = [['G', 'G', 'G'],
        ['G', 'R', 'R'],
        ['G', 'G', 'G']]
measurements = ['R']
motions = [[0,0]]
sensor_right= 0.8
p_move= 1.0
p = localize(colors,measurements,motions,sensor_right,p_move)
print("test3")
show(p)
print("\n")

# test 4
colors = [['G', 'G', 'G'],
        ['G', 'R', 'R'],
        ['G', 'G', 'G']]
measurements = ['R', 'R']
motions = [[0,0], [0,1]]
sensor_right= 0.8
p_move= 1.0
p = localize(colors,measurements,motions,sensor_right,p_move)
print("test4")
show(p)
print("\n")

# test 5
colors = [['G', 'G', 'G'],
        ['G', 'R', 'R'],
        ['G', 'G', 'G']]
measurements = ['R', 'R']
motions = [[0,0], [0,1]]
sensor_right= 1.0
p_move= 1.0
p = localize(colors,measurements,motions,sensor_right,p_move)
print("test5")
show(p)
print("\n")

# test 6
colors = [['G', 'G', 'G'],
        ['G', 'R', 'R'],
        ['G', 'G', 'G']]
measurements = ['R', 'R']
motions = [[0,0], [0,1]]
sensor_right= 0.8
p_move= 0.5
p = localize(colors,measurements,motions,sensor_right,p_move)
print("test6")
show(p)
print("\n")

# test 7
colors = [['G', 'G', 'G'],
        ['G', 'R', 'R'],
        ['G', 'G', 'G']]
measurements = ['R', 'R']
motions = [[0,0], [0,1]]
sensor_right= 1.0
p_move= 0.5
p = localize(colors,measurements,motions,sensor_right,p_move)
print("test7")
show(p)
print("\n")

colors = [['R','G','G','R','R'],
        ['R','R','G','R','R'],
        ['R','R','G','G','R'],
        ['R','R','R','R','R']]
measurements = ['G','G','G','G','G']
motions = [[0,0],[0,1],[1,0],[1,0],[0,1]]
p = localize(colors,measurements,motions,sensor_right= 0.7, p_move= 0.8)
print("test8")
show(p)