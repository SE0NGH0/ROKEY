p=[0.2, 0.2, 0.2, 0.2, 0.2]
world=['green', 'red', 'red', 'green', 'green']
Z = 'red'
pHit = 0.6
pMiss = 0.2

def sense(p, Z):
    #Enter code here
    for i in range(len(p)):
        if world[i] == Z:
            p[i] *= pHit
        else:
            p[i] *= pMiss
    return p

print (sense(p,Z))