p=[0.2, 0.2, 0.2, 0.2, 0.2]
world=['green', 'red', 'red', 'green', 'green']
measurements = ['red', 'green']
pHit = 0.6
pMiss = 0.2

def sense(p, Z):
    q = []
    sum = 0
    for i in range(len(p)):
        hit = (Z == world[i])
        q.append(p[i] * (hit * pHit + (1-hit) * pMiss))
        sum += q[i]
    for i in range(len(q)):
        q[i] = q[i] / sum
    return q

for measurement in measurements:
    p = sense(p, measurement)

print (p)