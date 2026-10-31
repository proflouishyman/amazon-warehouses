import re,sys,glob
for f in sorted(glob.glob(sys.argv[1])):
    s=open(f).read()
    ms=[m.start() for m in re.finditer(r'we operated the following\s+facilities',s)]
    print('=====',f)
    if not ms: print('NF'); continue
    t=s[ms[-1]-60:ms[-1]+int(sys.argv[2])]
    t=re.sub(r'\s*\|\s*(\|\s*)*',' | ',t); t=re.sub(r'\n+',' ',t); t=re.sub(r'(\| )+','| ',t)
    print(t)
