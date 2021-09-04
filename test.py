import random
count =  0

for i in range (1, 100000000):
    n =  random.random()*3
    if(n<=0.5):
        count+=1
print(count/1000000)
    
