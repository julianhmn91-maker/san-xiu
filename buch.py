#!/usr/bin/env python3
"""SAN XIU – Das Buch | cairosvg rendert SVGs zu PNGs, WeasyPrint rendert HTML"""
import re, os, sys, time, base64
import cairosvg
from weasyprint import HTML
from pypdf import PdfWriter, PdfReader

OUT = 'San_Xiu_Das_Buch.pdf'
SK="#C8935A"; SD="#9A7040"; INK="#1a1208"; RED="#8B1A0E"; GOLD="#B8961A"
#!/usr/bin/env python3
"""SAN XIU – Das Buch | cairosvg vorrendert SVGs als PNG, WeasyPrint rendert nur HTML"""
import re, os, sys, time, base64
import cairosvg
from weasyprint import HTML
from pypdf import PdfWriter, PdfReader

OUT = 'San_Xiu_Das_Buch.pdf'
SK="#C8935A"; SD="#9A7040"; INK="#1a1208"; RED="#8B1A0E"; GOLD="#B8961A"

def _svg(w,h,body):
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'

def _head(cx,cy,r):
    ex=r*2//5; ey=cy-r//8; exl=cx-ex; exr=cx+ex; ew=r*2//5; eh=r//5
    return f"""
<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{int(r*1.1)}" fill="{SK}" stroke="{INK}" stroke-width="2"/>
<path d="M{cx-r*5//9},{cy-r*7//10} Q{cx},{cy-r} {cx+r*5//9},{cy-r*7//10}" fill="{SD}" stroke="none" opacity="0.2"/>
<path d="M{cx-r},{cy} Q{cx-r-5},{cy+6} {cx-r-2},{cy+13} Q{cx-r+2},{cy+16} {cx-r+5},{cy+14}" fill="{SK}" stroke="{INK}" stroke-width="1.4"/>
<path d="M{cx+r},{cy} Q{cx+r+5},{cy+6} {cx+r+2},{cy+13} Q{cx+r-2},{cy+16} {cx+r-5},{cy+14}" fill="{SK}" stroke="{INK}" stroke-width="1.4"/>
<path d="M{exl-ew//2},{ey-2} Q{exl},{ey-eh-2} {exl+ew//2},{ey-2}" fill="none" stroke="{INK}" stroke-width="1.7" opacity="0.85"/>
<path d="M{exr-ew//2},{ey-2} Q{exr},{ey-eh-2} {exr+ew//2},{ey-2}" fill="none" stroke="{INK}" stroke-width="1.7" opacity="0.85"/>
<ellipse cx="{exl}" cy="{ey}" rx="{ew//2}" ry="{max(1,eh//2)}" fill="{INK}" opacity="0.9"/>
<ellipse cx="{exr}" cy="{ey}" rx="{ew//2}" ry="{max(1,eh//2)}" fill="{INK}" opacity="0.9"/>
<path d="M{cx-r//5},{cy+r//3} Q{cx},{cy+r//2} {cx+r//5},{cy+r//3}" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0.7"/>
<circle cx="{cx}" cy="{cy-r-r//3}" r="2" fill="{RED}"/>"""

def _robe(cx,top,h,w):
    w2=w//2; wb=int(w*.54); x1=cx-w2; x2=cx+w2; xb1=cx-wb; xb2=cx+wb; yb=top+h
    fm=top+h//3; fo=top+h//2
    return f"""<path d="M{x1},{top} C{x1},{fm} {xb1},{fo} {xb1},{yb} L{xb2},{yb} C{xb2},{fo} {x2},{fm} {x2},{top} Z"
  fill="#2a1a0a" fill-opacity="0.12" stroke="{INK}" stroke-width="2.2"/>
<path d="M{cx-w2//3},{top+h//5} Q{cx-w2//3},{fo} {cx-w2//3},{yb}" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.28"/>
<path d="M{cx},{top+10} Q{cx},{fo} {cx},{yb-4}" fill="none" stroke="{INK}" stroke-width="0.65" opacity="0.18"/>
<path d="M{cx+w2//3},{top+h//5} Q{cx+w2//3},{fo} {cx+w2//3},{yb}" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.28"/>"""

def _arm(x1,y1,x2,y2,x3,y3):
    return f'<path d="M{x1},{y1} Q{x2},{y2} {x3},{y3}" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round" opacity="0.10"/><path d="M{x1},{y1} Q{x2},{y2} {x3},{y3}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>'

def _leg(x1,y1,x2,y2,x3,y3):
    return f'<path d="M{x1},{y1} Q{x2},{y2} {x3},{y3}" fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round" opacity="0.10"/><path d="M{x1},{y1} Q{x2},{y2} {x3},{y3}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>'

def _hand(cx,cy,rx=10,ry=7):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{SK}" stroke="{INK}" stroke-width="1.8"/>'

def _mudra(cx,cy):
    return f'<path d="M{cx-28},{cy} Q{cx},{cy+10} {cx+28},{cy} Q{cx+24},{cy+6} {cx+18},{cy+10} Q{cx},{cy+14} {cx-18},{cy+10} Q{cx-24},{cy+6} {cx-28},{cy} Z" fill="{SK}" stroke="{INK}" stroke-width="1.6"/><ellipse cx="{cx}" cy="{cy-1}" rx="7" ry="3" fill="#d4a870" stroke="{INK}" stroke-width="0.9" opacity="0.82"/>'

def _neck(cx,top,r=8):
    return f'<path d="M{cx-r},{top} Q{cx},{top-6} {cx+r},{top}" fill="{SK}" stroke="{INK}" stroke-width="1.7"/>'

def _ground(cx,cy,w=52):
    return f'<line x1="{cx-w}" y1="{cy}" x2="{cx+w}" y2="{cy}" stroke="{GOLD}" stroke-width="1.5"/>'

