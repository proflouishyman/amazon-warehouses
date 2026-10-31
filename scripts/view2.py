import re,sys
f,pat,n=sys.argv[1],sys.argv[2],int(sys.argv[3]); need=sys.argv[4]
s=open(f).read()
for m in re.finditer(pat,s):
    seg=s[m.start():m.start()+n]
    if re.search(need,seg):
        t=re.sub(r'\s*\|\s*(\|\s*)*',' | ',seg); t=re.sub(r'\n+',' ¶ ',t); t=re.sub(r'(\| )+','| ',t); print(t); break
else: print('NO MATCH')
