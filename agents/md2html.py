import re, html
def inline(s):
    out=[];parts=re.split(r'(`[^`]+`)',s)
    for p in parts:
        if p.startswith('`') and p.endswith('`') and len(p)>1: out.append('<code>'+html.escape(p[1:-1])+'</code>');continue
        p=html.escape(p,quote=False)
        p=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',p)
        p=re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])',r'<em>\1</em>',p)
        p=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2">\1</a>',p)
        out.append(p)
    return ''.join(out)
def convert(md):
    L=md.split('\n');i=0;o=[]
    def cells(r):
        r=r.strip()
        if r.startswith('|'):r=r[1:]
        if r.endswith('|'):r=r[:-1]
        return [c.strip() for c in re.split(r'(?<!\\)\|',r)]
    while i<len(L):
        l=L[i]
        if not l.strip(): i+=1;continue
        if l.startswith('```'):
            j=i+1;buf=[]
            while j<len(L) and not L[j].startswith('```'): buf.append(L[j]);j+=1
            o.append('<pre><code>'+html.escape('\n'.join(buf))+'</code></pre>');i=j+1;continue
        m=re.match(r'(#{1,6})\s+(.*)',l)
        if m: n=len(m.group(1));o.append(f'<h{n}>{inline(m.group(2))}</h{n}>');i+=1;continue
        if re.match(r'^\s*(---|\*\*\*|___)\s*$',l): o.append('<hr>');i+=1;continue
        if l.lstrip().startswith('|') and i+1<len(L) and re.match(r'^\s*\|?\s*:?-{2,}',L[i+1]):
            h=cells(l);i+=2;rows=[]
            while i<len(L) and L[i].lstrip().startswith('|'): rows.append(cells(L[i]));i+=1
            t='<div class="tw"><table><thead><tr>'+''.join(f'<th>{inline(c)}</th>' for c in h)+'</tr></thead><tbody>'
            t+=''.join('<tr>'+''.join(f'<td>{inline(c)}</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table></div>'
            o.append(t);continue
        if l.startswith('>'):
            buf=[]
            while i<len(L) and L[i].startswith('>'): buf.append(L[i][1:].lstrip());i+=1
            o.append('<blockquote>'+convert('\n'.join(buf))+'</blockquote>');continue
        if re.match(r'^\s*([-*+]|\d+[.)])\s+',l):
            # list block: collect lines until blank followed by non-list/non-indented
            buf=[]
            while i<len(L):
                x=L[i]
                if not x.strip():
                    if i+1<len(L) and (re.match(r'^\s*([-*+]|\d+[.)])\s+',L[i+1]) or L[i+1].startswith('  ')): buf.append('');i+=1;continue
                    break
                if not re.match(r'^\s*([-*+]|\d+[.)])\s+',x) and not x.startswith(' ') and buf and not buf[-1]: break
                if re.match(r'^(#{1,6}\s|\|)',x): break
                buf.append(x);i+=1
            o.append(lst(buf));continue
        buf=[l];i+=1
        while i<len(L) and L[i].strip() and not re.match(r'^(#{1,6}\s|\||>|```|\s*([-*+]|\d+[.)])\s+|---\s*$)',L[i]): buf.append(L[i]);i+=1
        o.append('<p>'+'<br>'.join(inline(b.strip()) for b in buf)+'</p>')
    return '\n'.join(o)
def lst(lines):
    lines=[x for x in lines]
    base=min(len(x)-len(x.lstrip()) for x in lines if x.strip())
    items=[];cur=None;ordered=None;start=None
    for x in lines:
        ind=len(x)-len(x.lstrip())
        m=re.match(r'^\s*([-*+]|(\d+)[.)])\s+(.*)',x)
        if m and ind<=base+1:
            if ordered is None: ordered=bool(m.group(2));start=m.group(2)
            cur=[m.group(3)];items.append(cur)
        elif cur is not None: cur.append(x[base+2:] if x.strip() else '')
    tag='ol' if ordered else 'ul'
    st=f' start="{start}"' if ordered and start and start!='1' else ''
    out=[f'<{tag}{st}>']
    for it in items:
        first=it[0];rest=it[1:]
        while rest and not rest[-1].strip(): rest.pop()
        inner=inline(first)
        if rest:
            sub='\n'.join(r[2:] if r.startswith('  ') and not re.match(r'^\s*([-*+]|\d+[.)])\s',r) else r for r in rest)
            inner+=convert('\n'.join(rest) if any(re.match(r'^\s*([-*+]|\d+[.)])\s',r) for r in rest) else sub)
        out.append('<li>'+inner+'</li>')
    out.append(f'</{tag}>');return ''.join(out)
