T = int(input())

for i in range(T):
    X, Y = map(int, input().split())
    
    floorX = (X - 1) // 10 + 1
    floorY = (Y - 1) // 10 + 1
    
    print(abs(floorX - floorY))
