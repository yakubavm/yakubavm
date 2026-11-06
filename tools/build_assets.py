#!/usr/bin/env python3
"""Regenerate custom local profile SVGs and the animated terminal GIF.

Install Pillow once: python -m pip install pillow
Run from any directory: python tools/build_assets.py
Does not update assets/metrics.svg (that card is owned by GitHub Actions).
"""
from pathlib import Path
from math import sin, cos, pi
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; A.mkdir(exist_ok=True)
BG='#0d1117'; PANEL='#111823'; PANEL2='#141c29'; STROKE='#283244'; WHITE='#e9f1ff'; MUTED='#94a3b8'; BLUE='#38bdf8'; CYAN='#67e8f9'; PURPLE='#c084fc'; GREEN='#50e3a4'

def wrap(w,h,children,extras=''):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Viktor Yakuba developer profile design">
 <defs><linearGradient id="border" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b267f9"/><stop offset=".56" stop-color="#4576fa"/><stop offset="1" stop-color="#28d7f5"/></linearGradient>
 <linearGradient id="hero" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1b1437"/><stop offset=".45" stop-color="#101b32"/><stop offset="1" stop-color="#071923"/></linearGradient>
 <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#171d2e"/><stop offset="1" stop-color="#101822"/></linearGradient>
 <linearGradient id="thin" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#c084fc"/><stop offset=".55" stop-color="#6478fb"/><stop offset="1" stop-color="#38d9ff"/></linearGradient>
 <radialGradient id="light"><stop stop-color="#9b60ff" stop-opacity=".25"/><stop offset="1" stop-color="#9b60ff" stop-opacity="0"/></radialGradient>
 <clipPath id="clip"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="19"/></clipPath>
 </defs>
 <style>
 .h{{font-family:'Segoe UI',Inter,Arial,sans-serif;fill:{WHITE};font-weight:700}}
 .t{{font-family:'Segoe UI',Inter,Arial,sans-serif;fill:{WHITE}}}
 .m{{font-family:'Segoe UI',Inter,Arial,sans-serif;fill:{MUTED}}}
 .code{{font-family:Consolas,'DejaVu Sans Mono',monospace}}
 @keyframes drift{{0%,100%{{transform:translateX(-9px) translateY(2px)}}50%{{transform:translateX(8px) translateY(-4px)}}}}
 @keyframes pulse{{0%,100%{{opacity:.34}}50%{{opacity:.78}}}}
 @keyframes cursor{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
 .wave{{animation:drift 8s ease-in-out infinite}} .spark{{animation:pulse 3.6s ease-in-out infinite}} .caret{{animation:cursor 1.1s steps(1) infinite}}
 @media (prefers-reduced-motion:reduce){{.wave,.spark,.caret{{animation:none!important}}}}
 </style>
 {extras}
 {children}
 </svg>'''

def r(x,y,w,h,rx=14,fill=PANEL,stroke=STROKE,sw=1):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def t(x,y,s,size=22,cls='t',color=None,weight=None,anchor=None,extra=''):
 attrs=(f' fill="{color}"' if color else '') +(f' font-weight="{weight}"' if weight else '')+(f' text-anchor="{anchor}"' if anchor else '')
 return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}"{attrs} {extra}>{escape(str(s))}</text>'
def line(x1,y1,x2,y2,color=STROKE,opacity=1,sw=1):
 return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-opacity="{opacity}" stroke-width="{sw}"/>'
def label(x,y,s,color=PURPLE):
 return t(x,y,s,18,'code',color,weight='bold',extra='letter-spacing="2"')
def save(name,svg):
 (A/name).write_text(svg,encoding='utf-8')

# HERO
W,H=1160,304
s=[r(1,1,1158,302,19,'url(#hero)','#334065')]
s+=['<g clip-path="url(#clip)">', '<circle cx="955" cy="160" r="380" fill="url(#light)"/>']
# grid
for x in range(575,1190,46): s.append(line(x,0,x,305,'#4c568e',.13))
for y in range(25,305,37): s.append(line(565,y,1160,y,'#4c568e',.12))
s.append('<g class="wave">')
for j in range(14):
 pts=[]
 for x in range(570,1191,21):
  y=157 + (j-6)*11.5 + sin((x-570)/82.0 + j*.31)*24 + sin((x-580)/179)*18
  pts.append((x,y))
 p=' '.join((('M' if i==0 else 'L')+f'{x:.1f},{y:.1f}') for i,(x,y) in enumerate(pts))
 s.append(f'<path d="{p}" fill="none" stroke="{PURPLE if j<6 else CYAN}" stroke-opacity="{.12 + (j/13)*.25:.2f}" stroke-width="1.1"/>')
 for i,(x,y) in enumerate(pts):
  if (i+j)%2==0:
   s.append(f'<circle cx="{x}" cy="{y:.1f}" r="{1.65 if j%3 else 2.1}" fill="{PURPLE if j<6 else CYAN}" opacity="{.34 + .32*(x/1160):.2f}"/>')
s.append('</g></g>')
s += [r(45,45,62,62,16,'#211c3d','#564b88'),t(57,87,'>_',35,'code',PURPLE,'bold')]
s += [label(137,56,'YAKUBAVM  /  PROFILE'), t(137,133,'Viktor Yakuba',58,'h'),t(139,173,'Python developer  /  DevOps  /  Automation',24,'t')]
s += [line(139,196,532,196,'url(#thin)',1,2.2), t(139,232,'Software  ·  Scripts  ·  Tools  ·  Bots',23,'m'),t(139,267,'BUILD  /  AUTOMATE  /  SHIP',17,'code',CYAN)]
s += [t(1102,42,'01 // 06',16,'code',MUTED,anchor='end')]
save('hero.svg',wrap(W,H,''.join(s)))

# IDENTITY: two integrated cards
W,H=1160,323
s=[r(1,1,1158,321,18,BG,'#283244')]
s += [r(16,16,702,291,14,'#111925','#344057'),r(732,16,412,291,14,'#111925','#344057')]
s += [r(34,31,665,35,8,'#1c2636','#344057')]
for i,c in enumerate(['#fb7185','#fbbf24','#4ade80']):s.append(f'<circle cx="{52+i*20}" cy="48" r="5.1" fill="{c}"/>')
s += [t(143,54,'viktor@workstation  ~/identity.py',17,'code',MUTED)]
code=[
 [("01",MUTED),("  developer",PURPLE),(" = {",WHITE)],
 [("02",MUTED),("    'name'",CYAN),(": ",WHITE),("'Viktor Yakuba'",GREEN),( ",",WHITE)],
 [("03",MUTED),("    'role'",CYAN),(": ",WHITE),("'Python / DevOps'",GREEN),( ",",WHITE)],
 [("04",MUTED),("    'work'",CYAN),(": ",WHITE),("'software · tooling · bots'",GREEN),( ",",WHITE)],
 [("05",MUTED),("    'focus'",CYAN),(": ",WHITE),("'reliable automation'",GREEN),( ",",WHITE)],
 [("06",MUTED),("    'base'",CYAN),(": ",WHITE),("'Ukraine'",GREEN),( ",",WHITE)],
 [("07",MUTED),("}",WHITE)],
]
# monospace x spacing with consistent char widths by estimated; SVG tspan spans consistent
for i,fragments in enumerate(code):
 y=99+i*28
 s.append(f'<text x="44" y="{y}" font-size="18" class="code">')
 for txt,col in fragments: s.append(f'<tspan fill="{col}">{escape(txt)}</tspan>')
 s.append('</text>')
s += [label(756,48,'AT A GLANCE')]
items=[('01','Engineering','Backend services and APIs'),('02','Operations','CI/CD, containers, workflows'),('03','Automation','Scripts, bots, integrations'),('04','Approach','Clear design. Reliable delivery.')]
for i,(n,name,desc) in enumerate(items):
 y=77+i*55
 s += [r(756,y,47,42,10,'#231c36','#4b426d'), t(779,y+28,n,19,'code',PURPLE,anchor='middle'), t(819,y+17,name,21,'h'),t(819,y+40,desc,17,'m')]
save('identity.svg',wrap(W,H,''.join(s)))

# TOOLBOX
W,H=1160,274
s=[r(1,1,1158,272,18,BG,'#283244')]
tech=[
 ('PY','Python','#5da7ef'),('FA','FastAPI','#46d5b2'),('DJ','Django / DRF','#80cf8e'),('PG','PostgreSQL','#7da8eb'),('RD','Redis','#f26b7d'),
 ('DK','Docker','#55bafd'),('CI','GitHub Actions','#7d94f6'),('NX','Nginx','#5fd6a6'),('WS','Windows / WSL','#64b9ff'),('PS','PowerShell','#6ba9ed'),
 ('SH','Bash','#d0aafb'),('GT','Git','#f8a372'),('TS','pytest','#88dbaa'),('API','REST APIs','#7ce1ec'),('BOT','Telegram Bots','#7abdf7')]
for i,(code,name,color) in enumerate(tech):
 row=i//5; col=i%5; x=22+col*228; y=22+row*82
 s += [r(x,y,216,69,12,'url(#tile)','#344058'),r(x+12,y+13,44,43,10,'#202b3c','#3b4966'),t(x+34,y+39,code,16,'code',color,'bold',anchor='middle'),t(x+67,y+41,name,20,'t')]
save('toolbox.svg',wrap(W,H,''.join(s)))

# ENVIRONMENT
W,H=1160,222
s=[r(1,1,1158,220,18,BG,'#283244'),r(19,19,705,184,16,'#0e2338','#2e5b7e'),r(738,19,405,184,16,'#151e2c','#344057')]
# ambient circular blue on left
s += ['<circle cx="640" cy="90" r="120" fill="#1477de" opacity=".14"/>','<circle cx="670" cy="163" r="100" fill="#62b8ff" opacity=".07"/>']
for x in (59,86):
 for y in (62,89):s.append(f'<rect x="{x}" y="{y}" width="23" height="23" fill="{BLUE}" opacity=".9"/>')
s += [label(148,53,'PRIMARY PLATFORM',BLUE),t(148,94,'Windows 11 Pro',33,'h'),t(148,130,'Everyday development and deployment tooling',20,'m'),t(148,162,'PowerShell  /  Python  /  Editors  /  Docker',18,'code',CYAN)]
s += [r(755,45,50,50,12,'#263047','#4a6388'),t(780,77,'$>',22,'code',PURPLE,'bold',anchor='middle'), label(820,55,'ON DEMAND'),t(820,91,'WSL / Linux',29,'h'),t(757,135,'Linux workflows when the task calls for them',19,'m'),t(757,166,'Bash  /  CLI  /  Containers',18,'code',CYAN)]
save('environment.svg',wrap(W,H,''.join(s)))

# FOCUS
W,H=1160,211
s=[r(1,1,1158,209,18,BG,'#283244')]
focus=[('01','SOFTWARE','Python applications','Backend services'),('02','AUTOMATION','Workflows & jobs','Routine ops, made simple'),('03','BOTS','Event-driven tools','Telegram / Discord'),('04','SCRIPTING','Practical utilities','CLI & productivity'),('05','DEVOPS','Build & delivery','CI/CD and containers')]
for i,(num,name,desc1,desc2) in enumerate(focus):
 x=19+i*228
 s += [r(x,18,213,173,13,'url(#tile)','#344057'),'<rect x="%s" y="18" width="213" height="3" rx="2" fill="%s"/>'%(x,[PURPLE,CYAN,'#769efb','#a18aff',GREEN][i]),t(x+17,52,num,19,'code',CYAN),t(x+17,88,name,22,'h'),t(x+17,124,desc1,18,'t'),t(x+17,154,desc2,16,'m')]
save('focus.svg',wrap(W,H,''.join(s)))

# Footer
W,H=1160,96
s=[line(5,44,350,44,'url(#thin)',1,2),line(815,44,1155,44,'url(#thin)',1,2),t(581,33,'AUTOMATE THE ROUTINE.',24,'code',PURPLE,anchor='middle'),t(581,65,'BUILD THE USEFUL. MAKE IT RELIABLE.',19,'code',WHITE,anchor='middle')]
save('footer.svg',wrap(W,H,''.join(s)))

# GIF typing status 1160 x 90
def find_mono_font():
    candidates = [
        'C:/Windows/Fonts/consola.ttf',
        'C:/Windows/Fonts/cour.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf',
        '/System/Library/Fonts/Menlo.ttc',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return 'DejaVuSansMono.ttf'

FONT = find_mono_font()
font=ImageFont.truetype(FONT,23); small=ImageFont.truetype(FONT,16)
messages=[
 'building Python software that solves real problems',
 'automating workflows, infrastructure and delivery',
 'shipping scripts, bots and developer tooling',
]
# 3 cycles 36 frames each, 90ms each => ~9.7s
frames=[]
for k,msg in enumerate(messages):
 for f in range(32):
  im=Image.new('RGB',(1160,90),(13,17,23)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((1,1,1158,88),radius=15,fill=(17,24,35),outline=(48,62,81),width=2)
  d.rounded_rectangle((19,19,155,71),radius=10,fill=(32,26,52),outline=(74,56,113),width=1)
  d.text((36,34),'yakubavm',font=small,fill=(192,132,252))
  d.text((174,30),'>',font=font,fill=(103,232,249))
  # 16 frames type; 5 hold; 11 erase
  if f < 19: n=round(len(msg)*f/18)
  elif f < 25: n=len(msg)
  else: n=round(len(msg)*(32-f)/7)
  prefix=msg[:max(0,min(n,len(msg)))]
  d.text((210,31),prefix,font=font,fill=(224,234,250))
  extent=d.textbbox((210,31),prefix,font=font); cx=min(extent[2]+5,1130)
  if f%8<5:d.rectangle((cx,33,cx+12,59),fill=(56,189,248))
  d.text((1110,10),f'{k+1:02d}/03',font=small,fill=(95,112,137),anchor='ra')
  frames.append(im.quantize(colors=96,method=Image.Quantize.FASTOCTREE))
frames[0].save(A/'terminal.gif',save_all=True,append_images=frames[1:],duration=95,loop=0,optimize=True,disposal=2)
print('SVG/GIF assets:',[(p.name,round(p.stat().st_size/1024,1)) for p in A.iterdir()])