def _lbl(x,y,t,anchor="start"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Georgia,serif" font-size="7.5" fill="{RED}">{t}</text>'

def _dot(cx,cy,r=8,n=""):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{RED}"/>{"<text x="+str(cx)+" y="+str(cy+3)+" text-anchor=middle font-size=8 fill=white font-family=Georgia>"+n+"</text>" if n else ""}'


def fig_bodhi():
    b = f"""<circle cx="130" cy="155" r="118" fill="none" stroke="{RED}" stroke-width="1.2" opacity="0.32"/>
<ellipse cx="130" cy="288" rx="82" ry="11" fill="{INK}" opacity="0.06"/>
<path d="M50,275 Q65,248 82,232 Q100,214 118,206 Q130,200 130,200 Q142,206 160,214 Q178,232 195,248 Q210,275 170,286 Q130,286 90,286 Q50,286 50,275 Z" fill="#2a1a0a" fill-opacity="0.12" stroke="{INK}" stroke-width="2.2"/>
<path d="M92,248 Q90,264 88,278" fill="none" stroke="{INK}" stroke-width="0.9" opacity="0.28"/>
<path d="M130,204 Q128,250 128,284" fill="none" stroke="{INK}" stroke-width="0.65" opacity="0.18"/>
<path d="M168,248 Q170,264 172,278" fill="none" stroke="{INK}" stroke-width="0.9" opacity="0.28"/>
<path d="M100,200 Q92,182 94,164 Q100,146 116,138 Q130,132 144,138 Q160,146 166,164 Q168,182 160,200" fill="#2a1a0a" fill-opacity="0.10" stroke="{INK}" stroke-width="2.2"/>"""
    b += _neck(130,132); b += _head(130,102,24); b += _mudra(130,218)
    return _svg(260,306,b)

def fig_zazen():
    b = f"""<ellipse cx="150" cy="266" rx="88" ry="10" fill="{INK}" opacity="0.06"/>
<path d="M56,260 Q70,236 86,218 Q102,200 120,192 Q134,184 150,182 Q166,184 180,192 Q198,200 214,218 Q230,236 244,260" fill="#2a1a0a" fill-opacity="0.12" stroke="{INK}" stroke-width="2.4"/>
<path d="M110,196 Q108,228 106,262" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.28"/>
<path d="M150,186 Q148,230 148,264" fill="none" stroke="{INK}" stroke-width="0.65" opacity="0.18"/>
<path d="M190,196 Q192,228 194,262" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.28"/>
<path d="M104,194 Q96,178 98,162 Q106,146 122,140 Q150,134 178,140 Q194,146 202,162 Q204,178 196,194" fill="#2a1a0a" fill-opacity="0.10" stroke="{INK}" stroke-width="2.2"/>"""
    b += _neck(150,134); b += _head(150,106,24); b += _mudra(150,218)
    b += f'''<circle cx="52" cy="108" r="8" fill="{RED}"/><text x="52" y="112" text-anchor="middle" font-size="8" fill="white" font-family="Georgia">1</text>
<text x="86" y="96" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Baihui</text>
<circle cx="202" cy="110" r="8" fill="{RED}"/><text x="202" y="114" text-anchor="middle" font-size="8" fill="white" font-family="Georgia">2</text>
<text x="212" y="106" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Augen halb</text>
<circle cx="50" cy="168" r="8" fill="{RED}"/><text x="50" y="172" text-anchor="middle" font-size="8" fill="white" font-family="Georgia">3</text>
<text x="5" y="162" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Schultern</text>
<circle cx="112" cy="220" r="8" fill="{RED}"/><text x="112" y="224" text-anchor="middle" font-size="8" fill="white" font-family="Georgia">4</text>
<text x="60" y="222" text-anchor="end" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Mudra</text>
<circle cx="192" cy="190" r="8" fill="{RED}"/><text x="192" y="194" text-anchor="middle" font-size="8" fill="white" font-family="Georgia">5</text>
<text x="224" y="186" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Rücken</text>
<circle cx="150" cy="264" r="8" fill="{RED}"/><text x="150" y="268" text-anchor="middle" font-size="8" fill="white" font-family="Georgia">6</text>
<text x="162" y="278" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Lotus/Sitz</text>'''
    return _svg(300,280,b)

def fig_wuji():
    b = _ground(100,304); b += _robe(100,76,218,94); b += _neck(100,76); b += _head(100,42,22)
    b += f'''<line x1="100" y1="14" x2="100" y2="2" stroke="{RED}" stroke-width="1.5"/>
<path d="M94,7 L100,0 L106,7" fill="none" stroke="{RED}" stroke-width="1.5"/>
<path d="M80,298 Q78,303 76,302" stroke="{INK}" stroke-width="2" fill="none"/>
<path d="M120,298 Q122,303 124,302" stroke="{INK}" stroke-width="2" fill="none"/>
<circle cx="100" cy="210" r="7" fill="none" stroke="{RED}" stroke-width="1" stroke-dasharray="2,2" opacity="0.55"/>
<circle cx="100" cy="210" r="2.5" fill="{RED}" opacity="0.45"/>
<text x="114" y="208" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Dan Tian</text>
<text x="100" y="-4" text-anchor="middle" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Baihui</text>'''
    return _svg(200,310,b)

def fig_baum():
    b = _ground(140,288,58)
    b += f'''<path d="M122,246 Q120,264 118,288 L128,288 Q130,268 132,250" fill="#2a1a0a" fill-opacity="0.10" stroke="{INK}" stroke-width="1.8"/>
<path d="M158,246 Q160,264 162,288 L152,288 Q150,268 148,250" fill="#2a1a0a" fill-opacity="0.10" stroke="{INK}" stroke-width="1.8"/>'''
    b += _robe(140,78,170,96); b += _neck(140,78); b += _head(140,43,22)
    b += _arm(106,128,76,155,72,190); b += _arm(174,128,204,155,208,190)
    b += _hand(128,220); b += _hand(152,220)
    b += f'''<ellipse cx="140" cy="185" rx="40" ry="32" fill="none" stroke="{RED}" stroke-width="1.2" stroke-dasharray="3,3" opacity="0.45"/>
<circle cx="140" cy="185" r="5" fill="{RED}" opacity="0.3"/>
<text x="196" y="190" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Qi-Ball</text>'''
    return _svg(270,295,b)

def fig_mabu():
    b = _ground(155,268,115)
    b += _leg(128,204,104,226,68,268); b += _leg(182,204,208,226,242,268)
    b += f'''<path d="M68,268 L52,270" stroke="{INK}" stroke-width="2.5"/>
<path d="M242,268 L258,270" stroke="{INK}" stroke-width="2.5"/>'''
    b += _robe(155,80,128,100); b += _neck(155,80); b += _head(155,45,23)
    b += _arm(108,145,88,152,74,180); b += _hand(74,182)
    b += _arm(202,145,222,152,236,180); b += _hand(236,182)
    b += f'''<line x1="155" y1="200" x2="155" y2="188" stroke="{RED}" stroke-width="1.3"/>
<path d="M149,194 L155,202 L161,194" fill="none" stroke="{RED}" stroke-width="1.3"/>'''
    return _svg(310,275,b)

def fig_squat():
    b = _ground(130,242,80)
    b += _leg(112,194,90,212,64,242); b += _leg(148,194,170,212,196,242)
    b += _robe(130,56,138,92); b += _neck(130,56); b += _head(130,22,22)
    b += _arm(96,136,106,150,130,160); b += _arm(164,136,154,150,130,160)
    b += _hand(96,136); b += _hand(164,136)
    b += f'''<path d="M96,136 Q113,156 130,160 Q147,156 164,136" fill="none" stroke="{INK}" stroke-width="2.1"/>'''
    return _svg(260,248,b)

def fig_kinhin():
    b = f'''<path d="M118,242 Q106,260 100,284" fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round" opacity="0.10"/>
<path d="M118,242 Q106,260 100,284" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>
<path d="M100,284 L86,286" stroke="{INK}" stroke-width="2.2"/>
<path d="M142,242 Q152,258 156,282" fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round" opacity="0.10"/>
<path d="M142,242 Q152,258 156,282" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>
<path d="M156,282 L170,284" stroke="{INK}" stroke-width="2.2"/>
<line x1="76" y1="290" x2="110" y2="290" stroke="{GOLD}" stroke-width="1.4"/>
<line x1="148" y1="290" x2="180" y2="290" stroke="{GOLD}" stroke-width="1.4"/>'''
    b += _robe(130,76,162,94); b += _neck(130,76); b += _head(130,41,22)
    b += f'''<path d="M108,136 Q118,128 130,126 Q142,128 152,136 Q148,150 130,160 Q112,150 108,136 Z" fill="{SK}" stroke="{INK}" stroke-width="1.7"/>
<text x="56" y="148" text-anchor="end" font-family="Georgia,serif" font-size="7.5" fill="{RED}">Gassho</text>'''
    return _svg(240,305,b)

def fig_wei_tuo():
    b = _ground(110,320,55)
    b += f'''<path d="M92,284 Q90,302 88,320" fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round" opacity="0.10"/>
<path d="M92,284 Q90,302 88,320" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>
<path d="M128,284 Q130,302 132,320" fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round" opacity="0.10"/>
<path d="M128,284 Q130,302 132,320" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>'''
    b += _robe(110,100,184,92)
    b += _arm(76,116,62,70,78,40); b += _arm(144,116,158,70,142,40)
    b += f'''<path d="M78,40 Q94,32 110,30 Q126,32 142,40 Q138,48 110,56 Q82,48 78,40 Z" fill="{SK}" stroke="{INK}" stroke-width="1.8"/>'''
    b += _neck(110,100); b += _head(110,64,22)
    b += f'''<line x1="110" y1="24" x2="110" y2="8" stroke="{RED}" stroke-width="1.6"/>
<path d="M104,14 L110,6 L116,14" fill="none" stroke="{RED}" stroke-width="1.6"/>
<text x="110" y="2" text-anchor="middle" font-family="Georgia,serif" font-size="7.5" fill="{RED}">San Jiao</text>'''
    return _svg(220,330,b)

def fig_bogen():
    b = _ground(155,272,115)
    b += _leg(130,202,104,222,68,272); b += _leg(180,202,206,222,240,272)
    b += _robe(155,78,128,98); b += _neck(155,78); b += _head(149,43,22)
    b += _arm(110,124,80,126,36,136)
    b += f'''<ellipse cx="34" cy="138" rx="9" ry="7" fill="{SK}" stroke="{INK}" stroke-width="1.8"/>
<line x1="34" y1="131" x2="34" y2="116" stroke="{SK}" stroke-width="5"/>
<line x1="34" y1="131" x2="34" y2="116" stroke="{INK}" stroke-width="1.8"/>'''
    b += _arm(200,124,218,116,244,114); b += _hand(218,140)
    b += f'''<path d="M88,110 Q64,128 66,153 Q68,176 92,186" fill="none" stroke="{GOLD}" stroke-width="3"/>
<line x1="88" y1="110" x2="92" y2="186" stroke="{INK}" stroke-width="1" stroke-dasharray="2,2" opacity="0.45"/>
<text x="22" y="120" text-anchor="end" font-family="Georgia,serif" font-size="7.5" fill="{RED}">BaZi</text>'''
    return _svg(310,278,b)

def fig_san_bao():
    return _svg(320,290,f'''<circle cx="160" cy="145" r="128" fill="none" stroke="{RED}" stroke-width="1" opacity="0.25"/>
<polygon points="160,32 278,212 42,212" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.15" stroke-dasharray="4,4"/>
<circle cx="160" cy="38" r="34" fill="#faf8f2" stroke="{RED}" stroke-width="2"/>
<text x="160" y="34" text-anchor="middle" font-size="11" font-family="Georgia,serif" font-style="italic" fill="{INK}">Shen</text>
<text x="160" y="48" text-anchor="middle" font-size="11" font-family="Noto Serif CJK SC,serif" fill="{RED}">神</text>
<circle cx="46" cy="222" r="34" fill="#faf8f2" stroke="{RED}" stroke-width="2"/>
<text x="46" y="218" text-anchor="middle" font-size="11" font-family="Georgia,serif" font-style="italic" fill="{INK}">Jing</text>
<text x="46" y="232" text-anchor="middle" font-size="11" font-family="Noto Serif CJK SC,serif" fill="{RED}">精</text>
<circle cx="274" cy="222" r="34" fill="#faf8f2" stroke="{RED}" stroke-width="2"/>
<text x="274" y="218" text-anchor="middle" font-size="11" font-family="Georgia,serif" font-style="italic" fill="{INK}">Qi</text>
<text x="274" y="232" text-anchor="middle" font-size="11" font-family="Noto Serif CJK SC,serif" fill="{RED}">氣</text>
<circle cx="160" cy="150" r="5" fill="{RED}"/>
<text x="160" y="78" text-anchor="middle" font-size="7.5" font-family="Georgia,serif" fill="{RED}">Geist</text>
<text x="46" y="262" text-anchor="middle" font-size="7.5" font-family="Georgia,serif" fill="{RED}">Essenz</text>
<text x="274" y="262" text-anchor="middle" font-size="7.5" font-family="Georgia,serif" fill="{RED}">Energie</text>''')

def fig_rain():
    def box(x,l,de,l1,l2):
        return f'''<rect x="{x}" y="4" width="80" height="104" rx="7" fill="#faf8f2" stroke="{RED}" stroke-width="1.8"/>
<text x="{x+40}" y="34" text-anchor="middle" font-family="Georgia,serif" font-size="26pt" fill="{RED}" font-weight="bold">{l}</text>
<text x="{x+40}" y="60" text-anchor="middle" font-family="Georgia,serif" font-size="8.5pt" fill="#1a1208">{de}</text>
<text x="{x+40}" y="80" text-anchor="middle" font-family="Georgia,serif" font-size="7pt" fill="#1a1208">{l1}</text>
<text x="{x+40}" y="92" text-anchor="middle" font-family="Georgia,serif" font-size="7pt" fill="#1a1208">{l2}</text>'''
    return _svg(360,116,box(4,"R","Erkennen","In welchem","Zustand?")+box(94,"A","Akzeptieren","Situation","annehmen")+box(184,"I","Untersuchen","Woher kommt","der Zustand?")+box(274,"N","Non-Id.","Ich bin nicht","mein Gedanke"))

def fig_five():
    return _svg(360,120,f'''<g transform="translate(36,15)">
<path d="M0,58 C-6,42 -10,26 0,8 C5,20 10,12 15,58 Z" fill="none" stroke="{RED}" stroke-width="2.4"/>
<text x="8" y="76" text-anchor="middle" font-family="Georgia,serif" font-size="8pt" fill="#1a1208">Begehren</text></g>
<g transform="translate(94,10)">
<path d="M2,38 Q0,20 12,20 Q14,11 22,14 Q30,5 38,14 Q47,12 47,22 Q53,22 53,32 Q53,42 45,42 L9,42 Q1,42 2,38 Z" fill="none" stroke="{RED}" stroke-width="2.4"/>
<path d="M25,42 L21,54 L27,52 L23,66" fill="none" stroke="{RED}" stroke-width="2"/>
<text x="27" y="81" text-anchor="middle" font-family="Georgia,serif" font-size="8pt" fill="#1a1208">Übelwollen</text></g>
<g transform="translate(178,15)">
<rect x="0" y="0" width="46" height="46" rx="5" fill="none" stroke="{RED}" stroke-width="2.4"/>
<path d="M8,16 L38,16 M8,25 L38,25 M8,34 L38,34" stroke="{RED}" stroke-width="2"/>
<path d="M23,46 L23,62 M14,62 L32,62" stroke="{RED}" stroke-width="2.2"/>
<text x="23" y="78" text-anchor="middle" font-family="Georgia,serif" font-size="8pt" fill="#1a1208">Trägheit</text></g>
<g transform="translate(250,10)">
<path d="M25,25 C25,12 37,8 39,18 C41,29 31,35 23,29 C15,23 19,11 29,9" fill="none" stroke="{RED}" stroke-width="2.4"/>
<circle cx="25" cy="42" r="3" fill="{RED}"/>
<text x="25" y="56" text-anchor="middle" font-family="Georgia,serif" font-size="8pt" fill="#1a1208">Unruhe</text></g>
<g transform="translate(305,10)">
<path d="M22,8 Q32,2 34,12 Q36,23 22,28 L22,35" fill="none" stroke="{RED}" stroke-width="2.6"/>
<circle cx="22" cy="42" r="3.5" fill="{RED}"/>
<text x="22" y="57" text-anchor="middle" font-family="Georgia,serif" font-size="8pt" fill="#1a1208">Zweifel</text></g>''')

def fig_atem():
    return _svg(360,180,f'''<ellipse cx="145" cy="90" rx="56" ry="72" fill="none" stroke="#1a1208" stroke-width="1" opacity="0.2"/>
<path d="M145,32 L145,108" fill="none" stroke="{RED}" stroke-width="2.2"/>
<path d="M138,100 L145,110 L152,100" fill="none" stroke="{RED}" stroke-width="2"/>
<ellipse cx="145" cy="124" rx="30" ry="22" fill="none" stroke="{RED}" stroke-width="1.8" stroke-dasharray="3,2" opacity="0.72"/>
<circle cx="145" cy="124" r="6" fill="{RED}" opacity="0.28"/>
<path d="M230,45 Q244,30 258,45 Q272,60 286,45 Q300,30 315,45" fill="none" stroke="{RED}" stroke-width="2.2"/>
<path d="M230,85 Q248,62 266,85 Q284,108 302,85" fill="none" stroke="{RED}" stroke-width="1.6" opacity="0.55"/>
<text x="32" y="48" font-family="Georgia,serif" font-size="8.5pt" fill="{RED}">Einatmen</text>
<text x="32" y="105" font-family="Georgia,serif" font-size="8.5pt" fill="#1a1208">Ausatmen</text>
<text x="145" y="156" text-anchor="middle" font-family="Georgia,serif" font-size="8.5pt" fill="{RED}">Dan Tian</text>
<text x="272" y="28" text-anchor="middle" font-family="Georgia,serif" font-size="8pt" fill="{RED}">Atemwellen</text>''')


def _to_img(svg_str, caption='', scale=2):
    png = cairosvg.svg2png(bytestring=svg_str.encode(), scale=scale)
    b64 = base64.b64encode(png).decode()
    cap = f'<div class="ic">{caption}</div>' if caption else ''
    return f'<div class="ib"><img src="data:image/png;base64,{b64}" style="display:block;margin:0 auto;max-width:100%;"/>{cap}</div>'

def _to_img_inline(svg_str, scale=2):
    png = cairosvg.svg2png(bytestring=svg_str.encode(), scale=scale)
    b64 = base64.b64encode(png).decode()
    return f'<img src="data:image/png;base64,{b64}" style="display:block;"/>'

CSS = """
@page {size:A4;margin:24mm 22mm 28mm 24mm;
  @bottom-center{content:"— " counter(page) " —";font-family:Georgia,serif;font-size:9pt;color:#8B1A0E;}}
@page cover-page{margin:0;@bottom-center{content:none;}}
@page ch-page{margin:0;@bottom-center{content:none;}}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:Georgia,'Times New Roman',serif;font-size:11pt;line-height:1.72;color:#1a1208;
  background:#f5f0e6;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.cov{page:cover-page;background:#0d0b08!important;color:#f5f0e6;width:210mm;height:297mm;
  display:block;text-align:center;padding:28mm 24mm;}
.chd{page:ch-page;background:#0d0b08!important;color:#f5f0e6;width:210mm;height:297mm;
  display:block;text-align:center;padding:36mm 22mm;page-break-before:always;}
.content{page-break-before:always;}
h2.t2{font-size:13.5pt;color:#8B1A0E;margin:7mm 0 2.5mm;border-bottom:1px solid #d4c9a8;padding-bottom:1.5mm;}
h3.t3{font-size:11.5pt;color:#1a1208;margin:4.5mm 0 1.5mm;font-weight:bold;}
p{margin-bottom:3.5mm;text-align:justify;orphans:3;widows:3;}p+p{text-indent:4mm;}
.intro{font-size:11.5pt;line-height:1.82;font-style:italic;color:#3a2a1a;
  border-left:3px solid #8B1A0E;padding-left:5mm;margin:5mm 0 6mm;}
.qb{background:#ede8da;border-left:4px solid #8B1A0E;padding:5mm 6mm;margin:6mm 0;
  font-style:italic;font-size:11pt;color:#2a1a0a;line-height:1.72;}
.au{font-size:9pt;color:#8B1A0E;font-style:normal;text-align:right;margin-top:2mm;}
.ib{text-align:center;margin:5mm 0;}
.ic{font-size:8.5pt;color:#8B1A0E;font-style:italic;text-align:center;margin-top:2mm;}
.cb{background:#ede8da;border:1px solid #c8b98a;padding:4.5mm 6mm;margin:5mm 0;border-radius:3px;}
.ct{font-size:10pt;font-weight:bold;color:#8B1A0E;margin-bottom:1.5mm;}
.row{display:flex;gap:7mm;margin:3.5mm 0;}.col{flex:1;}
.si{margin:3.5mm 0;padding:4mm;background:#faf8f2;border-radius:4px;border:1px solid #d4c9a8;overflow:hidden;}
.sh{font-size:12.5pt;color:#8B1A0E;font-weight:bold;margin-bottom:1mm;}
.sc{font-family:'Noto Serif CJK SC',serif;font-size:18pt;color:#8B1A0E;opacity:.42;float:right;margin-left:4mm;}
.pb{background:#ede8da;border:1.5px solid #8B1A0E;padding:4.5mm 6mm;margin:5mm 0;border-radius:4px;}
.pt{font-size:11pt;font-weight:bold;color:#8B1A0E;margin-bottom:2.5mm;text-align:center;}
.sr{display:flex;align-items:flex-start;margin:2mm 0;}
.sn{display:inline-block;background:#8B1A0E;color:white;width:18px;height:18px;
  border-radius:50%;text-align:center;line-height:18px;font-size:9pt;margin-right:3mm;flex-shrink:0;}
.st{flex:1;font-size:10.5pt;}
.hb{border:1px solid #d4c9a8;border-left:4px solid #8B1A0E;padding:3.5mm 5.5mm;margin:3.5mm 0;background:#faf8f2;}
.ht{font-size:11pt;font-weight:bold;color:#8B1A0E;}
.hp{font-size:9pt;color:#8B1A0E;opacity:.68;font-style:italic;}
.ht2{font-size:12pt;color:#8B1A0E;font-weight:bold;margin:5.5mm 0 2mm;}
.hc{font-family:'Noto Serif CJK SC',serif;font-size:13pt;color:#8B1A0E;opacity:.48;margin-left:3mm;}
.kp{background:#faf8f2;border:1px solid #d4c9a8;padding:3.5mm 5.5mm;margin:2.5mm 0;border-radius:3px;}
.kp p{margin:0;font-size:10.5pt;padding:.8mm 0;}
.kp p::before{content:"— ";color:#8B1A0E;font-weight:bold;}
table.pl{width:100%;border-collapse:collapse;font-size:9pt;margin:3.5mm 0;}
table.pl th{background:#8B1A0E;color:white;padding:2.5mm 3mm;text-align:left;font-size:8.5pt;}
table.pl td{padding:2mm 3mm;border-bottom:.4px solid #d4c9a8;}
table.pl tr:nth-child(even) td{background:#faf8f2;}
table.pl tr.tot td{font-weight:bold;color:#8B1A0E;background:#ede8da;}
.zi{margin:4mm 0;padding:3.5mm 5.5mm;border-left:3px solid #B8961A;}
.zt{font-size:10.5pt;font-style:italic;color:#2a1a0a;line-height:1.72;}
.zs{font-size:8.5pt;color:#8B1A0E;margin-top:1.5mm;text-align:right;}
.gi{margin:2.5mm 0;padding-bottom:2.5mm;border-bottom:.4px dotted #c8b98a;}
.gt{font-weight:bold;color:#8B1A0E;font-size:11pt;}
.gc{font-family:'Noto Serif CJK SC',serif;font-size:12pt;color:#8B1A0E;opacity:.55;margin-left:2mm;}
.gd{font-size:10pt;color:#1a1208;margin-top:.5mm;}
hr.or{border:none;text-align:center;margin:5mm 0;overflow:visible;height:0;}
hr.or::after{content:"❧ ❧ ❧";color:#8B1A0E;font-size:10pt;}
hr.rl{border:none;border-top:.5px solid #d4c9a8;margin:4.5mm 0;}
"""

# ─── HTML SECTIONS ──────────────────────────────────────────────────────────

def W(t): return f'<span style="font-family:\'Noto Serif CJK SC\',serif;color:#8B1A0E;opacity:.5;margin-left:2mm;">{t}</span>'
def H(css): return f'<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><style>{css}</style></head><body>'
E = '</body></html>'

def ch(num, rom, cn, title, sub):
    return f'''<div class="chd">
<div style="font-size:10pt;color:#8B1A0E;letter-spacing:5px;margin-bottom:4mm;">{num}</div>
<div style="font-size:44pt;color:#8B1A0E;font-weight:bold;opacity:.32;margin-bottom:2mm;line-height:1;">{rom}</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:5mm auto;opacity:.42;"></div>
<div style="font-family:'Noto Serif CJK SC',serif;font-size:28pt;color:#8B1A0E;margin-bottom:5mm;opacity:.62;">{cn}</div>
<div style="font-size:21pt;font-weight:bold;margin-bottom:3mm;">{title}</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:5mm auto;opacity:.42;"></div>
<div style="font-size:11pt;color:#c8b98a;font-style:italic;max-width:112mm;margin:0 auto;">{sub}</div>
</div>'''

def sn(n): return f'<span class="sn">{n}</span>'

def cover():
    return f'''<div class="cov">
<div style="color:#8B1A0E;font-size:13pt;letter-spacing:4px;margin-bottom:5mm;">— 三 修 —</div>
<div style="font-family:'Noto Serif CJK SC',serif;font-size:52pt;color:#8B1A0E;margin-bottom:3mm;letter-spacing:8px;">三修</div>
<div style="font-size:24pt;font-weight:bold;letter-spacing:5px;margin-bottom:4mm;text-transform:uppercase;">SAN XIU</div>
<div style="font-size:12.5pt;color:#c8b98a;font-style:italic;margin-bottom:9mm;">Der dreifache Weg: Körper, Atem, Geist</div>
<div style="width:72mm;height:1px;background:#8B1A0E;margin:5mm auto;opacity:.52;"></div>
<div style="margin:6mm 0;">{fig_bodhi()}</div>
<div style="width:72mm;height:1px;background:#8B1A0E;margin:5mm auto;opacity:.52;"></div>
<div style="font-size:9pt;color:#8B1A0E;letter-spacing:2px;opacity:.8;margin-bottom:3mm;">Zhan Zhuang · Chan-Meditation · Shaolin Qigong</div>
<div style="font-size:9pt;color:#8B1A0E;letter-spacing:2px;opacity:.8;margin-bottom:3mm;">Inspiriert von Meister Shi Heng Yi (釋恒義) · 35. Generation Shaolin</div>
<div style="font-size:8pt;color:#8B1A0E;letter-spacing:1px;opacity:.52;margin-top:7mm;">Ein persönliches Trainingsbuch zur täglichen Praxis</div>
</div>'''

def titelblatt():
    return f'''<div style="page-break-before:always;text-align:center;padding:18mm 16mm 0;">
<div style="height:16mm;"></div>
<div style="font-size:30pt;color:#8B1A0E;font-weight:bold;letter-spacing:4px;margin-bottom:2mm;">SAN XIU</div>
<div style="font-family:'Noto Serif CJK SC',serif;font-size:19pt;color:#8B1A0E;opacity:.55;margin-bottom:5mm;">三修</div>
<div style="font-size:13pt;color:#1a1208;font-style:italic;margin-bottom:11mm;">Der dreifache Weg: Körper, Atem, Geist</div>
<div style="width:72mm;height:1.5px;background:#8B1A0E;margin:5mm auto;"></div>
<p style="font-size:9pt;color:#5a4a3a;max-width:106mm;margin:5mm auto;line-height:1.75;text-align:center;">
Ein Trainingsbuch zur täglichen Kultivierung von Körper und Geist,<br>
verwurzelt in der 1500-jährigen Tradition des Shaolin-Klosters<br>
und den zeitlosen Lehren von Bodhidharma (Da Mo).</p>
<div style="width:72mm;height:1.5px;background:#8B1A0E;margin:5mm auto;"></div>
<p style="font-size:8.5pt;color:#8B1A0E;text-align:center;max-width:106mm;margin:5mm auto;">
Inspiriert von Meister Shi Heng Yi (釋恒義),<br>
35. Generation der Shaolin-Meister · Shaolin Temple Europe</p>
<p style="font-size:8pt;color:#8B1A0E;font-style:italic;text-align:center;margin-top:5mm;">
三修: San = Drei · Xiu = Kultivierung · Körper (身) · Atem (息) · Geist (神)</p>
</div>'''

def toc():
    def p(t,n): return f'<div style="font-size:9.5pt;padding:1.5mm 0;border-bottom:.4px dotted #c8b98a;display:flex;justify-content:space-between;"><span>{t}</span><span style="color:#8B1A0E;font-style:italic;">{n}</span></div>'
    def h(t): return f'<div style="font-size:10.5pt;font-weight:bold;color:#8B1A0E;margin:5mm 0 1.5mm;text-transform:uppercase;letter-spacing:1px;">{t}</div>'
    return f'''<div style="page-break-before:always;padding:10mm 0 0;">
<div style="font-size:18pt;color:#8B1A0E;text-align:center;margin-bottom:8mm;letter-spacing:2px;">Inhalt</div>
<hr class="rl">
{h("Einleitung")}
{p("Der Berg und der Aufstieg — Eine Parabel",8)}{p("Über dieses Buch",9)}
{h("Teil I — Philosophische Grundlagen")}
{p("Die drei Schätze: Jing, Qi, Shen",12)}{p("Wu De — Die 14 Tugenden",15)}
{p("Die fünf Hindernisse zur Selbstmeisterschaft",17)}{p("Die RAIN-Methode",21)}
{p("Die fünf Elemente (Wu Xing) und ihre Organe",22)}
{h("Teil II — Chan-Meditation")}
{p("Bodhidharma und die Wurzel des Chan",26)}{p("Die Sitzhaltung — Sieben Punkte",27)}
{p("Schritt-für-Schritt: Deine Meditationspraxis",29)}{p("Der Affen-Geist",30)}
{p("Kinhin — Die Gehmeditation",32)}{p("Metta — Das Mitgefühl kultivieren",33)}
{h("Teil III — Zhan Zhuang")}
{p("Das Prinzip der stehenden Pfahlarbeit",36)}{p("Song — Das Loslassen",37)}
{p("Die fünf Kernhaltungen mit Illustrationen",38)}{p("Nei Gong — Die innere Arbeit",43)}
{p("Was während des Stehens passiert",45)}
{h("Teil IV — Atemtechniken")}
{p("Die drei Säulen des Qi Gong",48)}{p("Sechs Stufen der Atemverfeinerung",49)}
{p("Sieben zentrale Atemübungen",50)}
{h("Teil V — Shaolin Qigong")}
{p("Ba Duan Jin — Die Acht Brokate",55)}{p("Yi Jin Jing — Die 12 Übungen",60)}
{p("Shu Jing Gong — Buddhistische Qigong-Form",64)}
{h("Trainingsplan")}
{p("6-Wochen-Progression · 13 Übungen",67)}{p("Tempel-Tagesrhythmus",69)}
{p("Die sieben Praxis-Prinzipien",70)}
{h("Anhang")}
{p("Ausgewählte Zitate — Shi Heng Yi",72)}{p("Glossar chinesischer Begriffe",75)}
</div>'''

def einleitung():
    return f'''<div class="chd">
<div style="font-size:10pt;color:#8B1A0E;letter-spacing:5px;margin-bottom:4mm;">Einleitung</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:5mm auto;opacity:.42;"></div>
<div style="font-family:'Noto Serif CJK SC',serif;font-size:28pt;color:#8B1A0E;margin-bottom:5mm;opacity:.62;">序言</div>
<div style="font-size:21pt;font-weight:bold;margin-bottom:3mm;">Der Weg des Selbst</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:5mm auto;opacity:.42;"></div>
<div style="font-size:11pt;color:#c8b98a;font-style:italic;max-width:112mm;margin:4mm auto;">„Um deinem Leben Bedeutung zu geben, musst du dich selbst kennenlernen und meistern."<br><em>— Shi Heng Yi</em></div>
</div>
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Der Berg und der Aufstieg</h2>
<p class="intro">Ein Mann lebte am Fuß eines Berges. Jeden Tag betrachtete er den Gipfel. Als er aufbrach, fragte er dreißig Wanderer. Nach all den Berichten entschied er: Da so viele den Berg bereits bestiegen haben, muss ich nicht mehr selbst hinauf. Der Mann begann die Reise nie.</p>
<p>Diese Parabel trifft das Wesen allen Strebens: Kein Buch, kein Lehrer kann dir ersetzen, selbst auf dem Gipfel zu stehen. Worte zeigen den Weg. Gegangen werden muss er von dir.</p>
<p><strong>San Xiu</strong> (三修) — der dreifache Weg — bezeichnet die gleichzeitige Kultivierung von Körper, Atem und Geist. Nicht Körper <em>oder</em> Geist. Nicht Training <em>oder</em> Meditation. Alles, gleichzeitig, täglich.</p>
<h2 class="t2">Über dieses Buch</h2>
<div class="row">
<div class="col"><div class="cb"><div class="ct">Shaolin-Tradition</div>
<p style="font-size:10pt;">1500 Jahre von Bodhidharma bis heute. Ba Duan Jin, Yi Jin Jing, Shu Jing Gong, Chan-Meditation.</p></div></div>
<div class="col"><div class="cb"><div class="ct">Zhan Zhuang</div>
<p style="font-size:10pt;">Stehende Pfahlarbeit aus Yi Quan und Nei Gong — über 27 Jahrhunderte alt.</p></div></div>
</div>
<div class="cb" style="text-align:center;"><div class="ct">Sanchin / Sanshin</div>
<p style="font-size:10pt;">Isometrisches Halten, Atemkontrolle, Yi (Vorstellung) — verbindet alle Elemente täglich.</p></div>
<div class="qb">„Es gibt zwei Fehler auf dem Weg zur Selbstmeisterschaft: Nicht damit anzufangen. Und nicht den ganzen Weg zu gehen."<div class="au">— Shi Heng Yi</div></div>
</div>'''

def teil1():
    return f'''{ch("Teil I","I","哲學","Philosophische Grundlagen","Die Wurzeln verstehen, bevor du die Äste erklimmst.")}
<div class="content">
<div class="ib">{fig_san_bao()}<div class="ic">Die drei Schätze — San Bao 三寶 · Jing nährt Qi · Qi trägt Shen · Shen lenkt Jing</div></div>
<div class="si"><span class="sc">精</span><div class="sh">Jing — Die Essenz</div>
<p style="font-size:10.5pt;margin-bottom:0;">Jing ist die dichteste Lebensenergie, in den Nieren gespeichert. Vorgeburtliches Jing ist endlich; nachgeburtliches Jing wird durch Schlaf, Ernährung und Qigong täglich erneuert. Zhan Zhuang und Yi Jin Jing kultivieren Jing direkt.</p></div>
<div class="si"><span class="sc">氣</span><div class="sh">Qi — Die Lebensenergie</div>
<p style="font-size:10.5pt;margin-bottom:0;">Qi ist Bewegung, Fluss, Lebenskraft — animiert Körper und Geist, fließt durch Meridiane. <em>„Wo deine Aufmerksamkeit hingeht, fließt deine Energie."</em></p></div>
<div class="si"><span class="sc">神</span><div class="sh">Shen — Der Geist</div>
<p style="font-size:10.5pt;margin-bottom:0;">Shen ist Bewusstsein, Präsenz, Klarheit — sichtbar in den Augen. <em>„Wenn der See still ist, siehst du den Grund."</em></p></div>
<div class="cb"><div class="ct">Transformation</div>
<p style="font-size:10pt;"><strong>Jing → Qi</strong> durch Körperpraxis &nbsp;·&nbsp; <strong>Qi → Shen</strong> durch Atem &nbsp;·&nbsp; <strong>Shen → Wuji</strong> durch Meditation</p></div>
<hr class="or">
<h2 class="t2">Wu De — Die 14 Tugenden</h2>
<div class="row"><div class="col"><div class="kp">
<p><strong>Jì Lǜ (紀律)</strong> — Disziplin</p><p><strong>Zì Zhì (自制)</strong> — Selbstkontrolle</p>
<p><strong>Qiān Xū (謙虛)</strong> — Bescheidenheit</p><p><strong>Cí Bēi (慈悲)</strong> — Mitgefühl</p>
<p><strong>Qiān Xùn (謙遜)</strong> — Demut</p><p><strong>Zūn Jìng (尊敬)</strong> — Respekt</p>
<p><strong>Zhèng Yì (正義)</strong> — Rechtschaffenheit</p>
</div></div><div class="col"><div class="kp">
<p><strong>Xìn Yòng (信用)</strong> — Vertrauen</p><p><strong>Zhōng Chéng (忠誠)</strong> — Loyalität</p>
<p><strong>Yì Yuàn (意願)</strong> — Wille</p><p><strong>Rěn Nài (忍耐)</strong> — Beharrlichkeit</p>
<p><strong>Yì Lì (毅力)</strong> — Beständigkeit</p><p><strong>Nài Xīn (耐心)</strong> — Geduld</p>
<p><strong>Yǒng Gǎn (勇敢)</strong> — Mut</p>
</div></div></div>
<hr class="or">
<h2 class="t2">Die fünf Hindernisse zur Selbstmeisterschaft</h2>
<div class="ib">{fig_five()}<div class="ic">Pañca Nīvaraṇa — aus Shi Heng Yis TEDx-Talk (17 Mio. Aufrufe)</div></div>
<div class="hb"><div class="ht">1. Sinnesbegehren <span class="hp">Kamacchanda 欲欲</span></div>
<p style="font-size:10.5pt;margin-top:2mm;">Wenn Angenehmes zur Obsession wird. Frage: Bin ich süchtig — oder wähle ich frei?</p></div>
<div class="hb"><div class="ht">2. Übelwollen <span class="hp">Byapada 瞋恚</span></div>
<p style="font-size:10.5pt;margin-top:2mm;">Ablehnung gegen Situation, Mensch, Umstand. <em>„Dann wird jede Reise Kampf."</em></p></div>
<div class="hb"><div class="ht">3. Trägheit &amp; Mattheit <span class="hp">Thinamiddha 昏沉</span></div>
<p style="font-size:10.5pt;margin-top:2mm;">Schwere des Körpers, Dumpfheit des Geistes. Weg: Inspiration erinnern. Kleinen Schritt machen.</p></div>
<div class="hb"><div class="ht">4. Unruhe <span class="hp">Uddhacca 掉举</span></div>
<p style="font-size:10.5pt;margin-top:2mm;">Der Affengeist springt zwischen Vergangenheit und Zukunft. Weg: Atem als Anker. RAIN anwenden.</p></div>
<div class="hb"><div class="ht">5. Skeptischer Zweifel <span class="hp">Vicikiccha 疑</span></div>
<p style="font-size:10.5pt;margin-top:2mm;">Lähmende Unentschlossenheit. Frage: Trennt mein Zweifel mich von meinen Zielen?</p></div>
<h2 class="t2">Die RAIN-Methode</h2>
<div class="ib">{fig_rain()}</div>
<div class="qb">„Lass es einfach regnen." &nbsp;·&nbsp; <em>Just let it RAIN.</em><div class="au">— Shi Heng Yi (TEDxVitosha)</div></div>
<hr class="or">
<h2 class="t2">Die fünf Elemente — Wu Xing 五行</h2>
<table class="pl">
<thead><tr><th>Element</th><th>Organ</th><th>Emotion</th><th>Heilton</th><th>Jahreszeit</th></tr></thead>
<tbody>
<tr><td><strong>Holz 木</strong></td><td>Leber / Gallenblase</td><td>Wut · Kreativität</td><td>Xu (虛)</td><td>Frühling</td></tr>
<tr><td><strong>Feuer 火</strong></td><td>Herz / Dünndarm</td><td>Freude · Aufregung</td><td>Ha (哈)</td><td>Sommer</td></tr>
<tr><td><strong>Erde 土</strong></td><td>Milz / Magen</td><td>Sorge · Grübeln</td><td>Hu (呼)</td><td>Spätsommer</td></tr>
<tr><td><strong>Metall 金</strong></td><td>Lunge / Dickdarm</td><td>Trauer · Loslassen</td><td>Si (嘶)</td><td>Herbst</td></tr>
<tr><td><strong>Wasser 水</strong></td><td>Nieren / Blase</td><td>Angst · Weisheit</td><td>Chui (吹)</td><td>Winter</td></tr>
</tbody></table>
</div>'''

def teil2():
    sub2 = '&#8222;Der Atem ist immer im Hier und Jetzt.&#8220;<br><em>&#8212; Shi Heng Yi</em>'
    return f'''{ch("Teil II","II","禪定","Chan-Meditation",sub2)}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Bodhidharma und die Wurzel des Chan</h2>
<p>Chan (禅) wurde im 6. Jh. von Bodhidharma (Da Mo, 達摩) im Shaolin-Kloster etabliert. Er soll neun Jahre lang in einer Höhle meditiert haben — <em>bìguān</em> (壁觀), Wandmeditation. Danach entwickelte er das Yi Jin Jing für die körperlich geschwächten Mönche.</p>
<div class="qb">„Shaolin ist Chan. Die Bewegungen, Formen, Disziplin — alles ist ein Fahrzeug für das Verständnis des Selbst."<div class="au">— Shi Heng Yi</div></div>
<h2 class="t2">Die Sitzhaltung — Sieben Punkte</h2>
<div class="ib">{fig_zazen()}<div class="ic">Die anatomischen Korrekturpunkte der Chan-Sitzmeditation</div></div>
<h2 class="t2">Schritt-für-Schritt: Deine Meditationspraxis</h2>
<div class="pb"><div class="pt">Die tägliche Sitzmeditation</div>
<div class="sr"><span class="sn">1</span><div class="st"><strong>Ort wählen.</strong> Täglich gleicher Ort — das Gehirn assoziiert ihn mit Stille.</div></div>
<div class="sr"><span class="sn">2</span><div class="st"><strong>Sieben Punkte einstellen.</strong> Kiefer locker. Zunge am Gaumen. Schultern fallen. Hände im Dhyana-Mudra.</div></div>
<div class="sr"><span class="sn">3</span><div class="st"><strong>Ausatmen — einatmen.</strong> Fokus liegt auf dem Empfangen des Einatems als Lebenskraft.</div></div>
<div class="sr"><span class="sn">4</span><div class="st"><strong>Dan Tian als Anker.</strong> Aufmerksamkeit drei Fingerbreit unter den Nabel. Mindestens 9 Atemzüge.</div></div>
<div class="sr"><span class="sn">5</span><div class="st"><strong>Gedanken beobachten.</strong> Nicht kämpfen. RAIN bei Hindernissen anwenden.</div></div>
<div class="sr"><span class="sn">6</span><div class="st"><strong>Dauer steigern.</strong> Anfänger: 10–15 Min. Mittelstufe: 20–30 Min. Tempel: 45–60 Min.</div></div>
</div>
<h2 class="t2">Der Affen-Geist</h2>
<div class="kp"><p><strong>Benennen:</strong> „Planung." „Sorge." — benannt, losgelassen.</p>
<p><strong>Atem als Anker:</strong> Bei jedem Abschweifen sanft zurückkehren.</p>
<p><strong>Non-Identifikation:</strong> <em>„Ich bin nicht meine Gedanken. Ich bin der Himmel."</em></p>
<p><strong>Neun Atemzüge:</strong> Vor jeder Reaktion im Alltag.</p></div>
<hr class="or">
<h2 class="t2">Kinhin — Die Gehmeditation</h2>
<div style="display:flex;gap:8mm;align-items:flex-start;margin:4mm 0;">
<div style="flex-shrink:0;">{fig_kinhin()}</div>
<div style="flex:1;">
<p style="font-size:10.5pt;">Kinhin (経行) folgt auf die Sitzmeditation und bringt die innere Stille in Bewegung.</p>
<div class="kp"><p>Hände in Gassho (gefaltet) vor der Brust</p>
<p>Schrittlänge: halbe Fußlänge</p>
<p>Rechter Fuß beim Einatmen, linker beim Ausatmen</p>
<p>Tempo: sehr langsam — halb so schnell wie normal</p></div>
</div></div>
<hr class="or">
<h2 class="t2">Metta — Das Mitgefühl kultivieren</h2>
<p style="text-align:center;font-size:9pt;color:#8B1A0E;font-style:italic;margin-bottom:4mm;">Cí Bēi Guān 慈悲觀 — Loving-Kindness Meditation</p>
<div class="pb"><div class="pt">Metta-Praxis — 15 Minuten täglich</div>
<div class="sr"><span class="sn">1</span><div class="st"><strong>Sitzhaltung (2 Min.).</strong> Drei tiefe Atemzüge. Ankommen.</div></div>
<div class="sr"><span class="sn">2</span><div class="st"><strong>Für dich selbst (4 Min.).</strong> <em>„Möge ich glücklich, gesund, in Frieden sein."</em></div></div>
<div class="sr"><span class="sn">3</span><div class="st"><strong>Für nahe Menschen (3 Min.).</strong> Dieselben Worte, auf ihn/sie gerichtet.</div></div>
<div class="sr"><span class="sn">4</span><div class="st"><strong>Für neutrale Menschen (3 Min.).</strong> Jemand den du kaum kennst.</div></div>
<div class="sr"><span class="sn">5</span><div class="st"><strong>Für alle Wesen (3 Min.).</strong> Das Feld der liebenden Güte — ohne Grenzen.</div></div>
</div>
</div>'''

def teil3():
    return f'''{ch("Teil III","III","站樁","Zhan Zhuang","Stehen wie ein Pfahl. In äußerer Stille — maximale innere Arbeit.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Das Prinzip</h2>
<p>Zhan Zhuang (站桩) verbindet seit 27 Jahrhunderten körperliche Kraft mit innerer Kultivierung. Von außen: nichts passiert. Von innen: der Geist spürt Spannungen auf, der Körper entwickelt elastische innere Kraft.</p>
<div class="qb">„In der Ruhe muss Dynamik sein. In der Bewegung muss Ruhe sein. Ruhe ist die Mutter aller Bewegungen."</div>
<h2 class="t2">Song 松 — Das Loslassen</h2>
<div class="kp"><p><strong>Physisch:</strong> Muskeln hängen. Gelenke öffnen. Schwere sinkt in den Boden.</p>
<p><strong>Atem:</strong> Lang, leise, durch die Nase. Dan Tian dehnt sich allseitig.</p>
<p><strong>Mental:</strong> Shi Heng Yi: <em>„Let the drama out of your mind."</em></p></div>
<h2 class="t2">Die fünf Kernhaltungen</h2>
<div class="ht2">1. Wuji-Stand <span class="hc">無極樁</span></div>
<div style="display:flex;gap:7mm;align-items:flex-start;margin:3mm 0 6mm;">
<div style="flex-shrink:0;">{fig_wuji()}</div>
<div style="flex:1;">
<p style="font-size:10.5pt;">Der Ausgangspunkt aller Praxis. Wuji = Leere vor dem Beginn.</p>
<div class="kp"><p>Füße parallel, schulterbreit. Gewicht auf Yongquan</p>
<p>Knie minimal gebeugt — nie durchgestreckt</p>
<p>Becken neutral. Baihui zieht nach oben</p>
<p>Schultern locker. Augen halb geschlossen. Zunge am Gaumen</p></div>
<p style="font-size:9pt;color:#8B1A0E;font-style:italic;">Dauer: 3–30 Minuten</p>
</div></div>
<div class="ht2">2. Den Baum halten <span class="hc">撑抱樁</span></div>
<div style="display:flex;gap:7mm;align-items:flex-start;margin:3mm 0 6mm;">
<div style="flex-shrink:0;">{fig_baum()}</div>
<div style="flex:1;">
<p style="font-size:10.5pt;">Arme auf Brusthöhe, als umarmst du einen großen Baum.</p>
<div class="kp"><p>Ellbogen tiefer als Handgelenke</p>
<p>Achseln „offen" — Tischtennisbälle eingeklemmt</p>
<p>Handflächen zum Körper, Finger entspannt</p></div>
<p style="font-size:10pt;font-style:italic;">Vorstellung: Ein Qi-Ball zwischen Händen und Brust.</p>
<p style="font-size:9pt;color:#8B1A0E;font-style:italic;">Dauer: 5–20 Minuten</p>
</div></div>
<div class="ht2">3. Reiterhaltung <span class="hc">馬步 Mǎ Bù</span></div>
<div style="display:flex;gap:7mm;align-items:flex-start;margin:3mm 0 6mm;">
<div style="flex-shrink:0;">{fig_mabu()}</div>
<div style="flex:1;">
<p style="font-size:10.5pt;">Zwei Schulterbreiten, Knie tief gebeugt, Rücken aufrecht. <em>„Das ist Willenskraft."</em></p>
<div class="kp"><p>Füße geradeaus — nie nach außen</p>
<p>Knie über Zehenspitzen — nie nach innen</p>
<p>Steißbein senkrecht — kein Hohlkreuz</p></div>
<p style="font-size:9pt;color:#8B1A0E;font-style:italic;">Dauer: 2–10 Minuten</p>
</div></div>
<div class="ht2">4. Hockender Affe <span class="hc">蹲猴式</span></div>
<div style="display:flex;gap:7mm;align-items:flex-start;margin:3mm 0 6mm;">
<div style="flex-shrink:0;">{fig_squat()}</div>
<div style="flex:1;">
<p style="font-size:10.5pt;"><em>„Täglich 15 Minuten — unmittelbar in dem Zustand, bei dem der ganze Körper schüttelt."</em></p>
<div class="qb" style="font-size:10pt;">"Brennen ist gut. Feuer transformiert den Körper."<div class="au">— Shi Heng Yi</div></div>
<p style="font-size:9pt;color:#8B1A0E;font-style:italic;">Dauer: 5–15 Minuten (mit Zittern)</p>
</div></div>
<div class="ht2">5. Schlangenstand <span class="hc">蛇形樁</span></div>
<p style="font-size:10.5pt;">Fortgeschrittene Haltung: leichte S-Form der Wirbelsäule, Hände auf Dan Tian. Erst nach 3–6 Monaten Basis üben.</p>
<hr class="or">
<h2 class="t2">Nei Gong — Die innere Arbeit 内功</h2>
<div class="row"><div class="col">
<div class="cb"><div class="ct">1. Breathing &amp; Intention</div><p style="font-size:10pt;">Atem als Vehikel für Yi. Wo der Atem hingeht, folgt das Qi.</p></div>
<div class="cb" style="margin-top:3mm;"><div class="ct">2. Attention &amp; Frequency</div><p style="font-size:10pt;">Wo Aufmerksamkeit ist, sammelt sich Qi.</p></div>
<div class="cb" style="margin-top:3mm;"><div class="ct">3. Refinement</div><p style="font-size:10pt;">Schrittweise Verfeinerung vom Groben zum Feinen.</p></div>
</div><div class="col">
<div class="cb"><div class="ct">4. Smallest to Biggest</div><p style="font-size:10pt;">Von der Fingerkuppe zum ganzen Körperraum.</p></div>
<div class="cb" style="margin-top:3mm;"><div class="ct">5. Mental Objects</div><p style="font-size:10pt;">Visualisierung von Licht, Wärme, Fluss verstärkt den Qi-Fluss.</p></div>
</div></div>
<h2 class="t2">Was während des Stehens passiert</h2>
<table class="pl">
<thead><tr><th>Phase</th><th>Empfindung</th><th>Anweisung</th></tr></thead>
<tbody>
<tr><td>0–3 Min.</td><td>Anfängliches Behagen, Geist schweift</td><td>Körper wahrnehmen, nicht bewerten</td></tr>
<tr><td>3–7 Min.</td><td>Brennen, Knieschmerz</td><td>„Der Geist will aufhören. Du bist stärker."</td></tr>
<tr><td>7–15 Min.</td><td>Zittern, Schwitzen</td><td>Atem fließen lassen. Song. Lächeln.</td></tr>
<tr><td>15–30 Min.</td><td>Tiefe Entspannung, Wärme im Dan Tian</td><td>Awareness halten</td></tr>
<tr><td>30+ Min.</td><td>Elastische Kraft, vertiefte Atmung</td><td>Dan Tian als Zentrum halten</td></tr>
</tbody></table>
</div>'''

def teil4():
    sub4 = "Jedes Mal wenn du einatmest, betritt Lebenskraft deinen Körper.<br><em>— Shi Heng Yi</em>"
    return f'''{ch("Teil IV","IV","呼吸","Atemtechniken",sub4)}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Die drei Säulen des Qi Gong</h2>
<div class="row">
<div class="col"><div class="cb"><div class="ct">1. Körper (调身)</div><p style="font-size:10pt;">Physische Struktur und Ausrichtung.</p></div>
<div class="cb" style="margin-top:3mm;"><div class="ct">2. Atem (调息)</div><p style="font-size:10pt;">Tiefe, Dauer, Intensität, Volumen.</p></div></div>
<div class="col"><div class="cb"><div class="ct">3. Intention (调心)</div><p style="font-size:10pt;">Yi: Wo die Aufmerksamkeit ist, fließt das Qi.</p></div>
<div class="qb" style="margin-top:3mm;font-size:10pt;">„Bewegung ist die Konsequenz von Qi. Qi folgt der Intention."<div class="au">— Shi Heng Yi</div></div></div>
</div>
<div class="ib">{fig_atem()}<div class="ic">Bauchatmung: Atem tief in den Dan Tian — Ausatmung immer länger als Einatmung</div></div>
<h2 class="t2">Sechs Stufen der Atemverfeinerung</h2>
<table class="pl">
<thead><tr><th>Stufe</th><th>Name</th><th>Beschreibung</th></tr></thead>
<tbody>
<tr><td>1</td><td>Lungenatmung (肺呼吸)</td><td>Brustatmung — flach, schnell. Häufigste Alltagsform.</td></tr>
<tr><td>2</td><td>Bauchatmung / Dan Tian</td><td>Grundlage aller Qigong-Praxis.</td></tr>
<tr><td>3</td><td>Umgekehrte Bauchatmung</td><td>Bauch zieht beim Einatmen EIN — Qi-Verdichtung.</td></tr>
<tr><td>4</td><td>Fersenatmung (踵息)</td><td>Energie fließt bis in die Fersen (Zhuangzi).</td></tr>
<tr><td>5</td><td>Porenatmung (毛孔呼吸)</td><td>Jede Pore atmet. Körper und Umgebung durchlässig.</td></tr>
<tr><td>6</td><td>Embryonalatmung (胎息)</td><td>Kaum merklicher Atem. Vollständige Stille.</td></tr>
</tbody></table>
<h2 class="t2">Sieben zentrale Atemübungen</h2>
<h3 class="t3">1. Achtsame Atmung</h3>
<div class="cb"><p style="font-size:10.5pt;">Wuji-Stand. Atemstrom beobachten ohne zu verändern. 9 Atemzüge. <em>„Beobachte ihn zuerst."</em> 5–10 Min. täglich als Einstieg.</p></div>
<h3 class="t3">2. Tiefe Bauchatmung (腹式呼吸)</h3>
<div class="cb"><p style="font-size:10.5pt;">Einatmen: Bauch wölbt sich wie ein Ballon. Ausatmen: sanft einziehen. Verhältnis 4:6 bis 8:12 Sek. 5–15 Min. täglich.</p></div>
<h3 class="t3">3. Umgekehrte Bauchatmung</h3>
<div class="cb"><p style="font-size:10.5pt;">Beim Einatmen zieht der Bauch sich EIN. Qi-Verdichtung für innere Kraft. <span style="color:#8B1A0E;font-weight:bold;">Erst nach stabiler Bauchatmung. Nicht bei Bluthochdruck.</span></p></div>
<h3 class="t3">4. Einatmen/Ausatmen in Bewegung</h3>
<div class="row">
<div class="col"><div class="cb"><div class="ct">Einatmen bei:</div><p style="font-size:10pt;">Heben · Öffnen · Strecken · Aufwärts</p></div></div>
<div class="col"><div class="cb"><div class="ct">Ausatmen bei:</div><p style="font-size:10pt;">Senken · Schließen · Kraft · Abwärts</p></div></div>
</div>
<h3 class="t3">5. Großer Atemzyklus</h3>
<div class="cb"><p style="font-size:10.5pt;">8 Sek. ein — 12 Sek. aus. Ziel: 4–6 Atemzüge pro Minute. 5–10 Min. Abschluss jeder Einheit.</p></div>
<h3 class="t3">6. Liu Zi Jue — Die sechs Heiltöne</h3>
<div class="cb"><p style="font-size:10.5pt;">Xu (Leber), Ha (Herz), Hu (Milz), Si (Lunge), Chui (Nieren), Xi (San Jiao). Beim langen Ausatmen gesprochen. Je 6–9 Wiederholungen täglich.</p></div>
<h3 class="t3">7. Zhan Zhuang Atmung</h3>
<div class="cb"><p style="font-size:10.5pt;">Natürliche Bauchatmung durch die Nase. Ausatmen: Spannung in den Boden entladen. Einatmen: Erdenergie durch Yongquan aufwärts. Nach 15 Min. vertieft sich der Atem automatisch.</p></div>
</div>'''

def teil5():
    return f'''{ch("Teil V","V","氣功","Shaolin Qigong","Ba Duan Jin · Yi Jin Jing · Shu Jing Gong")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Ba Duan Jin 八段錦 — Die Acht Brokate</h2>
<p style="text-align:center;font-size:9pt;color:#8B1A0E;font-style:italic;margin-bottom:4mm;">Song-Dynastie (960 n. Chr.) · „Schön wie kostbarer Brokatstoff"</p>
<p>Shi Heng Yi: <em>„Bleibe in jeder Haltung. Mindestens 4 Atemzyklen. Halte die Kraft gleichmäßig."</em></p>
<div style="display:flex;gap:8mm;align-items:flex-start;margin:4mm 0;">
<div style="flex-shrink:0;">{fig_wei_tuo()}</div>
<div style="flex:1;">
<div class="ht2">Posture 1: Himmel stützen <span class="hc">托天式</span></div>
<p style="font-size:10.5pt;">Finger verschränken, Hände über den Kopf, Handflächen nach oben. Fersen heben. <strong>Wirkung:</strong> San Jiao, Faszienketten, Lunge.</p>
<div class="kp"><p>Einatmen beim Heben — Ausatmen beim Senken</p>
<p>Rippen nicht nach vorne — aufrecht bleiben</p></div>
<p style="font-size:9pt;color:#8B1A0E;">6 Wiederholungen</p>
</div></div>
<div style="display:flex;gap:8mm;align-items:flex-start;margin:4mm 0;">
<div style="flex-shrink:0;">{fig_bogen()}</div>
<div style="flex:1;">
<div class="ht2">Posture 2: Den Bogen spannen <span class="hc">射雕式</span></div>
<p style="font-size:10.5pt;">Reiterhaltung. Linker Zeigefinger oben (BaZi). Rechte Faust zieht den goldenen Bogen. <strong>Wirkung:</strong> Lungen- und Herzmeridian, Brustwirbelsäule.</p>
<div class="kp"><p>Blick folgt dem Zeigefinger</p>
<p>Rücken aufrecht — kein Einsinken</p></div>
<p style="font-size:9pt;color:#8B1A0E;">3 Wiederholungen je Seite</p>
</div></div>
<table class="pl" style="margin-top:5mm;">
<thead><tr><th>#</th><th>Name</th><th>Chinesisch</th><th>Hauptwirkung</th><th>Wdh.</th></tr></thead>
<tbody>
<tr><td>1</td><td>Himmel stützen</td><td>双手托天</td><td>San Jiao · Lunge</td><td>6×</td></tr>
<tr><td>2</td><td>Bogen spannen</td><td>左右开弓</td><td>Herz- u. Lungenmeridian</td><td>3× je S.</td></tr>
<tr><td>3</td><td>Himmel und Erde spalten</td><td>调理脾胃</td><td>Milz · Magen · Verdauung</td><td>6×</td></tr>
<tr><td>4</td><td>Die weise Eule blickt zurück</td><td>五劳七伤</td><td>Nacken · Wirbelsäule · Du Mai</td><td>3× je S.</td></tr>
<tr><td>5</td><td>Der Bär bewegt sich</td><td>摇头摆尾</td><td>Herzfeuer kühlen</td><td>6×</td></tr>
<tr><td>6</td><td>Die Zehen berühren</td><td>两手攀足</td><td>Nieren · Lende · Ren Mai</td><td>6×</td></tr>
<tr><td>7</td><td>Fäuste ballen, grimmig schauen</td><td>攒拳怒目</td><td>Leber · Muskelkraft</td><td>6×</td></tr>
<tr><td>8</td><td>Siebenmaliges Wippen</td><td>背后七颠</td><td>Qi glätten · Nieren</td><td>7×</td></tr>
</tbody></table>
<hr class="or">
<h2 class="t2">Yi Jin Jing 易筋經 — Muskel-Sehnen-Wandlung</h2>
<p>12 Übungen, stehend, Bodhidharma zugeschrieben. <em>„Du musst fühlen, welchen Teil des Körpers jede Übung beeinflusst."</em></p>
<table class="pl">
<thead><tr><th>#</th><th>Name</th><th>Chinesisch</th><th>Hauptwirkung</th></tr></thead>
<tbody>
<tr><td>1</td><td>Wei Tuo — Vorwärts</td><td>韦驮献杵一</td><td>Geist beruhigen, Atem regulieren</td></tr>
<tr><td>2</td><td>Wei Tuo — Seitwärts</td><td>韦驮献杵二</td><td>Schultern, Qi-Zirkulation</td></tr>
<tr><td>3</td><td>Wei Tuo — Aufwärts</td><td>韦驮献杵三</td><td>San Jiao öffnen</td></tr>
<tr><td>4</td><td>Sterne pflücken</td><td>摘星换斗</td><td>Nieren und Mingmen</td></tr>
<tr><td>5</td><td>Neun Ochsen ziehen</td><td>倒拽九牛尾</td><td>Herz- und Lungenmeridian</td></tr>
<tr><td>6</td><td>Krallen zeigen</td><td>出爪亮翅</td><td>Lunge öffnen, Brustkorb weiten</td></tr>
<tr><td>7</td><td>Reiterschwert</td><td>九鬼拔马刀</td><td>Yin-Meridiane, Herz-Niere</td></tr>
<tr><td>8</td><td>Drei Teller</td><td>三盘落地</td><td>Nieren stärken</td></tr>
<tr><td>9</td><td>Schwarzer Drache</td><td>青龙探爪</td><td>Leber, Schulterblatt</td></tr>
<tr><td>10</td><td>Tiger springt auf Beute</td><td>卧虎扑食</td><td>Du Mai, Wirbelsäule</td></tr>
<tr><td>11</td><td>Verbeugend grüßen</td><td>打躬势</td><td>Gehirn durchbluten</td></tr>
<tr><td>12</td><td>Den Schwanz schwingen</td><td>掉尾势</td><td>Integration · alle Meridiane</td></tr>
</tbody></table>
<div class="cb" style="margin-top:4mm;"><div class="ct">Stufenweise Wirkungen</div>
<p style="font-size:10pt;">Jahr 1: Vitalität · Jahr 2: Blutzirkulation · Jahr 3: Sehnen elastisch · Jahr 4: Meridiane · Jahr 5: Knochenmark</p></div>
<hr class="or">
<h2 class="t2">Shu Jing Gong 舒筋功</h2>
<p style="text-align:center;font-size:9pt;color:#8B1A0E;font-style:italic;">„Smooth Relaxation Practice" · Shaolin Temple Europe · 10 Sektionen mit Mantra</p>
<p>Shi Heng Yi: <em>„Reguliert zuerst den Körper, dann die Atmung, dann die Emotionen, dann das Qi und schließlich den Geist."</em></p>
<table class="pl">
<thead><tr><th>Sektion</th><th>Name</th><th>Schwerpunkt</th></tr></thead>
<tbody>
<tr><td>Intro</td><td>Demonstration mit Atmung und Mantra</td><td>Vorbereitung · Intention</td></tr>
<tr><td>1</td><td>Hände drücken den Himmel</td><td>Nacken und Schultern</td></tr>
<tr><td>2</td><td>Der Handfläche folgen</td><td>Schultergelenke mobilisieren</td></tr>
<tr><td>3</td><td>Die Fäuste scheren</td><td>Brustkorb und Rücken</td></tr>
<tr><td>4</td><td>Den Geist klären</td><td>Hals und Kopf befreien</td></tr>
<tr><td>5</td><td>Bogen und Pfeil</td><td>Wirbelsäule und Brust</td></tr>
<tr><td>6</td><td>Himmel und Erde wenden</td><td>Ganzkörper-Integration</td></tr>
<tr><td>7</td><td>Allwissender Geist</td><td>Mentale Klarheit</td></tr>
<tr><td>8</td><td>Das Dharma-Rad</td><td>Qi ausbreiten</td></tr>
<tr><td>9</td><td>Den Geist leeren</td><td>Stille und Loslassen</td></tr>
<tr><td>10</td><td>Buddhas Verbeugung</td><td>Dankbarkeit und Abschluss</td></tr>
</tbody></table>
</div>'''

def trainingsplan():
    return f'''{ch("Dein Weg","","修煉計劃","San Xiu Trainingsplan","Wochenweise Progression · 13 Übungen · 6 Wochen · 19–49 Min. täglich")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Tagesstruktur</h2>
<div class="pb"><div class="pt">Die vollständige tägliche Einheit</div>
<div class="sr"><span class="sn">1</span><div class="st"><strong>Atemzentrierung (2 Min.).</strong> Wuji-Stand. Bauchatmung. Körper scannen.</div></div>
<div class="sr"><span class="sn">2</span><div class="st"><strong>Kern-Übungen 1–4 (Sanshin-Basis).</strong> Isometrische Haltearbeit nach Plan.</div></div>
<div class="sr"><span class="sn">3</span><div class="st"><strong>Zhan Zhuang (ab Woche 2).</strong> Baum halten oder Squatting Monkey.</div></div>
<div class="sr"><span class="sn">4</span><div class="st"><strong>Shaolin-Ergänzungen (ab Woche 3).</strong> Ba Duan Jin und Yi Jin Jing.</div></div>
<div class="sr"><span class="sn">5</span><div class="st"><strong>Core &amp; Bauch (ab Woche 5).</strong> Fuhu Gong, Füße greifen, Dan Tian Rotation.</div></div>
<div class="sr"><span class="sn">6</span><div class="st"><strong>Schulter &amp; Qi (ab Woche 6).</strong> Diao Bang, Yang Dan Qi.</div></div>
<div class="sr"><span class="sn">7</span><div class="st"><strong>Nachspüren (2 Min.).</strong> Körper lockern. 60 Sek. still. Hände auf Dan Tian.</div></div>
</div>
<h2 class="t2">Die 13 Übungen — 6 Wochen Progression</h2>
<table class="pl">
<thead><tr><th>#</th><th>Übung</th><th>W1</th><th>W2</th><th>W3</th><th>W4</th><th>W5</th><th>W6</th></tr></thead>
<tbody>
<tr><td>1</td><td>Faust ballen &amp; halten</td><td>4</td><td>5</td><td>6</td><td>6</td><td>6</td><td>6</td></tr>
<tr><td>2</td><td>Reiterhaltung (Ma Bu)</td><td>2</td><td>3</td><td>4</td><td>5</td><td>5</td><td>5</td></tr>
<tr><td>3</td><td>L-Stand / Ausschütteln</td><td>3</td><td>4</td><td>5</td><td>5</td><td>5</td><td>5</td></tr>
<tr><td>4</td><td>Seitenarme / Mittelfinger</td><td>3</td><td>4</td><td>5</td><td>5</td><td>5</td><td>5</td></tr>
<tr><td>5</td><td>Himmel stützen (BdJ #1)</td><td>—</td><td>—</td><td>2</td><td>3</td><td>3</td><td>3</td></tr>
<tr><td>6</td><td>Bogen spannen (BdJ #2)</td><td>—</td><td>—</td><td>2</td><td>3</td><td>3</td><td>3</td></tr>
<tr><td>7</td><td>Wirbelsäulen-Drachen</td><td>—</td><td>—</td><td>—</td><td>2</td><td>2</td><td>2</td></tr>
<tr><td>8</td><td>Kopf-Nacken-Befreiung</td><td>—</td><td>—</td><td>—</td><td>2</td><td>2</td><td>2</td></tr>
<tr><td>9</td><td>Fuhu Gong / Planke</td><td>—</td><td>—</td><td>—</td><td>—</td><td>1</td><td>1</td></tr>
<tr><td>10</td><td>Füße greifen (BdJ #6)</td><td>—</td><td>—</td><td>—</td><td>—</td><td>2</td><td>2</td></tr>
<tr><td>11</td><td>Dan Tian Rotation</td><td>—</td><td>—</td><td>—</td><td>—</td><td>3</td><td>3</td></tr>
<tr><td>12</td><td>Diao Bang (Schultern)</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>3</td></tr>
<tr><td>13</td><td>Yang Dan Qi</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>4</td></tr>
<tr><td colspan="2" style="font-weight:bold;">+ Einstieg / Abschluss</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td></tr>
<tr class="tot"><td colspan="2">GESAMT ca. (Min.)</td><td>~19</td><td>~24</td><td>~32</td><td>~36</td><td>~42</td><td>~49</td></tr>
</tbody></table>
<h2 class="t2">Tempel-Tagesrhythmus (Shi Heng Yi)</h2>
<table class="pl">
<thead><tr><th>Zeit</th><th>Aktivität</th></tr></thead>
<tbody>
<tr><td>Aufwachen</td><td>„Wake up empty" — ohne Gedanken vom Vortag</td></tr>
<tr><td>Morgen</td><td>Sitzen, atmen, Körper scannen (1 Stunde)</td></tr>
<tr><td>Früh</td><td>Push-ups, Squatting Monkey (15 Min. halten)</td></tr>
<tr><td>Vormittag</td><td>Qigong-Praxis (Ba Duan Jin, Yi Jin Jing, Shu Jing Gong)</td></tr>
<tr><td>Mittag</td><td>90% vegetarische Mahlzeit, bewusstes Essen</td></tr>
<tr><td>Nachmittag</td><td>Kung Fu-Training, Zhan Zhuang, Studium</td></tr>
<tr><td>Abend</td><td>Sitzmeditation, Stille, früh schlafen gehen</td></tr>
</tbody></table>
<h2 class="t2">Die sieben Praxis-Prinzipien</h2>
<div class="kp">
<p><strong>Atem ist der Dirigent.</strong> Niemals anhalten — auch in schmerzhaften Momenten.</p>
<p><strong>Zittern ist Fortschritt.</strong> Tiefe Muskelschichten werden aktiviert.</p>
<p><strong>Drei verborgene Spannungsfelder:</strong> Kiefer locker · Zunge am Gaumen · Nacken lang.</p>
<p><strong>Yi — Die Kraft der Vorstellung.</strong> Wo die Aufmerksamkeit hingeht, fließt das Qi.</p>
<p><strong>Schmerz vs. Brennen.</strong> Muskelfeuer: erwünscht. Gelenkschmerz: aufhören.</p>
<p><strong>Regelmäßigkeit schlägt Intensität.</strong> Täglich 20 Min. schlägt 90 Min. einmal pro Woche.</p>
<p><strong>Nachspüren ist Pflicht.</strong> Nie abrupt aufhören. 60 Sekunden stilles Nachspüren.</p>
</div>
</div>'''

def zitate():
    def z(t,s): return f'<div class="zi"><div class="zt">„{t}"</div><div class="zs">— {s}</div></div>'
    return f'''{ch("Anhang I","","語錄","Meister Shi Heng Yi","Ausgewählte Lehren zur täglichen Begleitung")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Über Selbstmeisterschaft</h2>
{z("Es gibt zwei Fehler auf dem Weg zur Selbstmeisterschaft: Nicht damit anzufangen. Und nicht den ganzen Weg zu gehen.","Shi Heng Yi")}
{z("Selbstmeisterschaft bedeutet zu erkennen: Wenn du glücklich sein willst, bist du derjenige, der es erzeugen muss.","Shi Heng Yi")}
{z("Freiheit geht Hand in Hand mit deiner Fähigkeit, dich selbst einzuschränken. Disziplin ist Freiheit.","Shi Heng Yi")}
{z("Vervollkommnung kommt durch Wiederholung.","Shi Heng Yi")}
{z("Was man will, ist nicht so wichtig. Entscheidend ist, welche Opfer, welches Leid man bereit ist, auf sich zu nehmen.","Shi Heng Yi")}
{z("Löse dich von der Idee, das Leben wäre leicht.","Shi Heng Yi")}
<h2 class="t2">Über Geist und Bewusstsein</h2>
{z("Du bist nicht deine Gedanken. Du bist der Himmel. Manchmal ist er klar, manchmal gibt es Wolken.","Shi Heng Yi")}
{z("Wenn der See still ist, siehst du den Grund. Wenn dein Geist still ist, erkennst du dich selbst.","Shi Heng Yi")}
{z("Ich suche nicht nach Glück. Ich suche nach Frieden. Wenn es Glück gibt, gibt es Trauer.","Shi Heng Yi")}
{z("Gefühl ist die Verkündigung des Geistes. Was du fühlst, wurde zuerst in deinem Geist aufgebaut.","Shi Heng Yi")}
<h2 class="t2">Über Körper, Übung und den Weg</h2>
{z("Mentale Stärke benötigt eine sichtbare Form. Nutze deinen Körper, um zum Geist zu gelangen.","Shi Heng Yi")}
{z("Leben ist Bewegung. Je fließender du bist, desto mehr bist du lebendig.","Shi Heng Yi")}
{z("Warte nicht darauf, dass sich die Welt ändert. Beginne mit dir selbst.","Shi Heng Yi")}
{z("Du wirst nicht über Nacht ankommen. Aber wenn du weitermachst, wirst du ankommen.","Shi Heng Yi")}
{z("Spare dir dein Grimassieren, dein Klagen, dein Leiden — und wandle es in innere Energie um.","Shi Heng Yi")}
{z("Im Shaolin ist Natur nicht etwas außerhalb von uns. Wir sind ein Teil davon.","Shi Heng Yi")}
<div class="qb" style="margin-top:8mm;font-size:12pt;text-align:center;line-height:1.9;">
„Dorthin, wo deine Aufmerksamkeit fließt,<br>dorthin fließt auch deine Energie."
<div class="au" style="font-size:10pt;margin-top:3mm;">— Daoyin-Tradition</div></div>
</div>'''

def glossar():
    def g(t,c,d): return f'<div class="gi"><span class="gt">{t}</span><span class="gc">{c}</span><div class="gd">{d}</div></div>'
    return f'''{ch("Anhang II","","詞彙","Glossar","Chinesische Begriffe und ihre Bedeutungen")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Grundbegriffe</h2>
{g("Qi","氣","Lebensenergie. Fließt durch Meridiane. Folgt der Intention. Wird durch Qigong kultiviert.")}
{g("Jing","精","Essenz. Die dichteste Lebensenergie — in den Nieren gespeichert.")}
{g("Shen","神","Geist, Bewusstsein. Das Subtilste der drei Schätze. Residiert im Herzen.")}
{g("Yi","意","Intention. Formel: Yi → Qi → Bewegung. Wo die Aufmerksamkeit ist, fließt das Qi.")}
{g("Dan Tian","丹田","Energiezentrum. 3 Fingerbreit unter dem Nabel. Primäres Zentrum der Qigong-Praxis.")}
{g("Song","松","Durchlässigkeit, Loslassen. Aktives Lösen von Spannung. Grundprinzip des Zhan Zhuang.")}
{g("Chan","禪","Zen. Meditationstradition, die Bodhidharma im Shaolin-Kloster begründete.")}
{g("Wu De","武德","Kriegerische Tugend. Die 14 ethischen Grundsätze der Shaolin-Praxis.")}
<h2 class="t2" style="margin-top:5mm;">Übungsbegriffe</h2>
{g("Zhan Zhuang","站桩","Stehende Pfahlarbeit. Statische Stehübung zur Entwicklung innerer Kraft. Über 27 Jahrhunderte alt.")}
{g("Ba Duan Jin","八段锦","Acht-Brokate-Qigong. 8 Haupthaltungen. Seit der Song-Dynastie (960 n. Chr.) belegt.")}
{g("Yi Jin Jing","易筋经","Muskel-Sehnen-Wandlungsklassiker. 12 Übungen, Bodhidharma zugeschrieben.")}
{g("Shu Jing Gong","舒筋功","Buddhistische Qigong-Form des Shaolin Temple Europe. 10 Sektionen mit Mantra.")}
{g("Ma Bu","马步","Reiterhaltung. Breiter, tiefer Stand. Grundlegende Kraftübung.")}
{g("Wuji","无极","Leere vor dem Beginn. Der neutrale Grundstand, aus dem alle Formen entstehen.")}
{g("Baihui","百会","Scheitelakupunkturpunkt (GV20). Verbindung mit dem Yang des Himmels.")}
{g("Yongquan","涌泉","Sprudelnde Quelle (KD1). Im vorderen Fußdrittel. Erdungspunkt im Zhan Zhuang.")}
{g("Nei Gong","内功","Innere Arbeit. Bewusste Lenkung von Yi und Qi durch den Körper.")}
{g("Kinhin","経行","Gehmeditation der Chan/Zen-Tradition. Bringt innere Stille in Bewegung.")}
{g("San Xiu","三修","Der dreifache Weg. Gleichzeitige Kultivierung von Körper, Atem und Geist.")}
<hr class="or">
<p style="text-align:center;font-size:9pt;color:#8B1A0E;font-style:italic;margin-top:5mm;line-height:1.9;">
Dieses Buch ist ein persönliches Werkzeug für die tägliche Praxis.<br>
Kein Buch kann die direkte Erfahrung ersetzen.<br>
Beginne. Bleibe dran. Gehe den ganzen Weg.
</p>
<p style="text-align:center;font-size:18pt;color:#8B1A0E;margin-top:6mm;font-family:'Noto Serif CJK SC',serif;">三修</p>
</div>'''

# ─── RENDERER ───────────────────────────────────────────────────────────────

def render_part(sections, name):
    html = H(CSS) + ''.join(sections) + E
    tmp = f'/tmp/san_{name}.pdf'
    print(f"  Rendere {name} ({len(html):,} Zeichen)...", flush=True)
    t0 = time.time()
    HTML(string=html).write_pdf(tmp)
    print(f"  {name} fertig: {time.time()-t0:.1f}s", flush=True)
    return tmp

if __name__ == '__main__':
    print("SAN XIU – Das Buch | Start", flush=True)
    t_total = time.time()

    parts = [
        ('A', [cover(), titelblatt(), toc(), einleitung(), teil1()]),
        ('B', [teil2(), teil3()]),
        ('C', [teil4(), teil5()]),
        ('D', [trainingsplan(), zitate(), glossar()]),
    ]

    pdfs = []
    for name, sections in parts:
        pdfs.append(render_part(sections, name))

    print("Merge PDFs...", flush=True)
    writer = PdfWriter()
    for pdf in pdfs:
        for page in PdfReader(pdf).pages:
            writer.add_page(page)

    with open(OUT, 'wb') as f:
        writer.write(f)

    r = PdfReader(OUT)
    size = os.path.getsize(OUT)
    print(f"\nFertig! {len(r.pages)} Seiten · {size//1024} KB · {time.time()-t_total:.0f}s", flush=True)
    print(f"Output: {os.path.abspath(OUT)}", flush=True)
