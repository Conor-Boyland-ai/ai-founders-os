"""Simple 'real thing' visuals for step slides. Not meant to be read; just a quiet,
authoritative image that changes each step. Muted grays + one green accent. No motion."""
G="#12A150"; L="#E6E2D8"; M="#CFCAC0"; INK="#2A2B2F"
def bar(w, c=L, h=1.1, mt=1.1): return f'<div style="height:{h}vh;width:{w}%;background:{c};border-radius:1vh;margin-top:{mt}vh"></div>'
def card(inner, w=34, h=None):
    hh=f"height:{h}vh;" if h else ""
    return f'<div class="cd" style="width:{w}vw;{hh}">{inner}</div>'
def email(subject, sender=""):
    return card(f'''<div style="display:flex;gap:1vw;align-items:center"><div style="width:4.2vh;height:4.2vh;border-radius:50%;background:{G}"></div>
<div style="flex:1;text-align:left"><div style="font-weight:700;font-size:1.25vw;color:{INK}">{sender}</div><div style="font-size:1.05vw;color:#8a8d94">to me</div></div></div>
<div style="text-align:left;font-weight:700;font-size:1.45vw;color:{INK};margin-top:2.2vh">{subject}</div>{bar(95)}{bar(88)}{bar(92)}{bar(60)}''')
def emails(subjects): return '<div style="display:flex;flex-direction:column;gap:1.2vh">'+"".join(
    card(f'<div style="display:flex;gap:1vw;align-items:center"><div style="width:3vh;height:3vh;border-radius:50%;background:{G}"></div><div style="font-weight:700;font-size:1.2vw;color:{INK};text-align:left">{s}</div></div>',w=34) for s in subjects)+'</div>'
def spike():
    hs=[10,14,12,16,13,20,92,70,30]
    bars="".join(f'<div style="flex:1;height:{h}%;background:{G if h>60 else M};border-radius:.6vh .6vh 0 0"></div>' for h in hs)
    return card(f'<div style="text-align:left;font-size:1.1vw;color:#8a8d94;font-weight:600">Gross volume</div><div style="display:flex;gap:.8vw;align-items:flex-end;height:22vh;margin-top:2vh">{bars}</div>',w=34)
def page(hi):
    """Sales-page wireframe; highlight section index hi (0-based of 13 rows)."""
    rows=[]
    for i in range(13):
        c=G if i==hi else L; h=1.3 if i==hi else 1.0
        w=[55,90,70,85,80,75,88,65,82,60,78,70,86][i]
        rows.append(f'<div style="height:{h}vh;width:{w}%;background:{c};border-radius:1vh;margin:0 auto {1.15}vh auto"></div>')
    return card(f'<div style="height:1.8vh;width:40%;background:{INK};border-radius:1vh;margin:0 auto 2vh auto;opacity:.85"></div>'+"".join(rows),w=26)
def funnel(hi, labels=4):
    out=""
    for i in range(labels):
        w=96-i*16; c=G if i==hi else L
        out+=f'<div style="height:5.2vh;width:{w}%;background:{c};margin:0 auto 1.1vh auto;border-radius:.8vh"></div>'
    return card(out,w=30)
def profile():
    return card(f'''<div style="display:flex;gap:1.4vw;align-items:center"><div style="width:9vh;height:9vh;border-radius:50%;background:{M}"></div>
<div style="flex:1">{bar(60,INK,1.6,0)}{bar(40)}</div></div><div style="display:flex;gap:.8vw;margin-top:2.4vh">
<span class="tg" style="background:{G};color:#fff">trying</span><span class="tg">failing</span><span class="tg">frustrated</span></div>''')
def bubbles():
    b=lambda w,me: f'<div style="display:flex;justify-content:{"flex-end" if me else "flex-start"};margin-top:1.4vh"><div style="background:{G if me else L};border-radius:2vh;padding:1.6vh 1.4vw;width:{w}%">{bar(90,"#ffffff" if me else M,1,0)}{bar(60,"#ffffff" if me else M,1,1)}</div></div>'
    return card(b(70,False)+b(55,True)+b(65,False))
def doc(hi=None, title_w=55, lines=(90,80,95,70,85,60)):
    rows="".join(bar(w, G if hi==i else L, 1.2 if hi==i else 1.0, 1.3) for i,w in enumerate(lines))
    return card(f'<div style="text-align:left"><div style="font-size:3vh">📄</div>{bar(title_w,INK,1.8,1)}{rows}</div>')
