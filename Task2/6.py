t = int(input())
for i in range(t):
    n = int(input())
    a= list(map(int, input().split()))

    freq = {}
    for x in a:
        if x in freq:
            freq[x] += 1
        else:
            freq[x] = 1

    maxfreq = 0
    for v in freq.values():
        if v > maxfreq:
            maxfreq = v

    print(n - maxfreq)
