t = int(input().strip())

for i in range(t):
    n, x = map(int, input().split())
    a = list(map(int, input().split()))
    
    c = 0
    button = True
    
    while c<n:
        if a[c] == 0:
            c += 1
        else:
            if button:
                c += x
                button = False
            else:
                print("NO")
                break
                
    else:
        print("YES")
                
       
            
            