def product():
    return card(f'''<div style="display:flex;gap:1.6vw;align-items:center"><div style="width:9vw;height:14vh;border-radius:1vh;background:{INK};opacity:.88"></div>
<div style="flex:1;text-align:left">{bar(80,INK,1.6,0)}{bar(65)}{bar(55)}<div style="margin-top:2vh;background:{G};color:#fff;font-weight:700;font-size:1.2vw;border-radius:1vh;padding:1.2vh 0;width:60%;text-align:center">Get Instant Access</div></div></div>''')
def chart():
    hs=[18,26,30,42,50,63,78,92]
    bars="".join(f'<div style="flex:1;height:{h}%;background:{G if i>=5 else M};border-radius:.6vh .6vh 0 0"></div>' for i,h in enumerate(hs))
    return card(f'<div style="display:flex;gap:.8vw;align-items:flex-end;height:24vh">{bars}</div>')
def wave():
    hs=[30,60,45,85,50,70,35,90,55,40,75,50,65,30,80,45,60,35]
    b="".join(f'<div style="flex:1;height:{h}%;background:{G if 6<=i<=11 else M};border-radius:1vh"></div>' for i,h in enumerate(hs))
    return card(f'<div style="display:flex;gap:.5vw;align-items:center;height:16vh">{b}</div>')
def skill():
    return card(f'''<div style="text-align:left;font-family:ui-monospace,Menlo,monospace;font-size:1.15vw;color:#8a8d94">SKILL.md</div>
{bar(50,INK,1.5,1.6)}{bar(85)}{bar(78)}{bar(90)}<div style="height:1.5vh"></div>{bar(40,G,1.2,0)}{bar(80)}{bar(70)}''')
def checklist():
    row=lambda done,w: f'<div style="display:flex;gap:1vw;align-items:center;margin-top:1.6vh"><div style="width:2.6vh;height:2.6vh;border-radius:.6vh;background:{G if done else "#fff"};border:.25vh solid {G if done else M};color:#fff;font-size:1.8vh;line-height:2.4vh;text-align:center">{"✓" if done else ""}</div><div style="flex:1">{bar(w,L,1.1,0)}</div></div>'
    return card(row(1,80)+row(1,65)+row(1,90)+row(1,70)+row(0,55))
def target():
    rings="".join(f'<div style="position:absolute;inset:{i*3.2}vh;border-radius:50%;border:.5vh solid {G if i==3 else M}"></div>' for i in range(4))
    return card(f'<div style="position:relative;width:24vh;height:24vh;margin:0 auto">{rings}<div style="position:absolute;inset:11vh;border-radius:50%;background:{G}"></div></div>',w=22)
def phone(kind):
    inner={"hook":f'<div style="position:absolute;top:12%;left:10%;right:10%;background:#fff;border-radius:.6vh;padding:.8vh">{bar(90,INK,1.1,0)}{bar(60,INK,1.1,.7)}</div>',
           "visual":f'<div style="position:absolute;top:40%;left:12%;right:12%;height:24%;background:#fff;border-radius:.8vh;border:.4vh solid {G}"></div>',
           "fast":f'<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:6vh;font-weight:800">»</div>',
           "end":f'<div style="position:absolute;top:6%;right:8%;width:5vh;height:5vh;border-radius:50%;border:.5vh solid #fff;border-left-color:transparent"></div><div style="position:absolute;bottom:6%;left:8%;right:8%;height:.7vh;background:rgba(255,255,255,.35);border-radius:1vh"><div style="width:68%;height:100%;background:{G};border-radius:1vh"></div></div>'}[kind]
    return f'<div style="position:relative;width:15vw;height:46vh;border-radius:3vh;background:#3a3c42;border:.8vh solid {INK};overflow:hidden;margin:0 auto">{inner}</div>'
def retention():
    """Watch-time curve: a typical reel drops off fast (gray), a retention reel holds high (green)."""
    W_,H_=520,220
    def path(pts): return "M"+" L".join(f"{x*W_:.0f},{H_-y*H_:.0f}" for x,y in pts)
    drop=[(0,.95),(.08,.55),(.2,.32),(.4,.2),(.7,.12),(1,.08)]
    hold=[(0,.95),(.08,.88),(.25,.84),(.5,.8),(.75,.77),(1,.74)]
    svg=(f'<svg viewBox="-10 -10 {W_+20} {H_+20}" width="100%" style="display:block">'
         f'<line x1="0" y1="{H_}" x2="{W_}" y2="{H_}" stroke="{M}" stroke-width="3"/>'
         f'<path d="{path(drop)}" fill="none" stroke="{M}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="{path(hold)}" fill="none" stroke="{G}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    return card(f'<div style="text-align:left;font-size:1.1vw;color:#8a8d94;font-weight:600;margin-bottom:1.5vh">Watch time</div>{svg}',w=40)
