import sys,re,glob
pat=re.compile(sys.argv[2]); k=int(sys.argv[3]) if len(sys.argv)>3 else 12
for f in sorted(glob.glob(sys.argv[1])):
    L=open(f).read().split('\n'); n=0
    print('##',f[:40])
    for i,l in enumerate(L):
        if pat.search(l):
            cells=[]
            for j in range(i,min(i+14,len(L))):
                cells+= [c.strip() for c in L[j].split('|') if c.strip() not in ('','$',')','%')]
            print('  L%d: %s'%(i+1,' ; '.join(cells)[:230])); n+=1
            if n>=int(sys.argv[4] if len(sys.argv)>4 else 3): break
