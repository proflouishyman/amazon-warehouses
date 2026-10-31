import sys,re,html,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*')):
    if f.endswith('.txt.out') or f.endswith('_txt'): continue
    s=open(f,errors='ignore').read()
    s=re.sub(r'(?is)<(script|style).*?</\1>','',s)
    s=re.sub(r'(?i)</(tr|p|div|br|li|h\d)>|<br\s*/?>','\n',s)
    s=re.sub(r'(?i)</t[dh]>',' | ',s)
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s).replace('\xa0',' ')
    s=re.sub(r'[ \t]+',' ',s); s=re.sub(r'\n\s*\n+','\n',s)
    os.makedirs(sys.argv[2],exist_ok=True)
    open(os.path.join(sys.argv[2],os.path.basename(f)+'.txt'),'w').write(s)
