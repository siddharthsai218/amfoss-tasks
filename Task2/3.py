T=int(input())
for i in range(T):
    N, X, Y = map(int, input().split())
    t=(N+1)*Y
    if t>=X:
        print("YES")
    else:
        print("NO")