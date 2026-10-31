import sys,re
f,a,b=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
L=open(f).read().split('\n')[a-1:b]
out=[]
for l in L:
    cells=[c.strip() for c in l.split('|') if c.strip() not in ('','$',')','%')]
    if cells: out.append(' ; '.join(cells))
print('\n'.join(out))
