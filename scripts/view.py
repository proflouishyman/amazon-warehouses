import re,sys
f,pat,n=sys.argv[1],sys.argv[2],int(sys.argv[3]); idx=int(sys.argv[4]) if len(sys.argv)>4 else -1
s=open(f).read()
ms=[m.start() for m in re.finditer(pat,s)]
print(len(ms),'matches')
st=ms[idx]
t=s[st:st+n]
t=re.sub(r'\s*\|\s*(\|\s*)*',' | ',t); t=re.sub(r'\n+',' ¶ ',t); t=re.sub(r'(\| )+','| ',t)
print(t)
