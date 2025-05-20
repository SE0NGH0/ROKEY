#Modify the program to find and print the sum of all
#the entries in the list p.

p=[0.2,0.2,0.2,0.2,0.2]
pHit = 0.6
pMiss = 0.2
sum = 0

#Enter code here
for i in range(len(p)):
    if i == 1 or i == 2:
        p[i] *= pHit
    else:
        p[i] *= pMiss
    sum += p[i]

print(p)
print(sum)