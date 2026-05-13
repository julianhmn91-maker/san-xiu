#!/usr/bin/env python3
"""SAN XIU – Das Buch | Komplett neue Edition mit klaren Figuren
Renderpipeline: WeasyPrint + pypdf-Merge."""
import os, time
from weasyprint import HTML
from pypdf import PdfWriter, PdfReader

OUT = 'San_Xiu_Das_Buch.pdf'

# ─── Farbpalette ────────────────────────────────────────────────────────────
SK  = "#D9B488"   # Skin
SD  = "#A07A4C"   # Skin dark
INK = "#1a1208"   # Lines
RED = "#8B1A0E"   # Accent red
GOLD= "#B8961A"   # Accent gold
ROBE= "#3a2418"   # Mönchsrobe
ROBE2="#5a3826"   # Mönchsrobe hell
BG  = "#faf6ec"   # Soft cream

# ═══ SVG GRUNDLAGEN ════════════════════════════════════════════════════════

def _svg(w, h, body, vb=None):
    vbs = vb or f"0 0 {w} {h}"
    return f'<svg viewBox="{vbs}" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{body}</svg>'

def _label(x, y, t, anchor="middle", size=8, color=None, italic=True):
    c = color or RED
    it = ' font-style="italic"' if italic else ''
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Georgia,serif" font-size="{size}pt" fill="{c}"{it}>{t}</text>'

def _arrow(x1, y1, x2, y2, color=None, w=1.4):
    c = color or RED
    import math
    a = math.atan2(y2-y1, x2-x1)
    al = 6
    ax1 = x2 - al*math.cos(a - 0.4)
    ay1 = y2 - al*math.sin(a - 0.4)
    ax2 = x2 - al*math.cos(a + 0.4)
    ay2 = y2 - al*math.sin(a + 0.4)
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"/>'
            f'<path d="M{ax1:.1f},{ay1:.1f} L{x2},{y2} L{ax2:.1f},{ay2:.1f}" fill="none" stroke="{c}" stroke-width="{w}"/>')

def _ground(cx, y, w=80):
    return (f'<line x1="{cx-w}" y1="{y}" x2="{cx+w}" y2="{y}" stroke="{GOLD}" stroke-width="1.6"/>'
            f'<line x1="{cx-w-6}" y1="{y+3}" x2="{cx-w+4}" y2="{y+3}" stroke="{GOLD}" stroke-width="0.7" opacity="0.5"/>'
            f'<line x1="{cx+w-4}" y1="{y+3}" x2="{cx+w+6}" y2="{y+3}" stroke="{GOLD}" stroke-width="0.7" opacity="0.5"/>')

# ═══ KÖRPERTEILE — ANATOMISCH KLAR ══════════════════════════════════════════

def _head(cx, cy, r=14, look="meditative"):
    """Kopf mit erkennbaren Gesichtszügen — schmaler oben (Schädel), breiter zum Kiefer."""
    # Schädelform: leicht eiförmig
    head = f'''<path d="M{cx-r*0.85},{cy-r*0.4} Q{cx-r},{cy-r*0.85} {cx-r*0.55},{cy-r}
        Q{cx},{cy-r*1.15} {cx+r*0.55},{cy-r}
        Q{cx+r},{cy-r*0.85} {cx+r*0.85},{cy-r*0.4}
        Q{cx+r*0.95},{cy+r*0.25} {cx+r*0.7},{cy+r*0.7}
        Q{cx+r*0.35},{cy+r*1.05} {cx},{cy+r*1.05}
        Q{cx-r*0.35},{cy+r*1.05} {cx-r*0.7},{cy+r*0.7}
        Q{cx-r*0.95},{cy+r*0.25} {cx-r*0.85},{cy-r*0.4} Z"
        fill="{SK}" stroke="{INK}" stroke-width="1.6"/>'''
    # Glatze/Schädeldach Schattierung
    head += f'<path d="M{cx-r*0.55},{cy-r*0.9} Q{cx},{cy-r*1.12} {cx+r*0.55},{cy-r*0.9} Q{cx+r*0.3},{cy-r*0.4} {cx},{cy-r*0.5} Q{cx-r*0.3},{cy-r*0.4} {cx-r*0.55},{cy-r*0.9}" fill="{SD}" opacity="0.2"/>'
    # Ohren
    head += f'<path d="M{cx-r*0.95},{cy-r*0.1} Q{cx-r*1.15},{cy} {cx-r*0.95},{cy+r*0.3}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
    head += f'<path d="M{cx+r*0.95},{cy-r*0.1} Q{cx+r*1.15},{cy} {cx+r*0.95},{cy+r*0.3}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
    # Augen
    if look == "meditative":
        head += f'<path d="M{cx-r*0.45},{cy-r*0.1} q{r*0.18},{r*0.08} {r*0.32},0" fill="none" stroke="{INK}" stroke-width="1.4"/>'
        head += f'<path d="M{cx+r*0.13},{cy-r*0.1} q{r*0.18},{r*0.08} {r*0.32},0" fill="none" stroke="{INK}" stroke-width="1.4"/>'
    elif look == "fierce":
        head += f'<ellipse cx="{cx-r*0.3}" cy="{cy-r*0.05}" rx="{r*0.13}" ry="{r*0.08}" fill="{INK}"/>'
        head += f'<ellipse cx="{cx+r*0.3}" cy="{cy-r*0.05}" rx="{r*0.13}" ry="{r*0.08}" fill="{INK}"/>'
        head += f'<path d="M{cx-r*0.55},{cy-r*0.3} L{cx-r*0.05},{cy-r*0.15}" stroke="{INK}" stroke-width="1.4"/>'
        head += f'<path d="M{cx+r*0.55},{cy-r*0.3} L{cx+r*0.05},{cy-r*0.15}" stroke="{INK}" stroke-width="1.4"/>'
    else:  # neutral
        head += f'<circle cx="{cx-r*0.3}" cy="{cy-r*0.05}" r="{r*0.08}" fill="{INK}"/>'
        head += f'<circle cx="{cx+r*0.3}" cy="{cy-r*0.05}" r="{r*0.08}" fill="{INK}"/>'
    # Nase
    head += f'<path d="M{cx},{cy-r*0.05} Q{cx+r*0.05},{cy+r*0.2} {cx},{cy+r*0.3} Q{cx-r*0.08},{cy+r*0.35} {cx-r*0.02},{cy+r*0.3}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.7"/>'
    # Mund
    head += f'<path d="M{cx-r*0.2},{cy+r*0.55} Q{cx},{cy+r*0.62} {cx+r*0.2},{cy+r*0.55}" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.75"/>'
    return head

def _neck(cx, top_y, w=8, h=8):
    """Hals als Trapez."""
    return f'<path d="M{cx-w},{top_y} Q{cx-w*0.9},{top_y+h} {cx-w*0.95},{top_y+h} L{cx+w*0.95},{top_y+h} Q{cx+w*0.9},{top_y+h} {cx+w},{top_y} Z" fill="{SK}" stroke="{INK}" stroke-width="1.4"/>'

def _torso(cx, top_y, shoulder_w=44, waist_w=36, height=70, robe=True):
    """Oberkörper als Trapez mit Falten."""
    sx1, sx2 = cx - shoulder_w, cx + shoulder_w
    wx1, wx2 = cx - waist_w, cx + waist_w
    by = top_y + height
    fill = ROBE if robe else "#2a1a0a"
    op = "1" if robe else "0.12"
    s = f'''<path d="M{sx1},{top_y} L{wx1},{by} L{wx2},{by} L{sx2},{top_y} Z" fill="{fill}" fill-opacity="{op}" stroke="{INK}" stroke-width="2"/>'''
    if robe:
        # Falten
        s += f'<line x1="{cx-shoulder_w*0.4}" y1="{top_y+4}" x2="{cx-waist_w*0.4}" y2="{by-4}" stroke="{INK}" stroke-width="0.7" opacity="0.35"/>'
        s += f'<line x1="{cx}" y1="{top_y+6}" x2="{cx}" y2="{by-6}" stroke="{INK}" stroke-width="0.5" opacity="0.25"/>'
        s += f'<line x1="{cx+shoulder_w*0.4}" y1="{top_y+4}" x2="{cx+waist_w*0.4}" y2="{by-4}" stroke="{INK}" stroke-width="0.7" opacity="0.35"/>'
        # Kragenlinie
        s += f'<path d="M{sx1+3},{top_y+1} Q{cx},{top_y+8} {sx2-3},{top_y+1}" fill="none" stroke="{ROBE2}" stroke-width="1.6"/>'
        s += f'<path d="M{cx-6},{top_y+2} L{cx},{top_y+10} L{cx+6},{top_y+2}" fill="{SK}" stroke="{INK}" stroke-width="1.2"/>'
    return s

def _hip_pants(cx, top_y, hip_w=40, height=10, robe=True):
    """Hosenbund / unterer Robenabschluss."""
    x1, x2 = cx - hip_w, cx + hip_w
    fill = ROBE if robe else "#2a1a0a"
    op = "1" if robe else "0.12"
    return f'<path d="M{x1},{top_y} L{x1-2},{top_y+height} L{x2+2},{top_y+height} L{x2},{top_y} Z" fill="{fill}" fill-opacity="{op}" stroke="{INK}" stroke-width="2"/>'

def _arm(sx, sy, ex, ey, hx, hy, side='r', thick=8):
    """Arm mit Schulter, Ellbogen, Hand-Endpunkt. Ellbogen markiert."""
    return (
        f'<path d="M{sx},{sy} Q{(sx+ex)/2+(side=="r")*2-(side=="l")*2},{(sy+ey)/2} {ex},{ey} Q{(ex+hx)/2-(side=="r")*2+(side=="l")*2},{(ey+hy)/2} {hx},{hy}" '
        f'fill="none" stroke="{ROBE}" stroke-width="{thick+2}" stroke-linecap="round" opacity="0.85"/>'
        f'<path d="M{sx},{sy} Q{(sx+ex)/2+(side=="r")*2-(side=="l")*2},{(sy+ey)/2} {ex},{ey} Q{(ex+hx)/2-(side=="r")*2+(side=="l")*2},{(ey+hy)/2} {hx},{hy}" '
        f'fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>'
        f'<circle cx="{ex}" cy="{ey}" r="2" fill="{INK}" opacity="0.7"/>'
    )

def _arm_straight(sx, sy, hx, hy, thick=8):
    """Gerade gestreckter Arm (für Schläge etc.)."""
    return (
        f'<line x1="{sx}" y1="{sy}" x2="{hx}" y2="{hy}" stroke="{ROBE}" stroke-width="{thick+2}" stroke-linecap="round" opacity="0.85"/>'
        f'<line x1="{sx}" y1="{sy}" x2="{hx}" y2="{hy}" stroke="{INK}" stroke-width="1.6"/>'
    )

def _leg(hx, hy, kx, ky, fx, fy, thick=12):
    """Bein mit Hüfte, Knie, Knöchel."""
    return (
        f'<path d="M{hx},{hy} Q{kx-1},{(hy+ky)/2} {kx},{ky} Q{kx+1},{(ky+fy)/2} {fx},{fy}" '
        f'fill="none" stroke="{ROBE}" stroke-width="{thick+3}" stroke-linecap="round" opacity="0.85"/>'
        f'<path d="M{hx},{hy} Q{kx-1},{(hy+ky)/2} {kx},{ky} Q{kx+1},{(ky+fy)/2} {fx},{fy}" '
        f'fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>'
        f'<circle cx="{kx}" cy="{ky}" r="2.5" fill="{INK}" opacity="0.65"/>'
    )

def _foot(cx, cy, dir_='front', size=12):
    """Fuß als Schuh-Andeutung."""
    if dir_ == 'side':
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{size}" ry="{size*0.35}" fill="{INK}" opacity="0.85"/>'
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{size*0.6}" ry="{size*0.3}" fill="{INK}" opacity="0.85"/>'

def _hand_open(cx, cy, dir_='down', size=8):
    """Offene Hand mit 5 erkennbaren Fingern."""
    if dir_ == 'down':
        # Handfläche
        s = f'<ellipse cx="{cx}" cy="{cy}" rx="{size*0.85}" ry="{size}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
        # 4 Finger nach unten
        for i, off in enumerate([-size*0.55, -size*0.2, size*0.15, size*0.5]):
            fl = size * (0.85 if i in (1,2) else 0.7)
            s += f'<rect x="{cx+off-1.5}" y="{cy+size*0.5}" width="3" height="{fl}" rx="1.5" fill="{SK}" stroke="{INK}" stroke-width="1"/>'
        # Daumen
        s += f'<ellipse cx="{cx-size*0.85}" cy="{cy+size*0.1}" rx="2" ry="{size*0.4}" fill="{SK}" stroke="{INK}" stroke-width="1" transform="rotate(-30 {cx-size*0.85} {cy+size*0.1})"/>'
        return s
    if dir_ == 'up':
        s = f'<ellipse cx="{cx}" cy="{cy}" rx="{size*0.85}" ry="{size}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
        for i, off in enumerate([-size*0.55, -size*0.2, size*0.15, size*0.5]):
            fl = size * (0.85 if i in (1,2) else 0.7)
            s += f'<rect x="{cx+off-1.5}" y="{cy-size*0.5-fl}" width="3" height="{fl}" rx="1.5" fill="{SK}" stroke="{INK}" stroke-width="1"/>'
        s += f'<ellipse cx="{cx-size*0.85}" cy="{cy-size*0.1}" rx="2" ry="{size*0.4}" fill="{SK}" stroke="{INK}" stroke-width="1" transform="rotate(30 {cx-size*0.85} {cy-size*0.1})"/>'
        return s
    if dir_ == 'right':
        s = f'<ellipse cx="{cx}" cy="{cy}" rx="{size}" ry="{size*0.85}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
        for i, off in enumerate([-size*0.55, -size*0.2, size*0.15, size*0.5]):
            fl = size * (0.85 if i in (1,2) else 0.7)
            s += f'<rect x="{cx+size*0.5}" y="{cy+off-1.5}" width="{fl}" height="3" rx="1.5" fill="{SK}" stroke="{INK}" stroke-width="1"/>'
        s += f'<ellipse cx="{cx-size*0.1}" cy="{cy+size*0.85}" rx="{size*0.4}" ry="2" fill="{SK}" stroke="{INK}" stroke-width="1" transform="rotate(-30 {cx-size*0.1} {cy+size*0.85})"/>'
        return s
    # left
    s = f'<ellipse cx="{cx}" cy="{cy}" rx="{size}" ry="{size*0.85}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
    for i, off in enumerate([-size*0.55, -size*0.2, size*0.15, size*0.5]):
        fl = size * (0.85 if i in (1,2) else 0.7)
        s += f'<rect x="{cx-size*0.5-fl}" y="{cy+off-1.5}" width="{fl}" height="3" rx="1.5" fill="{SK}" stroke="{INK}" stroke-width="1"/>'
    s += f'<ellipse cx="{cx+size*0.1}" cy="{cy+size*0.85}" rx="{size*0.4}" ry="2" fill="{SK}" stroke="{INK}" stroke-width="1" transform="rotate(30 {cx+size*0.1} {cy+size*0.85})"/>'
    return s

def _fist(cx, cy, dir_='right', size=9):
    """Faust mit Knöcheln."""
    s = f'<rect x="{cx-size}" y="{cy-size*0.8}" width="{size*2}" height="{size*1.6}" rx="{size*0.5}" fill="{SK}" stroke="{INK}" stroke-width="1.5"/>'
    # Knöchel-Linien
    if dir_ in ('left', 'right'):
        for off in [-size*0.4, 0, size*0.4]:
            s += f'<line x1="{cx-size*0.7}" y1="{cy+off*0.5}" x2="{cx+size*0.7}" y2="{cy+off*0.5}" stroke="{INK}" stroke-width="0.7" opacity="0.55"/>'
        # Daumen
        if dir_ == 'right':
            s += f'<path d="M{cx-size*0.4},{cy-size*0.8} Q{cx-size*0.9},{cy-size*0.4} {cx-size*0.5},{cy}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
        else:
            s += f'<path d="M{cx+size*0.4},{cy-size*0.8} Q{cx+size*0.9},{cy-size*0.4} {cx+size*0.5},{cy}" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
    else:
        for off in [-size*0.4, 0, size*0.4]:
            s += f'<line x1="{cx+off*0.5}" y1="{cy-size*0.6}" x2="{cx+off*0.5}" y2="{cy+size*0.6}" stroke="{INK}" stroke-width="0.7" opacity="0.55"/>'
    return s

def _palm_belly(cx, cy):
    """Dhyana-Mudra: gefaltete Hände auf dem Schoß."""
    s = f'<ellipse cx="{cx}" cy="{cy}" rx="24" ry="9" fill="{SK}" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<path d="M{cx-22},{cy-1} Q{cx},{cy-6} {cx+22},{cy-1}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.55"/>'
    s += f'<line x1="{cx-4}" y1="{cy-5}" x2="{cx-4}" y2="{cy+5}" stroke="{INK}" stroke-width="0.8" opacity="0.45"/>'
    s += f'<line x1="{cx+4}" y1="{cy-5}" x2="{cx+4}" y2="{cy+5}" stroke="{INK}" stroke-width="0.8" opacity="0.45"/>'
    s += f'<ellipse cx="{cx}" cy="{cy-2}" rx="6" ry="2.5" fill="{SD}" opacity="0.5"/>'
    return s

def _gassho(cx, cy):
    """Anjali-Mudra: zusammengelegte Handflächen."""
    s = f'<path d="M{cx-2},{cy+10} Q{cx-8},{cy} {cx-5},{cy-22} Q{cx-3},{cy-30} {cx},{cy-30} Q{cx+3},{cy-30} {cx+5},{cy-22} Q{cx+8},{cy} {cx+2},{cy+10} Z" fill="{SK}" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<line x1="{cx}" y1="{cy-26}" x2="{cx}" y2="{cy+6}" stroke="{INK}" stroke-width="0.8" opacity="0.45"/>'
    s += f'<path d="M{cx-4},{cy-15} L{cx-4},{cy+4}" stroke="{INK}" stroke-width="0.6" opacity="0.4"/>'
    s += f'<path d="M{cx+4},{cy-15} L{cx+4},{cy+4}" stroke="{INK}" stroke-width="0.6" opacity="0.4"/>'
    return s

def _crown_arrow(cx, top_y):
    """Pfeil über dem Kopf nach oben — Baihui-Ausrichtung."""
    return (
        f'<line x1="{cx}" y1="{top_y}" x2="{cx}" y2="{top_y-12}" stroke="{RED}" stroke-width="1.4"/>'
        f'<path d="M{cx-5},{top_y-7} L{cx},{top_y-13} L{cx+5},{top_y-7}" fill="none" stroke="{RED}" stroke-width="1.4"/>'
        f'<text x="{cx+8}" y="{top_y-8}" font-family="Georgia,serif" font-size="7pt" fill="{RED}" font-style="italic">Baihui</text>'
    )

def _dantian_dot(cx, cy):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="9" fill="none" stroke="{GOLD}" stroke-width="1" stroke-dasharray="2,2" opacity="0.65"/>'
        f'<circle cx="{cx}" cy="{cy}" r="3" fill="{GOLD}" opacity="0.7"/>'
        f'<text x="{cx+14}" y="{cy+3}" font-family="Georgia,serif" font-size="7pt" fill="{RED}" font-style="italic">Dan Tian</text>'
    )

# ═══ FIGUREN ════════════════════════════════════════════════════════════════

def fig_wuji():
    """Wuji-Stand — natürlicher Grundstand, frontal."""
    cx = 90
    b = _ground(cx, 290, 60)
    b += _leg(cx-12, 174, cx-14, 230, cx-16, 288)
    b += _leg(cx+12, 174, cx+14, 230, cx+16, 288)
    b += _foot(cx-16, 290, 'front')
    b += _foot(cx+16, 290, 'front')
    b += _hip_pants(cx, 168, 24, 8)
    b += _torso(cx, 90, 38, 30, 80)
    # Arme hängen seitlich, leicht vor dem Körper
    b += _arm(cx-38, 94, cx-44, 130, cx-34, 168, side='l')
    b += _arm(cx+38, 94, cx+44, 130, cx+34, 168, side='r')
    b += _hand_open(cx-34, 174, 'down')
    b += _hand_open(cx+34, 174, 'down')
    b += _neck(cx, 80, 7, 10)
    b += _head(cx, 64, 14)
    b += _crown_arrow(cx, 48)
    b += _dantian_dot(cx, 138)
    return _svg(200, 310, b)

def fig_baum():
    """Den Baum halten."""
    cx = 130
    b = _ground(cx, 290, 70)
    b += _leg(cx-14, 174, cx-16, 230, cx-20, 288)
    b += _leg(cx+14, 174, cx+16, 230, cx+20, 288)
    b += _foot(cx-20, 290, 'front'); b += _foot(cx+20, 290, 'front')
    b += _hip_pants(cx, 168, 26, 8)
    b += _torso(cx, 90, 40, 32, 80)
    # Arme: aufgerundete Umarmung
    b += _arm(cx-40, 94, cx-78, 130, cx-46, 154, side='l')
    b += _arm(cx+40, 94, cx+78, 130, cx+46, 154, side='r')
    b += _hand_open(cx-44, 160, 'right')
    b += _hand_open(cx+44, 160, 'left')
    b += _neck(cx, 80, 7, 10); b += _head(cx, 64, 14)
    b += _crown_arrow(cx, 48)
    # Qi-Kreis
    b += f'<ellipse cx="{cx}" cy="148" rx="46" ry="22" fill="none" stroke="{RED}" stroke-width="1" stroke-dasharray="3,2" opacity="0.5"/>'
    b += f'<circle cx="{cx}" cy="148" r="3" fill="{RED}" opacity="0.5"/>'
    b += _label(cx+88, 150, "Qi-Ball")
    b += _label(cx-58, 110, "Achseln offen", "end", 7)
    return _svg(260, 310, b)

def fig_mabu():
    """Ma Bu — Reiterhaltung, frontal, tief."""
    cx = 150
    b = _ground(cx, 288, 130)
    b += _leg(cx-22, 174, cx-60, 222, cx-92, 288, thick=14)
    b += _leg(cx+22, 174, cx+60, 222, cx+92, 288, thick=14)
    b += _foot(cx-92, 290, 'side'); b += _foot(cx+92, 290, 'side')
    b += _hip_pants(cx, 166, 34, 10)
    b += _torso(cx, 88, 42, 36, 78)
    b += _arm(cx-42, 92, cx-36, 132, cx-18, 168, side='l')
    b += _arm(cx+42, 92, cx+36, 132, cx+18, 168, side='r')
    # Fäuste an die Hüfte
    b += _fist(cx-16, 170, 'right'); b += _fist(cx+16, 170, 'left')
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14, 'fierce')
    b += _crown_arrow(cx, 46)
    # Dan Tian rechts neben dem Körper
    b += f'<circle cx="{cx+58}" cy="140" r="3" fill="{GOLD}"/>'
    b += f'<line x1="{cx+50}" y1="140" x2="{cx+30}" y2="140" stroke="{GOLD}" stroke-width="0.7" opacity="0.6"/>'
    b += _label(cx+62, 143, "Dan Tian", "start", 7)
    # Schenkellinien-Indikator
    b += f'<line x1="{cx-100}" y1="222" x2="{cx-66}" y2="222" stroke="{RED}" stroke-width="0.8" stroke-dasharray="2,2" opacity="0.65"/>'
    b += f'<line x1="{cx+66}" y1="222" x2="{cx+100}" y2="222" stroke="{RED}" stroke-width="0.8" stroke-dasharray="2,2" opacity="0.65"/>'
    b += _label(cx-100, 216, "Oberschenkel parallel", "start", 7)
    b += _label(cx, 306, "2 Schulterbreiten", "middle", 7)
    return _svg(310, 314, b)

def fig_gongbu():
    """Gong Bu — Bogenstand, seitlich."""
    cx = 150
    b = _ground(cx, 288, 130)
    # Vorderes Bein gebeugt (rechts), hinteres gestreckt (links)
    b += _leg(cx+14, 174, cx+62, 220, cx+86, 288, thick=14)  # vorne
    b += _leg(cx-14, 174, cx-46, 240, cx-94, 286, thick=12)  # hinten gestreckt
    b += _foot(cx+86, 290, 'side'); b += _foot(cx-94, 288, 'side')
    b += _hip_pants(cx, 166, 32, 10)
    b += _torso(cx, 88, 42, 36, 78)
    b += _arm_straight(cx-42, 92, cx-90, 102)
    b += _fist(cx-95, 102, 'right')
    b += _arm(cx+42, 92, cx+44, 130, cx+22, 168, side='r')
    b += _fist(cx+22, 170, 'left')
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14, 'fierce')
    b += _crown_arrow(cx, 46)
    b += _label(cx-100, 304, "Hintere Ferse am Boden", "start", 7)
    b += _label(cx+86, 304, "Knie über Fuß", "middle", 7)
    return _svg(310, 314, b)

def fig_xubu():
    """Xu Bu — leerer Stand."""
    cx = 150
    b = _ground(cx, 288, 110)
    b += _leg(cx-6, 174, cx-30, 224, cx-58, 286, thick=13)  # hinten tragend
    b += _leg(cx+6, 174, cx+30, 240, cx+62, 280, thick=11)  # vorne leer (Fußballen)
    b += _foot(cx-58, 288, 'side')
    # Fußspitze vorn
    b += f'<path d="M{cx+58},280 L{cx+72},282 L{cx+70},286 Z" fill="{INK}" opacity="0.85"/>'
    b += _hip_pants(cx, 166, 32, 10)
    b += _torso(cx, 88, 42, 36, 78)
    b += _arm(cx-42, 92, cx-58, 130, cx-46, 170, side='l')
    b += _arm(cx+42, 92, cx+58, 130, cx+46, 170, side='r')
    b += _hand_open(cx-50, 174, 'down'); b += _hand_open(cx+50, 174, 'down')
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14)
    b += _crown_arrow(cx, 46)
    b += _label(cx-58, 304, "90 % Gewicht", "middle", 7)
    b += _label(cx+62, 296, "nur Ballen", "middle", 7)
    return _svg(310, 312, b)

def fig_pubu():
    """Pu Bu — geduckter Stand, sehr tief."""
    cx = 150
    b = _ground(cx, 290, 140)
    # Linkes Bein gestreckt seitlich, rechtes Bein tief gebeugt
    b += _leg(cx-10, 200, cx-58, 240, cx-110, 288, thick=12)
    b += _leg(cx+10, 200, cx+38, 250, cx+30, 288, thick=14)
    b += _foot(cx-110, 290, 'side'); b += _foot(cx+30, 290, 'front')
    b += _hip_pants(cx, 192, 28, 10)
    b += _torso(cx, 116, 38, 32, 78)
    b += _arm_straight(cx-38, 120, cx-100, 198)  # Hand zieht zum Fuß
    b += _hand_open(cx-104, 200, 'right')
    b += _arm(cx+38, 120, cx+44, 158, cx+38, 196, side='r')
    b += _fist(cx+38, 198, 'left')
    b += _neck(cx, 106, 7, 10); b += _head(cx, 90, 14, 'fierce')
    b += _label(cx-110, 306, "Bein flach am Boden", "middle", 7)
    b += _label(cx+30, 306, "Stützbein", "middle", 7)
    return _svg(310, 320, b)

def fig_xiebu():
    """Xie Bu — Kreuzstand."""
    cx = 150
    b = _ground(cx, 290, 100)
    # Beine überkreuzt: vorderes Bein links, hinteres Knie sinkt hinter rechtem Fuß
    b += _leg(cx-8, 180, cx-20, 240, cx-30, 288, thick=13)
    b += _leg(cx+8, 180, cx+8, 250, cx-12, 286, thick=12)
    b += _foot(cx-30, 290, 'side')
    b += f'<ellipse cx="{cx-12}" cy="286" rx="7" ry="3" fill="{INK}" opacity="0.85"/>'
    b += _hip_pants(cx, 172, 28, 10)
    b += _torso(cx, 94, 40, 34, 80)
    b += _arm(cx-40, 98, cx-60, 138, cx-40, 174, side='l')
    b += _fist(cx-40, 176, 'right')
    b += _arm(cx+40, 98, cx+60, 138, cx+40, 174, side='r')
    b += _fist(cx+40, 176, 'left')
    b += _neck(cx, 84, 7, 10); b += _head(cx, 68, 14, 'fierce')
    b += _label(cx, 306, "Beine kreuzen sich", "middle", 7)
    return _svg(310, 314, b)

def fig_chongquan():
    """Chong Quan — gerader Faustschlag aus Ma Bu, seitlich."""
    cx = 170
    b = _ground(cx, 290, 130)
    b += _leg(cx-22, 174, cx-60, 222, cx-92, 288, thick=14)
    b += _leg(cx+22, 174, cx+60, 222, cx+92, 288, thick=14)
    b += _foot(cx-92, 290, 'side'); b += _foot(cx+92, 290, 'side')
    b += _hip_pants(cx, 166, 34, 10)
    b += _torso(cx, 88, 42, 36, 78)
    # Linke Faust ausgestreckt nach vorne (rechts)
    b += _arm_straight(cx+42, 96, cx+118, 110)
    b += _fist(cx+125, 110, 'left')
    # Rechte Faust an der Hüfte
    b += _arm(cx-42, 96, cx-30, 130, cx-12, 168, side='l')
    b += _fist(cx-10, 170, 'right')
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14, 'fierce')
    # Bewegungsstreifen
    b += f'<line x1="{cx+60}" y1="110" x2="{cx+100}" y2="110" stroke="{RED}" stroke-width="1" opacity="0.45"/>'
    b += f'<line x1="{cx+60}" y1="114" x2="{cx+100}" y2="114" stroke="{RED}" stroke-width="0.7" opacity="0.3"/>'
    b += _label(cx+90, 96, "Chong Quan", "middle", 8)
    b += _label(cx-12, 158, "Hüftfaust", "middle", 7)
    return _svg(340, 310, b)

def fig_piquan():
    """Pi Quan — Hackschlag."""
    cx = 150
    b = _ground(cx, 290, 130)
    b += _leg(cx-22, 174, cx-60, 222, cx-92, 288, thick=14)
    b += _leg(cx+22, 174, cx+60, 222, cx+92, 288, thick=14)
    b += _foot(cx-92, 290, 'side'); b += _foot(cx+92, 290, 'side')
    b += _hip_pants(cx, 166, 34, 10)
    b += _torso(cx, 88, 42, 36, 78)
    # Linker Arm hoch über dem Kopf, dann hackt nach unten (Zwischenposition: Arm zeigt schräg vorne unten)
    b += _arm_straight(cx+38, 96, cx+92, 152)
    b += _fist(cx+96, 156, 'left')
    b += _arm(cx-42, 96, cx-30, 130, cx-12, 168, side='l')
    b += _fist(cx-10, 170, 'right')
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14, 'fierce')
    # Bewegungsbogen
    b += f'<path d="M{cx+50},60 Q{cx+90},90 {cx+96},150" fill="none" stroke="{RED}" stroke-width="1" stroke-dasharray="3,2" opacity="0.55"/>'
    b += _label(cx+80, 56, "Bahn von oben", "middle", 7)
    return _svg(310, 310, b)

def fig_tantui():
    """Tan Tui — Federtritt, Seitansicht."""
    cx = 130
    b = _ground(cx, 290, 110)
    # Standbein
    b += _leg(cx-8, 174, cx-10, 230, cx-12, 288, thick=14)
    b += _foot(cx-12, 290, 'side')
    # Trittbein — schnellt nach vorne (rechts)
    b += _leg(cx+8, 174, cx+50, 200, cx+118, 198, thick=14)
    b += f'<ellipse cx="{cx+125}" cy="200" rx="10" ry="3.5" fill="{INK}" opacity="0.85"/>'
    b += _hip_pants(cx, 166, 28, 10)
    b += _torso(cx, 88, 40, 32, 78)
    b += _arm(cx-40, 92, cx-50, 130, cx-36, 168, side='l')
    b += _fist(cx-34, 170, 'right')
    b += _arm(cx+38, 92, cx+30, 130, cx+10, 168, side='r')
    b += _fist(cx+10, 170, 'left')
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14, 'fierce')
    # Trittbahn-Marker
    b += f'<path d="M{cx+30},230 Q{cx+80},218 {cx+118},202" fill="none" stroke="{RED}" stroke-width="1" stroke-dasharray="3,2" opacity="0.6"/>'
    b += _label(cx+95, 220, "schnellt aus dem Knie", "middle", 7)
    return _svg(310, 310, b)

def fig_cechuai():
    """Ce Chuai — Seittritt."""
    cx = 130
    b = _ground(cx, 290, 110)
    b += _leg(cx-4, 174, cx-8, 228, cx-12, 288, thick=14)
    b += _foot(cx-12, 290, 'side')
    # Seitlicher Tritt nach rechts mit Fußaußenkante
    b += _leg(cx+8, 174, cx+50, 184, cx+118, 188, thick=14)
    b += f'<ellipse cx="{cx+125}" cy="190" rx="10" ry="4" fill="{INK}" opacity="0.85"/>'
    b += f'<line x1="{cx+115}" y1="186" x2="{cx+128}" y2="186" stroke="{RED}" stroke-width="2"/>'
    b += _hip_pants(cx, 166, 28, 10)
    b += _torso(cx, 88, 40, 32, 78)
    b += _arm(cx-40, 92, cx-50, 130, cx-36, 168, side='l'); b += _fist(cx-34, 170, 'right')
    b += _arm(cx+38, 92, cx+50, 110, cx+62, 142, side='r'); b += _fist(cx+64, 144, 'left')
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14, 'fierce')
    b += _label(cx+115, 178, "Fußaußenkante", "middle", 7)
    return _svg(310, 310, b)

def fig_squat():
    """Squatting Monkey — tiefe Hocke."""
    cx = 110
    b = _ground(cx, 248, 90)
    b += _leg(cx-14, 168, cx-44, 200, cx-52, 246, thick=14)
    b += _leg(cx+14, 168, cx+44, 200, cx+52, 246, thick=14)
    b += _foot(cx-52, 248, 'front'); b += _foot(cx+52, 248, 'front')
    b += _hip_pants(cx, 160, 28, 10)
    b += _torso(cx, 76, 40, 32, 80)
    b += _arm(cx-38, 80, cx-22, 110, cx, 134, side='l')
    b += _arm(cx+38, 80, cx+22, 110, cx, 134, side='r')
    b += _hand_open(cx, 138, 'up', 7)
    b += _neck(cx, 66, 7, 10); b += _head(cx, 50, 14)
    b += _label(cx, 36, "Atem ruhig", "middle", 7)
    return _svg(220, 268, b)

def fig_zazen(annotate=True, cover=False):
    """Zazen — Sitzmeditation; mit oder ohne Beschriftungspunkte."""
    if cover:
        # Großes Cover-Format auf Schwarz: helle Linien
        cx = 200
        scol = "#D9B488"; rcol = "#6B4424"; lcol = "#f5f0e6"
        ground_op = "0.0"
        # Sitzfläche
        b = f'<ellipse cx="{cx}" cy="384" rx="140" ry="12" fill="{lcol}" opacity="0.04"/>'
        b += f'<path d="M{cx-138},370 Q{cx-110},310 {cx-44},296 Q{cx},290 {cx+44},296 Q{cx+110},310 {cx+138},370 Z" fill="{rcol}" stroke="{lcol}" stroke-width="2"/>'
        b += f'<path d="M{cx-76},320 Q{cx},310 {cx+76},320" fill="none" stroke="{lcol}" stroke-width="1.4" opacity="0.4"/>'
        # Torso
        b += f'<path d="M{cx-48},212 L{cx-70},298 L{cx+70},298 L{cx+48},212 Z" fill="{rcol}" stroke="{lcol}" stroke-width="2"/>'
        b += f'<line x1="{cx-18}" y1="220" x2="{cx-22}" y2="294" stroke="{lcol}" stroke-width="0.7" opacity="0.35"/>'
        b += f'<line x1="{cx+18}" y1="220" x2="{cx+22}" y2="294" stroke="{lcol}" stroke-width="0.7" opacity="0.35"/>'
        # Kragen
        b += f'<path d="M{cx-38},212 Q{cx},222 {cx+38},212" fill="none" stroke="{lcol}" stroke-width="1.6" opacity="0.6"/>'
        b += f'<path d="M{cx-9},214 L{cx},228 L{cx+9},214" fill="{scol}" stroke="{lcol}" stroke-width="1.2"/>'
        # Mudra
        b += f'<ellipse cx="{cx}" cy="275" rx="34" ry="13" fill="{scol}" stroke="{lcol}" stroke-width="1.6"/>'
        b += f'<ellipse cx="{cx}" cy="272" rx="9" ry="3.5" fill="{rcol}" opacity="0.6"/>'
        # Arme
        b += f'<path d="M{cx-54},220 Q{cx-66},250 {cx-32},272" fill="none" stroke="{rcol}" stroke-width="11" stroke-linecap="round"/>'
        b += f'<path d="M{cx-54},220 Q{cx-66},250 {cx-32},272" fill="none" stroke="{lcol}" stroke-width="1.6" stroke-linecap="round"/>'
        b += f'<path d="M{cx+54},220 Q{cx+66},250 {cx+32},272" fill="none" stroke="{rcol}" stroke-width="11" stroke-linecap="round"/>'
        b += f'<path d="M{cx+54},220 Q{cx+66},250 {cx+32},272" fill="none" stroke="{lcol}" stroke-width="1.6" stroke-linecap="round"/>'
        # Hals + Kopf (heller)
        b += f'<path d="M{cx-10},200 Q{cx-9},212 {cx-9.5},212 L{cx+9.5},212 Q{cx+9},212 {cx+10},200 Z" fill="{scol}" stroke="{lcol}" stroke-width="1.4"/>'
        r = 24
        b += f'<path d="M{cx-r*0.85},{180-r*0.4} Q{cx-r},{180-r*0.85} {cx-r*0.55},{180-r} Q{cx},{180-r*1.15} {cx+r*0.55},{180-r} Q{cx+r},{180-r*0.85} {cx+r*0.85},{180-r*0.4} Q{cx+r*0.95},{180+r*0.25} {cx+r*0.7},{180+r*0.7} Q{cx+r*0.35},{180+r*1.05} {cx},{180+r*1.05} Q{cx-r*0.35},{180+r*1.05} {cx-r*0.7},{180+r*0.7} Q{cx-r*0.95},{180+r*0.25} {cx-r*0.85},{180-r*0.4} Z" fill="{scol}" stroke="{lcol}" stroke-width="1.6"/>'
        b += f'<path d="M{cx-r*0.55},{180-r*0.9} Q{cx},{180-r*1.12} {cx+r*0.55},{180-r*0.9} Q{cx+r*0.3},{180-r*0.4} {cx},{180-r*0.5} Q{cx-r*0.3},{180-r*0.4} {cx-r*0.55},{180-r*0.9}" fill="{rcol}" opacity="0.35"/>'
        b += f'<path d="M{cx-r*0.95},{180-r*0.1} Q{cx-r*1.15},{180} {cx-r*0.95},{180+r*0.3}" fill="{scol}" stroke="{lcol}" stroke-width="1.3"/>'
        b += f'<path d="M{cx+r*0.95},{180-r*0.1} Q{cx+r*1.15},{180} {cx+r*0.95},{180+r*0.3}" fill="{scol}" stroke="{lcol}" stroke-width="1.3"/>'
        b += f'<path d="M{cx-r*0.45},{180-r*0.1} q{r*0.18},{r*0.08} {r*0.32},0" fill="none" stroke="{lcol}" stroke-width="1.4"/>'
        b += f'<path d="M{cx+r*0.13},{180-r*0.1} q{r*0.18},{r*0.08} {r*0.32},0" fill="none" stroke="{lcol}" stroke-width="1.4"/>'
        b += f'<path d="M{cx-r*0.2},{180+r*0.55} Q{cx},{180+r*0.62} {cx+r*0.2},{180+r*0.55}" fill="none" stroke="{lcol}" stroke-width="1.2" opacity="0.75"/>'
        # Halo
        b += f'<circle cx="{cx}" cy="180" r="62" fill="none" stroke="{lcol}" stroke-width="0.6" opacity="0.18"/>'
        return _svg(400, 400, b)

    cx = 140
    b = f'<ellipse cx="{cx}" cy="266" rx="92" ry="9" fill="{INK}" opacity="0.08"/>'
    b += f'<path d="M{cx-90},256 Q{cx-70},220 {cx-30},210 Q{cx},204 {cx+30},210 Q{cx+70},220 {cx+90},256 Z" fill="{ROBE}" stroke="{INK}" stroke-width="2"/>'
    b += f'<path d="M{cx-50},226 Q{cx},218 {cx+50},226" fill="none" stroke="{ROBE2}" stroke-width="1.4"/>'
    b += f'<path d="M{cx-32},150 L{cx-46},212 L{cx+46},212 L{cx+32},150 Z" fill="{ROBE}" stroke="{INK}" stroke-width="2"/>'
    b += f'<line x1="{cx-12}" y1="156" x2="{cx-16}" y2="208" stroke="{INK}" stroke-width="0.7" opacity="0.35"/>'
    b += f'<line x1="{cx+12}" y1="156" x2="{cx+16}" y2="208" stroke="{INK}" stroke-width="0.7" opacity="0.35"/>'
    b += f'<path d="M{cx-26},150 Q{cx},158 {cx+26},150" fill="none" stroke="{ROBE2}" stroke-width="1.6"/>'
    b += f'<path d="M{cx-6},152 L{cx},162 L{cx+6},152" fill="{SK}" stroke="{INK}" stroke-width="1.2"/>'
    b += _palm_belly(cx, 195)
    b += _arm(cx-36, 156, cx-46, 178, cx-22, 195, side='l')
    b += _arm(cx+36, 156, cx+46, 178, cx+22, 195, side='r')
    b += _neck(cx, 142, 7, 8); b += _head(cx, 124, 16, 'meditative')
    if annotate:
        pts = [(34, 124, "1", "Baihui"), (246, 124, "2", "Augen halb"),
               (28, 162, "3", "Schultern"), (252, 162, "4", "Wirbelsäule"),
               (cx, 195, "5", "Mudra"), (cx, 256, "6", "Lotus")]
        for x, y, n, lbl in pts:
            b += f'<circle cx="{x}" cy="{y}" r="9" fill="{RED}"/>'
            b += f'<text x="{x}" y="{y+3}" text-anchor="middle" font-size="8pt" fill="white" font-family="Georgia,serif" font-weight="bold">{n}</text>'
            if x < 140:
                b += _label(x-12, y+2, lbl, "end", 7.5)
            elif x > 140:
                b += _label(x+12, y+2, lbl, "start", 7.5)
            else:
                b += _label(x, y+24 if n=="5" else y+22, lbl, "middle", 7.5)
    return _svg(290, 280, b)

def fig_kinhin():
    """Kinhin — Gehmeditation, halbprofil."""
    cx = 130
    b = _ground(cx, 290, 65)
    b += _leg(cx-8, 178, cx-16, 230, cx-20, 286, thick=13)
    b += _leg(cx+8, 178, cx+18, 232, cx+26, 286, thick=13)
    b += _foot(cx-20, 290, 'side'); b += _foot(cx+26, 290, 'side')
    b += _hip_pants(cx, 170, 24, 10)
    b += _torso(cx, 96, 36, 30, 75)
    b += _arm(cx-32, 100, cx-22, 130, cx-2, 158, side='l')
    b += _arm(cx+32, 100, cx+22, 130, cx+2, 158, side='r')
    b += _gassho(cx, 162)
    b += _neck(cx, 86, 7, 10); b += _head(cx, 70, 14, 'meditative')
    b += _label(cx-32, 156, "Gassho", "end", 7)
    b += _label(cx-50, 280, "halber Schritt", "middle", 7)
    return _svg(240, 310, b)

def fig_weituo():
    """Wei Tuo — Yi Jin Jing 1: Hände vor der Brust."""
    cx = 110
    b = _ground(cx, 308, 55)
    b += _leg(cx-12, 196, cx-12, 250, cx-14, 306, thick=13)
    b += _leg(cx+12, 196, cx+12, 250, cx+14, 306, thick=13)
    b += _foot(cx-14, 308, 'front'); b += _foot(cx+14, 308, 'front')
    b += _hip_pants(cx, 190, 26, 8)
    b += _torso(cx, 112, 38, 32, 80)
    # Beide Hände vor der Brust gefaltet
    b += _arm(cx-36, 118, cx-32, 138, cx-6, 152, side='l')
    b += _arm(cx+36, 118, cx+32, 138, cx+6, 152, side='r')
    # Vor der Brust gefaltete Hände — horizontal
    b += f'<path d="M{cx-22},148 Q{cx-26},155 {cx-22},162 L{cx+22},162 Q{cx+26},155 {cx+22},148 Z" fill="{SK}" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<line x1="{cx}" y1="148" x2="{cx}" y2="162" stroke="{INK}" stroke-width="0.8" opacity="0.55"/>'
    b += _neck(cx, 102, 7, 10); b += _head(cx, 86, 14, 'meditative')
    b += _crown_arrow(cx, 70)
    b += _label(cx-50, 158, "Hände gefaltet", "end", 7)
    return _svg(220, 320, b)

def fig_bogen():
    """Bogen spannen — Ba Duan Jin #2, Ma Bu mit Bogen."""
    cx = 165
    b = _ground(cx, 288, 130)
    b += _leg(cx-22, 174, cx-60, 222, cx-92, 288, thick=14)
    b += _leg(cx+22, 174, cx+60, 222, cx+92, 288, thick=14)
    b += _foot(cx-92, 290, 'side'); b += _foot(cx+92, 290, 'side')
    b += _hip_pants(cx, 166, 34, 10)
    b += _torso(cx, 88, 42, 36, 78)
    # Linke Hand: Zeigefinger ausgestreckt zur Seite
    b += _arm_straight(cx-42, 96, cx-100, 100)
    b += f'<ellipse cx="{cx-110}" cy="100" rx="8" ry="6" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
    b += f'<line x1="{cx-118}" y1="100" x2="{cx-132}" y2="98" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<line x1="{cx-118}" y1="103" x2="{cx-130}" y2="106" stroke="{INK}" stroke-width="0.8"/>'
    # Rechte Hand: zieht den Bogen nach rechts
    b += _arm(cx+42, 96, cx+62, 110, cx+78, 100, side='r')
    b += _fist(cx+86, 100, 'left')
    # Bogen
    b += f'<path d="M{cx-108},80 Q{cx-130},108 {cx-108},132" fill="none" stroke="{GOLD}" stroke-width="3"/>'
    b += f'<line x1="{cx-108}" y1="80" x2="{cx-108}" y2="132" stroke="{INK}" stroke-width="0.7" stroke-dasharray="2,2" opacity="0.5"/>'
    b += f'<line x1="{cx-108}" y1="106" x2="{cx+86}" y2="106" stroke="{INK}" stroke-width="0.8" opacity="0.5"/>'
    b += _neck(cx, 78, 7, 10); b += _head(cx, 62, 14, 'fierce')
    b += _label(cx-128, 70, "Zeigefinger fixiert", "middle", 7)
    b += _label(cx+92, 88, "Faust zieht", "middle", 7)
    return _svg(330, 310, b)

# ───── Vier Kernübungen ─────────────────────────────────────────────────────

def fig_fist_pose():
    """Fäuste an der Seite, Spannung im Unterarm."""
    cx = 100
    b = _ground(cx, 290, 60)
    b += _leg(cx-12, 174, cx-14, 230, cx-16, 288)
    b += _leg(cx+12, 174, cx+14, 230, cx+16, 288)
    b += _foot(cx-16, 290, 'front'); b += _foot(cx+16, 290, 'front')
    b += _hip_pants(cx, 168, 24, 8)
    b += _torso(cx, 90, 38, 30, 80)
    b += _arm(cx-38, 94, cx-44, 130, cx-32, 170, side='l')
    b += _arm(cx+38, 94, cx+44, 130, cx+32, 170, side='r')
    b += _fist(cx-32, 178, 'right', 10)
    b += _fist(cx+32, 178, 'left', 10)
    b += _neck(cx, 80, 7, 10); b += _head(cx, 64, 14, 'fierce')
    b += _crown_arrow(cx, 48)
    # Spannungswellen
    b += f'<path d="M{cx-50},150 Q{cx-58},155 {cx-50},160" fill="none" stroke="{RED}" stroke-width="1.2" opacity="0.7"/>'
    b += f'<path d="M{cx+50},150 Q{cx+58},155 {cx+50},160" fill="none" stroke="{RED}" stroke-width="1.2" opacity="0.7"/>'
    b += _label(cx-46, 192, "fest", "middle", 7)
    b += _label(cx+46, 192, "fest", "middle", 7)
    return _svg(220, 310, b)

def fig_lbend_pose():
    """L-Stand: Hüftbeuge 90°, Arme hängen — Seitansicht."""
    cx = 200
    b = _ground(cx, 290, 80)
    # Beine stehend
    b += _leg(cx-4, 200, cx-6, 240, cx-8, 288, thick=13)
    b += _leg(cx+4, 200, cx+6, 240, cx+8, 288, thick=13)
    b += _foot(cx-8, 290, 'side'); b += _foot(cx+8, 290, 'side')
    b += _hip_pants(cx, 194, 24, 8)
    # Torso horizontal: drehe Trapez 90°
    # Schultern bei (cx-90, 194), Hüfte bei (cx-8, 194) → horizontal Trapez
    b += f'<path d="M{cx-90},178 L{cx-90},206 L{cx-10},196 L{cx-10},192 Z" fill="{ROBE}" stroke="{INK}" stroke-width="2"/>'
    b += f'<line x1="{cx-78}" y1="184" x2="{cx-22}" y2="190" stroke="{INK}" stroke-width="0.7" opacity="0.4"/>'
    b += f'<line x1="{cx-78}" y1="200" x2="{cx-22}" y2="196" stroke="{INK}" stroke-width="0.7" opacity="0.4"/>'
    # Hals horizontal nach links
    b += f'<path d="M{cx-90},186 Q{cx-96},192 {cx-90},198 Z" fill="{SK}" stroke="{INK}" stroke-width="1.4"/>'
    # Kopf hängt nach unten-links
    b += _head(cx-104, 210, 13, 'neutral')
    # Arme hängen senkrecht nach unten
    b += _arm_straight(cx-86, 184, cx-92, 240)
    b += _hand_open(cx-92, 246, 'down', 7)
    b += _arm_straight(cx-78, 200, cx-72, 244)
    b += _hand_open(cx-72, 250, 'down', 7)
    # Schüttellinien
    b += f'<path d="M{cx-104},256 Q{cx-98},260 {cx-92},256 Q{cx-86},260 {cx-80},256" fill="none" stroke="{RED}" stroke-width="1.3"/>'
    b += f'<path d="M{cx-104},262 Q{cx-98},266 {cx-92},262" fill="none" stroke="{RED}" stroke-width="1" opacity="0.6"/>'
    # 90° Marker
    b += f'<path d="M{cx-22},202 L{cx-22},196 L{cx-16},196" fill="none" stroke="{RED}" stroke-width="1.1"/>'
    b += _label(cx-30, 215, "90°", "middle", 7)
    b += _label(cx-100, 232, "Arme schwer", "middle", 7)
    b += _label(cx-90, 282, "schütteln", "middle", 7)
    b += _label(cx+8, 308, "Standfüße hüftbreit", "middle", 7)
    return _svg(310, 320, b)

def fig_sidearms_pose():
    """Beide Arme zur Seite gestreckt, offene Hände — frontal."""
    cx = 180
    b = _ground(cx, 290, 70)
    b += _leg(cx-12, 174, cx-14, 230, cx-16, 288)
    b += _leg(cx+12, 174, cx+14, 230, cx+16, 288)
    b += _foot(cx-16, 290, 'front'); b += _foot(cx+16, 290, 'front')
    b += _hip_pants(cx, 168, 24, 8)
    b += _torso(cx, 90, 38, 30, 80)
    # Arme horizontal zur Seite
    b += _arm_straight(cx-38, 94, cx-138, 94)
    b += _arm_straight(cx+38, 94, cx+138, 94)
    # Offene Hände zur Seite — mit Mittelfinger-Highlight
    b += _hand_open(cx-148, 94, 'left', 9)
    b += _hand_open(cx+148, 94, 'right', 9)
    # Mittelfinger als rote Markierung über die offene Hand
    b += f'<line x1="{cx-153}" y1="94" x2="{cx-168}" y2="94" stroke="{RED}" stroke-width="2.2"/>'
    b += f'<line x1="{cx+153}" y1="94" x2="{cx+168}" y2="94" stroke="{RED}" stroke-width="2.2"/>'
    # Zugpfeile
    b += _arrow(cx-160, 78, cx-180, 78, RED, 1.4)
    b += _arrow(cx+160, 78, cx+180, 78, RED, 1.4)
    b += _neck(cx, 80, 7, 10); b += _head(cx, 64, 14, 'meditative')
    b += _crown_arrow(cx, 48)
    # Schulter senken Indikator
    b += f'<path d="M{cx-44},78 Q{cx-50},86 {cx-44},94" fill="none" stroke="{GOLD}" stroke-width="1" opacity="0.8"/>'
    b += f'<path d="M{cx+44},78 Q{cx+50},86 {cx+44},94" fill="none" stroke="{GOLD}" stroke-width="1" opacity="0.8"/>'
    b += _label(cx-170, 70, "Mittelfinger zieht", "middle", 7)
    b += _label(cx+170, 70, "Mittelfinger zieht", "middle", 7)
    b += _label(cx, 116, "Schultern fallen", "middle", 7)
    return _svg(380, 310, b)

# ───── Wu Qin Xi — 5 Tiere (kompakt) ────────────────────────────────────────

def fig_tiger():
    cx = 90
    b = _ground(cx, 250, 60)
    b += _leg(cx-16, 156, cx-40, 196, cx-46, 248, thick=13)
    b += _leg(cx+16, 156, cx+40, 196, cx+46, 248, thick=13)
    b += _foot(cx-46, 250, 'front'); b += _foot(cx+46, 250, 'front')
    b += _hip_pants(cx, 150, 28, 8)
    b += _torso(cx, 78, 38, 30, 72)
    # Tigerklauen — gespreizte Hände nach vorne
    b += _arm_straight(cx-36, 82, cx-70, 92)
    b += _arm_straight(cx+36, 82, cx+70, 92)
    # Klauenhände
    for hx, hy in [(cx-80, 92), (cx+80, 92)]:
        b += f'<ellipse cx="{hx}" cy="{hy}" rx="7" ry="6" fill="{SK}" stroke="{INK}" stroke-width="1.3"/>'
        for fx, fy in [(hx-10, hy-6),(hx-12, hy-2),(hx-10, hy+4)]:
            b += f'<path d="M{hx-4},{hy-1} Q{fx+2},{fy} {fx},{fy}" fill="none" stroke="{INK}" stroke-width="1.4"/>'
    b += _neck(cx, 68, 7, 10); b += _head(cx, 52, 14, 'fierce')
    b += _label(cx, 30, "Tiger", "middle", 9, RED, italic=False)
    return _svg(200, 270, b)

def fig_deer():
    cx = 100
    b = _ground(cx, 250, 60)
    b += _leg(cx-12, 156, cx-14, 196, cx-18, 248, thick=12)
    b += _leg(cx+12, 156, cx+14, 196, cx+18, 248, thick=12)
    b += _foot(cx-18, 250, 'front'); b += _foot(cx+18, 250, 'front')
    b += _hip_pants(cx, 150, 24, 8)
    b += _torso(cx, 78, 36, 28, 72)
    # Hirschgeweih-Hände: Zeige- und kleiner Finger ausgestreckt
    for sx, hx in [(cx-34, cx-60), (cx+34, cx+60)]:
        b += _arm_straight(sx, 82, hx, 60)
        b += f'<ellipse cx="{hx}" cy="56" rx="5" ry="6" fill="{SK}" stroke="{INK}" stroke-width="1.2"/>'
        b += f'<line x1="{hx-3}" y1="52" x2="{hx-6}" y2="36" stroke="{INK}" stroke-width="1.6"/>'
        b += f'<line x1="{hx+3}" y1="52" x2="{hx+6}" y2="36" stroke="{INK}" stroke-width="1.6"/>'
    b += _neck(cx, 68, 7, 10); b += _head(cx, 52, 14, 'meditative')
    b += _label(cx, 280, "Hirsch", "middle", 9, RED, italic=False)
    return _svg(220, 290, b)

def fig_bear():
    cx = 90
    b = _ground(cx, 250, 60)
    b += _leg(cx-14, 158, cx-18, 200, cx-24, 248, thick=14)
    b += _leg(cx+14, 158, cx+18, 200, cx+24, 248, thick=14)
    b += _foot(cx-24, 250, 'front'); b += _foot(cx+24, 250, 'front')
    b += _hip_pants(cx, 152, 28, 8)
    b += _torso(cx, 84, 44, 36, 70)
    b += _arm(cx-44, 88, cx-50, 124, cx-44, 158, side='l')
    b += _arm(cx+44, 88, cx+50, 124, cx+44, 158, side='r')
    b += f'<ellipse cx="{cx-44}" cy="166" rx="9" ry="7" fill="{SK}" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<ellipse cx="{cx+44}" cy="166" rx="9" ry="7" fill="{SK}" stroke="{INK}" stroke-width="1.5"/>'
    b += _neck(cx, 74, 8, 10); b += _head(cx, 58, 15, 'fierce')
    # Schulterrolle
    b += f'<path d="M{cx-50},72 Q{cx-54},80 {cx-46},90" fill="none" stroke="{GOLD}" stroke-width="1.2"/>'
    b += f'<path d="M{cx+50},72 Q{cx+54},80 {cx+46},90" fill="none" stroke="{GOLD}" stroke-width="1.2"/>'
    b += _label(cx, 280, "Bär", "middle", 9, RED, italic=False)
    return _svg(200, 290, b)

def fig_monkey():
    cx = 90
    b = _ground(cx, 250, 50)
    b += _leg(cx-10, 154, cx-18, 192, cx-26, 246, thick=12)
    b += _leg(cx+10, 154, cx+10, 198, cx+30, 240, thick=12)
    # Vorderfuß auf Zehen
    b += _foot(cx-26, 248, 'front')
    b += f'<path d="M{cx+30},240 L{cx+44},242 L{cx+42},246 Z" fill="{INK}" opacity="0.8"/>'
    b += _hip_pants(cx, 148, 24, 8)
    b += _torso(cx, 76, 34, 26, 72)
    # Eine Hand greift nach oben, andere zieht zurück
    b += _arm_straight(cx-32, 80, cx-30, 30)
    b += _hand_open(cx-30, 22, 'up', 7)
    b += _arm(cx+32, 80, cx+50, 100, cx+30, 130, side='r')
    b += _hand_open(cx+30, 138, 'down', 7)
    b += _neck(cx, 66, 7, 10); b += _head(cx-2, 50, 13, 'neutral')
    b += _label(cx, 280, "Affe", "middle", 9, RED, italic=False)
    return _svg(200, 290, b)

def fig_crane():
    cx = 100
    b = _ground(cx, 250, 60)
    # Standbein
    b += _leg(cx, 154, cx, 198, cx-2, 248, thick=13)
    b += _foot(cx-2, 250, 'front')
    # Knie hochgezogen
    b += _leg(cx, 154, cx+14, 196, cx+38, 174, thick=13)
    b += f'<ellipse cx="{cx+44}" cy="172" rx="9" ry="3" fill="{INK}" opacity="0.85"/>'
    b += _hip_pants(cx, 148, 22, 8)
    b += _torso(cx, 76, 34, 26, 72)
    # Arme breit ausgebreitet
    b += _arm_straight(cx-30, 80, cx-80, 50)
    b += _arm_straight(cx+30, 80, cx+80, 50)
    b += _hand_open(cx-86, 46, 'left', 8)
    b += _hand_open(cx+86, 46, 'right', 8)
    # Federn-Andeutung
    for ang in [-15, -25, -35]:
        import math
        rad = math.radians(ang)
        x1 = cx - 80 + math.cos(rad)*8
        y1 = 50 + math.sin(rad)*8
        b += f'<line x1="{cx-72}" y1="48" x2="{x1-15}" y2="{y1-12}" stroke="{INK}" stroke-width="0.8" opacity="0.55"/>'
        b += f'<line x1="{cx+72}" y1="48" x2="{cx+80-(x1-15-cx+80)}" y2="{y1-12}" stroke="{INK}" stroke-width="0.8" opacity="0.55"/>'
    b += _neck(cx, 66, 7, 10); b += _head(cx, 50, 13, 'meditative')
    b += _label(cx, 280, "Kranich", "middle", 9, RED, italic=False)
    return _svg(220, 290, b)

# ───── Diagramme ────────────────────────────────────────────────────────────

def fig_sanbao():
    """Drei-Schätze-Dreieck."""
    w, h = 320, 250
    def node(cx, cy, l1, l2):
        s = f'<circle cx="{cx}" cy="{cy}" r="36" fill="{BG}" stroke="{RED}" stroke-width="2"/>'
        s += f'<text x="{cx}" y="{cy-2}" text-anchor="middle" font-family="Georgia,serif" font-size="13pt" font-style="italic" fill="{INK}">{l1}</text>'
        s += f'<text x="{cx}" y="{cy+15}" text-anchor="middle" font-family="Georgia,serif" font-size="8pt" fill="{RED}">{l2}</text>'
        return s
    b = f'<polygon points="160,42 280,200 40,200" fill="none" stroke="{INK}" stroke-width="0.8" stroke-dasharray="4,4" opacity="0.3"/>'
    b += node(160, 50, "Shen", "Geist")
    b += node(50, 210, "Jing", "Essenz")
    b += node(270, 210, "Qi", "Energie")
    b += f'<circle cx="160" cy="135" r="4" fill="{GOLD}"/>'
    b += _label(160, 158, "Dan Tian", italic=True, size=7)
    return _svg(w, h, b)

def fig_progression():
    weeks = [20, 26, 32, 38, 44, 50, 56, 62, 66, 70, 72, 75]
    body = ''
    barW = 30; gap = 10; baseX = 40; baseY = 150
    for i, m in enumerate(weeks):
        x = baseX + i*(barW+gap)
        h = int(m*1.55)
        op = 0.35 + (i/12)*0.55
        body += f'<rect x="{x}" y="{baseY-h}" width="{barW}" height="{h}" fill="{RED}" opacity="{op:.2f}" rx="2"/>'
        body += f'<text x="{x+barW/2}" y="{baseY-h-4}" text-anchor="middle" font-family="Georgia,serif" font-size="7pt" fill="{INK}" font-weight="bold">{m}</text>'
        body += f'<text x="{x+barW/2}" y="{baseY+12}" text-anchor="middle" font-family="Georgia,serif" font-size="7pt" fill="{INK}">W{i+1}</text>'
    body += f'<line x1="30" y1="{baseY}" x2="{baseX+12*(barW+gap)}" y2="{baseY}" stroke="{INK}" stroke-width="1.2"/>'
    body += f'<text x="30" y="20" font-family="Georgia,serif" font-size="9pt" fill="{RED}" font-weight="bold">Minuten / Tag</text>'
    body += f'<text x="{baseX+12*(barW+gap)-10}" y="175" text-anchor="end" font-family="Georgia,serif" font-size="7.5pt" fill="{INK}" font-style="italic">12 Wochen — Vom Anfänger zum Tempel-Rhythmus</text>'
    return _svg(530, 180, body, vb="0 0 530 180")

def fig_atem():
    b = f'<ellipse cx="140" cy="90" rx="60" ry="78" fill="none" stroke="{INK}" stroke-width="1" opacity="0.22"/>'
    b += f'<path d="M140,28 L140,104" stroke="{RED}" stroke-width="2.4"/>'
    b += f'<path d="M133,96 L140,108 L147,96" fill="none" stroke="{RED}" stroke-width="2.2"/>'
    b += f'<ellipse cx="140" cy="124" rx="32" ry="22" fill="none" stroke="{RED}" stroke-width="1.8" stroke-dasharray="3,2" opacity="0.7"/>'
    b += f'<circle cx="140" cy="124" r="6" fill="{RED}" opacity="0.3"/>'
    for i in range(4):
        y = 50 + i*22
        amp = 14 - i*2
        b += f'<path d="M230,{y} Q{246-amp},{y-amp} {262},{y} Q{278+amp},{y+amp} 294,{y}" fill="none" stroke="{RED}" stroke-width="1.6" opacity="{0.85-i*0.18}"/>'
    b += _label(40, 50, "Einatmen", "start", 9)
    b += _label(40, 108, "Ausatmen", "start", 9, INK)
    b += _label(140, 158, "Dan Tian", "middle", 8.5)
    b += _label(262, 32, "Atemwellen", "middle", 8)
    return _svg(330, 178, b)

def fig_five_obstacles():
    body = ''
    items = [("Begehren", "Verlangen, das zur Obsession wird"),
             ("Übelwollen", "Ablehnung gegen Mensch oder Situation"),
             ("Trägheit", "Schwere des Körpers, Dumpfheit des Geistes"),
             ("Unruhe", "Affengeist springt durch Vergangenheit und Zukunft"),
             ("Zweifel", "Lähmende Unentschlossenheit")]
    for i, (title, desc) in enumerate(items):
        cx = 50 + i*82
        body += f'<circle cx="{cx}" cy="45" r="28" fill="{BG}" stroke="{RED}" stroke-width="1.8"/>'
        body += f'<text x="{cx}" y="49" text-anchor="middle" font-family="Georgia,serif" font-size="10pt" fill="{RED}" font-weight="bold">{i+1}</text>'
        body += f'<text x="{cx}" y="92" text-anchor="middle" font-family="Georgia,serif" font-size="9pt" fill="{INK}" font-weight="bold">{title}</text>'
        # Beschreibung kurz
        body += f'<foreignObject x="{cx-40}" y="100" width="80" height="40"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Georgia,serif;font-size:6.8pt;color:#1a1208;text-align:center;line-height:1.3;">{desc}</div></foreignObject>'
    return _svg(440, 150, body)

def fig_rain():
    def box(x, l, de, line1):
        return (f'<rect x="{x}" y="4" width="86" height="98" rx="8" fill="{BG}" stroke="{RED}" stroke-width="1.8"/>'
                f'<text x="{x+43}" y="36" text-anchor="middle" font-family="Georgia,serif" font-size="28pt" fill="{RED}" font-weight="bold">{l}</text>'
                f'<text x="{x+43}" y="62" text-anchor="middle" font-family="Georgia,serif" font-size="9pt" fill="{INK}" font-weight="bold">{de}</text>'
                f'<text x="{x+43}" y="84" text-anchor="middle" font-family="Georgia,serif" font-size="7pt" fill="{INK}">{line1}</text>')
    b = box(4, "R", "Recognize", "In welchem Zustand?")
    b += box(98, "A", "Allow", "Annehmen")
    b += box(192, "I", "Investigate", "Woher kommt es?")
    b += box(286, "N", "Non-Identify", "Ich bin nicht meine Gedanken")
    return _svg(380, 108, b)


# ═══ HTML / CSS ════════════════════════════════════════════════════════════

CSS = """
@page {size:A4;margin:22mm 20mm 26mm 22mm;
  @bottom-center{content:"— " counter(page) " —";font-family:Georgia,serif;font-size:9pt;color:#8B1A0E;}}
@page cover-page{margin:0;@bottom-center{content:none;}}
@page ch-page{margin:0;@bottom-center{content:none;}}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:Georgia,'Times New Roman',serif;font-size:10.5pt;line-height:1.65;color:#1a1208;
  background:#f5f0e6;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.cov{page:cover-page;background:#0d0b08!important;color:#f5f0e6;width:210mm;height:297mm;
  display:block;text-align:center;padding:30mm 22mm;}
.chd{page:ch-page;background:#0d0b08!important;color:#f5f0e6;width:210mm;height:297mm;
  display:block;text-align:center;padding:42mm 22mm;page-break-before:always;}
.content{page-break-before:always;}
.afterch{page-break-before:always;}
h2.t2{font-size:13pt;color:#8B1A0E;margin:6mm 0 2mm;border-bottom:1px solid #d4c9a8;padding-bottom:1.5mm;}
h3.t3{font-size:11pt;color:#1a1208;margin:4mm 0 1.5mm;font-weight:bold;}
p{margin-bottom:3mm;text-align:justify;orphans:3;widows:3;}
p+p{text-indent:4mm;}
.intro{font-size:11pt;line-height:1.78;font-style:italic;color:#3a2a1a;
  border-left:3px solid #8B1A0E;padding-left:5mm;margin:4mm 0 5mm;}
.qb{background:#ede8da;border-left:4px solid #8B1A0E;padding:4mm 6mm;margin:5mm 0;
  font-style:italic;font-size:10.5pt;color:#2a1a0a;line-height:1.7;}
.au{font-size:9pt;color:#8B1A0E;font-style:normal;text-align:right;margin-top:2mm;}
.ib{text-align:center;margin:4mm 0;}
.ic{font-size:8.5pt;color:#8B1A0E;font-style:italic;text-align:center;margin-top:2mm;}
.cb{background:#ede8da;border:1px solid #c8b98a;padding:3.5mm 5mm;margin:4mm 0;border-radius:3px;}
.ct{font-size:10pt;font-weight:bold;color:#8B1A0E;margin-bottom:1mm;}
.row{display:flex;gap:6mm;margin:3mm 0;}
.col{flex:1;}
.exrow{display:flex;gap:6mm;margin:4mm 0;align-items:flex-start;page-break-inside:avoid;}
.exfig{flex-shrink:0;text-align:center;}
.exdesc{flex:1;}
.exhdr{font-size:11.5pt;color:#8B1A0E;font-weight:bold;border-bottom:1px solid #d4c9a8;padding-bottom:1mm;margin-bottom:2mm;}
.exmeta{font-size:8.5pt;color:#8B1A0E;font-style:italic;margin-bottom:2.5mm;}
.exhow{font-size:9.8pt;line-height:1.55;}
.exhow li{margin:1mm 0 1mm 4mm;}
.exgrid2{display:flex;gap:5mm;margin:3mm 0;}
.exgrid2 .gcol{flex:1;background:#faf8f2;border:1px solid #d4c9a8;border-radius:3px;padding:2.5mm 3.5mm;}
.exgrid2 .glbl{font-size:8.5pt;font-weight:bold;color:#8B1A0E;text-transform:uppercase;letter-spacing:.5px;}
.exgrid2 .gtxt{font-size:9.5pt;line-height:1.5;}
.pb{background:#ede8da;border:1.5px solid #8B1A0E;padding:4mm 5mm;margin:4mm 0;border-radius:4px;}
.pt{font-size:11pt;font-weight:bold;color:#8B1A0E;margin-bottom:2mm;text-align:center;}
.sr{display:flex;align-items:flex-start;margin:1.8mm 0;}
.sn{display:inline-block;background:#8B1A0E;color:white;width:18px;height:18px;
  border-radius:50%;text-align:center;line-height:18px;font-size:9pt;margin-right:3mm;flex-shrink:0;font-weight:bold;}
.st{flex:1;font-size:10pt;line-height:1.55;}
.hb{border:1px solid #d4c9a8;border-left:4px solid #8B1A0E;padding:3mm 5mm;margin:3mm 0;background:#faf8f2;}
.ht{font-size:10.5pt;font-weight:bold;color:#8B1A0E;}
.kp{background:#faf8f2;border:1px solid #d4c9a8;padding:3mm 5mm;margin:2.5mm 0;border-radius:3px;}
.kp p{margin:0;font-size:10pt;padding:.8mm 0;}
.kp p::before{content:"— ";color:#8B1A0E;font-weight:bold;}
table.pl{width:100%;border-collapse:collapse;font-size:9pt;margin:3.5mm 0;}
table.pl th{background:#8B1A0E;color:white;padding:2.5mm 3mm;text-align:left;font-size:8.5pt;}
table.pl td{padding:2mm 3mm;border-bottom:.4px solid #d4c9a8;}
table.pl tr:nth-child(even) td{background:#faf8f2;}
table.pl tr.tot td{font-weight:bold;color:#8B1A0E;background:#ede8da;}
.zi{margin:4mm 0;padding:3mm 5mm;border-left:3px solid #B8961A;background:#faf8f2;}
.zt{font-size:10.5pt;font-style:italic;color:#2a1a0a;line-height:1.7;}
.zs{font-size:8.5pt;color:#8B1A0E;margin-top:1mm;text-align:right;}
.gi{margin:2.5mm 0;padding-bottom:2.5mm;border-bottom:.4px dotted #c8b98a;}
.gt{font-weight:bold;color:#8B1A0E;font-size:10.5pt;}
.gd{font-size:9.8pt;color:#1a1208;margin-top:.5mm;line-height:1.55;}
hr.or{border:none;text-align:center;margin:5mm 0;overflow:visible;height:0;}
hr.or::after{content:"❧ ❧ ❧";color:#8B1A0E;font-size:10pt;}
hr.rl{border:none;border-top:.5px solid #d4c9a8;margin:4mm 0;}
.tianimal{display:flex;gap:3mm;margin:3mm 0;flex-wrap:wrap;justify-content:space-between;}
.tcard{flex:1 1 30%;min-width:55mm;background:#faf8f2;border:1px solid #d4c9a8;border-radius:3px;padding:3mm;page-break-inside:avoid;}
.tcardh{font-weight:bold;color:#8B1A0E;font-size:10pt;margin-bottom:1mm;}
.tcardt{font-size:9pt;line-height:1.55;}
.stancegrid{display:flex;gap:4mm;margin:3mm 0;flex-wrap:wrap;}
.stcell{flex:1 1 30%;min-width:54mm;text-align:center;background:#faf8f2;border:1px solid #d4c9a8;border-radius:4px;padding:2.5mm;page-break-inside:avoid;}
.stname{font-weight:bold;color:#8B1A0E;font-size:10pt;margin:1mm 0;}
.stdesc{font-size:8.5pt;line-height:1.45;color:#1a1208;text-align:left;}
"""

def H():
    return f'<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><style>{CSS}</style></head><body>'
E = '</body></html>'

# ═══ KAPITEL-TITELSEITE ════════════════════════════════════════════════════

def ch(num, rom, title, sub):
    return f'''<div class="chd">
<div style="font-size:10pt;color:#8B1A0E;letter-spacing:5px;margin-bottom:6mm;">{num}</div>
<div style="font-size:48pt;color:#8B1A0E;font-weight:bold;opacity:.35;margin-bottom:4mm;line-height:1;">{rom}</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:6mm auto;opacity:.42;"></div>
<div style="font-size:22pt;font-weight:bold;margin-bottom:5mm;">{title}</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:6mm auto;opacity:.42;"></div>
<div style="font-size:11pt;color:#c8b98a;font-style:italic;max-width:112mm;margin:0 auto;line-height:1.7;">{sub}</div>
</div>'''

# ═══ COVER / TOC / EINLEITUNG ══════════════════════════════════════════════

def cover():
    return f'''<div class="cov">
<div style="color:#8B1A0E;font-size:13pt;letter-spacing:5px;margin-bottom:6mm;">— SAN XIU —</div>
<div style="font-size:32pt;font-weight:bold;letter-spacing:7px;margin-bottom:5mm;text-transform:uppercase;color:#f5f0e6;">SAN XIU</div>
<div style="font-size:13pt;color:#c8b98a;font-style:italic;margin-bottom:9mm;">Der dreifache Weg: Körper, Atem, Geist</div>
<div style="width:78mm;height:1px;background:#8B1A0E;margin:6mm auto;opacity:.6;"></div>
<div style="margin:6mm 0;">{fig_zazen(annotate=False, cover=True)}</div>
<div style="width:78mm;height:1px;background:#8B1A0E;margin:5mm auto;opacity:.6;"></div>
<div style="font-size:10pt;color:#8B1A0E;letter-spacing:2px;opacity:.85;margin-bottom:3mm;">Chan-Meditation · Zhan Zhuang · Qi Gong · Kung Fu</div>
<div style="font-size:10pt;color:#8B1A0E;letter-spacing:2px;opacity:.85;margin-bottom:3mm;">Inspiriert von Meister Shi Heng Yi — 35. Generation Shaolin</div>
<div style="font-size:9pt;color:#8B1A0E;letter-spacing:1px;opacity:.55;margin-top:7mm;">Trainingsbuch zur täglichen Praxis</div>
</div>'''

def titelblatt():
    return f'''<div style="page-break-before:always;text-align:center;padding:22mm 16mm 0;">
<div style="height:18mm;"></div>
<div style="font-size:34pt;color:#8B1A0E;font-weight:bold;letter-spacing:5px;margin-bottom:5mm;">SAN XIU</div>
<div style="font-size:14pt;color:#1a1208;font-style:italic;margin-bottom:12mm;">Der dreifache Weg: Körper, Atem, Geist</div>
<div style="width:78mm;height:1.5px;background:#8B1A0E;margin:6mm auto;"></div>
<p style="font-size:10pt;color:#5a4a3a;max-width:108mm;margin:6mm auto;line-height:1.78;text-align:center;">
Ein Trainingsbuch zur täglichen Kultivierung von Körper und Geist —<br>
verwurzelt in der 1500-jährigen Shaolin-Tradition und<br>
den zeitlosen Lehren von Bodhidharma (Da Mo).</p>
<div style="width:78mm;height:1.5px;background:#8B1A0E;margin:6mm auto;"></div>
<p style="font-size:9pt;color:#8B1A0E;text-align:center;max-width:108mm;margin:5mm auto;">
Inspiriert von Meister Shi Heng Yi<br>
35. Generation der Shaolin-Meister · Shaolin Temple Europe</p>
<p style="font-size:8.5pt;color:#8B1A0E;font-style:italic;text-align:center;margin-top:6mm;">
San — drei · Xiu — Kultivierung · Körper · Atem · Geist</p>
</div>'''

def toc():
    def p(t, n): return f'<div style="font-size:9.5pt;padding:1.4mm 0;border-bottom:.4px dotted #c8b98a;display:flex;justify-content:space-between;"><span>{t}</span><span style="color:#8B1A0E;font-style:italic;">{n}</span></div>'
    def h(t): return f'<div style="font-size:10.5pt;font-weight:bold;color:#8B1A0E;margin:4mm 0 1.5mm;text-transform:uppercase;letter-spacing:1px;">{t}</div>'
    return f'''<div style="page-break-before:always;padding:8mm 0 0;">
<div style="font-size:20pt;color:#8B1A0E;text-align:center;margin-bottom:8mm;letter-spacing:3px;">Inhalt</div>
<hr class="rl">
{h("Einleitung")}
{p("Der Berg und der Aufstieg",6)}{p("Über dieses Buch",7)}
{h("Teil I — Philosophische Grundlagen")}
{p("Die drei Schätze: Jing, Qi, Shen",10)}{p("Wu De — Die 14 Tugenden",11)}
{p("Die fünf Hindernisse · RAIN-Methode",12)}{p("Die fünf Wandlungsphasen (Wu Xing)",13)}
{h("Teil II — Chan-Meditation")}
{p("Bodhidharma und die Wurzel des Chan",16)}{p("Die Sitzhaltung — Sieben Punkte",17)}
{p("Schritt-für-Schritt-Praxis",18)}{p("Kinhin · Metta",19)}
{h("Teil III — Zhan Zhuang")}
{p("Das Prinzip · Song",22)}{p("Vier Stehhaltungen mit Illustrationen",23)}
{p("Was während des Stehens passiert",25)}
{h("Teil IV — Atemtechniken")}
{p("Drei Säulen · Sechs Stufen",28)}{p("Sieben zentrale Atemübungen",29)}
{h("Teil V — Shaolin Qigong")}
{p("Ba Duan Jin — Die Acht Brokate",32)}{p("Yi Jin Jing — Muskel-Sehnen-Wandlung",34)}
{h("Teil VI — Shaolin Kung Fu")}
{p("Die fünf Grundstände (Wu Bu)",38)}{p("Faustschläge und Tritte",42)}
{p("Wu Bu Quan — Die Fünf-Stand-Faust",44)}{p("Tan Tui — Linie 1",45)}
{h("Teil VII — Wu Qin Xi (Fünf Tiere)")}
{p("Tiger · Hirsch · Bär · Affe · Kranich",48)}
{h("Teil VIII — Die vier Kernübungen")}
{p("Faust · L-Stand · Seitenarme",54)}
{h("Trainingsplan")}
{p("12-Wochen-Progression",58)}{p("Tempel-Tagesrhythmus",60)}
{p("Die sieben Praxis-Prinzipien",61)}
{h("Anhang")}
{p("Zitate — Shi Heng Yi",64)}{p("Glossar",66)}
</div>'''

def einleitung():
    return f'''<div class="chd">
<div style="font-size:10pt;color:#8B1A0E;letter-spacing:5px;margin-bottom:6mm;">Einleitung</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:6mm auto;opacity:.42;"></div>
<div style="font-size:22pt;font-weight:bold;margin-bottom:5mm;">Der Weg des Selbst</div>
<div style="width:52mm;height:1px;background:#8B1A0E;margin:6mm auto;opacity:.42;"></div>
<div style="font-size:11pt;color:#c8b98a;font-style:italic;max-width:112mm;margin:5mm auto;line-height:1.75;">„Um deinem Leben Bedeutung zu geben, musst du dich selbst kennenlernen und meistern."<br><em>— Shi Heng Yi</em></div>
</div>
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Der Berg und der Aufstieg</h2>
<p class="intro">Ein Mann lebte am Fuß eines Berges. Jeden Tag betrachtete er den Gipfel. Als er aufbrach, fragte er dreißig Wanderer. Nach all den Berichten entschied er: Da so viele den Berg bereits bestiegen haben, muss ich nicht mehr selbst hinauf. Die Reise begann nie.</p>
<p>Diese Parabel trifft das Wesen aller Praxis: Kein Buch, kein Lehrer kann ersetzen, selbst auf dem Gipfel zu stehen. Worte zeigen den Weg. Gehen muss ihn jeder selbst.</p>
<p><strong>San Xiu</strong> — der dreifache Weg — bezeichnet die gleichzeitige Kultivierung von Körper, Atem und Geist. Nicht Körper <em>oder</em> Geist. Nicht Training <em>oder</em> Meditation. Alles, gleichzeitig, täglich.</p>
<h2 class="t2">Über dieses Buch</h2>
<div class="row">
<div class="col"><div class="cb"><div class="ct">Shaolin-Tradition</div>
<p style="font-size:9.8pt;margin:0;">1500 Jahre von Bodhidharma bis heute. Chan-Meditation, Qigong, Kung Fu — als eine einzige Praxis.</p></div></div>
<div class="col"><div class="cb"><div class="ct">Tägliche Praxis</div>
<p style="font-size:9.8pt;margin:0;">12-Wochen-Plan vom Anfänger zum Tempel-Rhythmus. Beständigkeit schlägt Intensität.</p></div></div>
</div>
<div class="qb">„Es gibt zwei Fehler auf dem Weg zur Selbstmeisterschaft: Nicht damit anzufangen. Und nicht den ganzen Weg zu gehen."<div class="au">— Shi Heng Yi</div></div>
</div>'''

# ═══ TEIL I — PHILOSOPHIE ══════════════════════════════════════════════════

def teil1():
    return f'''{ch("Teil I","I","Philosophische Grundlagen","Die Wurzeln verstehen, bevor du die Äste erklimmst.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Die drei Schätze — San Bao</h2>
<div class="ib">{fig_sanbao()}<div class="ic">Jing nährt Qi · Qi trägt Shen · Shen lenkt Jing</div></div>
<div class="row">
<div class="col"><div class="cb"><div class="ct">Jing — Essenz</div>
<p style="font-size:9.8pt;margin:0;">Dichteste Lebenskraft, in den Nieren gespeichert. Vorgeburtliches Jing ist endlich; nachgeburtliches Jing wird durch Schlaf, Ernährung und Qigong erneuert.</p></div></div>
<div class="col"><div class="cb"><div class="ct">Qi — Energie</div>
<p style="font-size:9.8pt;margin:0;">Bewegung, Fluss, Lebenskraft. Folgt der Intention durch Meridiane. <em>„Wo Aufmerksamkeit ist, fließt Qi."</em></p></div></div>
<div class="col"><div class="cb"><div class="ct">Shen — Geist</div>
<p style="font-size:9.8pt;margin:0;">Bewusstsein, Präsenz, Klarheit — sichtbar in den Augen. <em>„Ist der See still, siehst du den Grund."</em></p></div></div>
</div>
<div class="kp"><p><strong>Jing → Qi</strong> durch Körperpraxis &nbsp;·&nbsp; <strong>Qi → Shen</strong> durch Atem &nbsp;·&nbsp; <strong>Shen → Wuji</strong> durch Meditation</p></div>

<h2 class="t2">Wu De — Die vierzehn Tugenden</h2>
<div class="row">
<div class="col"><div class="kp">
<p><strong>Ji Lü</strong> — Disziplin</p><p><strong>Zi Zhi</strong> — Selbstkontrolle</p>
<p><strong>Qian Xu</strong> — Bescheidenheit</p><p><strong>Ci Bei</strong> — Mitgefühl</p>
<p><strong>Qian Xun</strong> — Demut</p><p><strong>Zun Jing</strong> — Respekt</p>
<p><strong>Zheng Yi</strong> — Rechtschaffenheit</p></div></div>
<div class="col"><div class="kp">
<p><strong>Xin Yong</strong> — Vertrauen</p><p><strong>Zhong Cheng</strong> — Loyalität</p>
<p><strong>Yi Yuan</strong> — Wille</p><p><strong>Ren Nai</strong> — Beharrlichkeit</p>
<p><strong>Yi Li</strong> — Beständigkeit</p><p><strong>Nai Xin</strong> — Geduld</p>
<p><strong>Yong Gan</strong> — Mut</p></div></div>
</div>

<h2 class="t2">Die fünf Hindernisse zur Selbstmeisterschaft</h2>
<div class="ib">{fig_five_obstacles()}<div class="ic">Pancha Nivarana — die fünf inneren Widerstände</div></div>
<div class="qb">„Lass es einfach regnen." &nbsp;·&nbsp; <em>Just let it RAIN.</em><div class="au">— Shi Heng Yi (TEDxVitosha)</div></div>
<div class="ib">{fig_rain()}</div>

<h2 class="t2">Die fünf Wandlungsphasen — Wu Xing</h2>
<table class="pl">
<thead><tr><th>Element</th><th>Organ</th><th>Emotion</th><th>Heilton</th><th>Jahreszeit</th></tr></thead>
<tbody>
<tr><td><strong>Holz</strong></td><td>Leber / Gallenblase</td><td>Wut · Kreativität</td><td>Xu</td><td>Frühling</td></tr>
<tr><td><strong>Feuer</strong></td><td>Herz / Dünndarm</td><td>Freude · Aufregung</td><td>Ha</td><td>Sommer</td></tr>
<tr><td><strong>Erde</strong></td><td>Milz / Magen</td><td>Sorge · Grübeln</td><td>Hu</td><td>Spätsommer</td></tr>
<tr><td><strong>Metall</strong></td><td>Lunge / Dickdarm</td><td>Trauer · Loslassen</td><td>Si</td><td>Herbst</td></tr>
<tr><td><strong>Wasser</strong></td><td>Nieren / Blase</td><td>Angst · Weisheit</td><td>Chui</td><td>Winter</td></tr>
</tbody></table>
</div>'''

# ═══ TEIL II — CHAN-MEDITATION ═════════════════════════════════════════════

def teil2():
    return f'''{ch("Teil II","II","Chan-Meditation","Der Atem ist immer im Hier und Jetzt.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Bodhidharma und die Wurzel des Chan</h2>
<p>Chan wurde im 6. Jahrhundert von Bodhidharma (Da Mo) im Shaolin-Kloster etabliert. Neun Jahre lang soll er in einer Höhle vor einer Wand meditiert haben — <em>biguan</em>, Wandmeditation. Anschließend entwickelte er das Yi Jin Jing für die körperlich geschwächten Mönche, um Geist und Leib in eine Praxis zu vereinen.</p>
<div class="qb">„Shaolin ist Chan. Die Bewegungen, Formen, Disziplin — alles ist ein Fahrzeug für das Verständnis des Selbst."<div class="au">— Shi Heng Yi</div></div>

<h2 class="t2">Die Sitzhaltung — Sieben Punkte</h2>
<div class="exrow">
<div class="exfig">{fig_zazen()}</div>
<div class="exdesc">
<div class="exhdr">Die anatomische Ordnung</div>
<div class="exhow">
<div class="sr"><span class="sn">1</span><div class="st"><strong>Baihui</strong> zieht sanft zum Himmel.</div></div>
<div class="sr"><span class="sn">2</span><div class="st"><strong>Augen halb</strong> geschlossen, Blick weich nach unten.</div></div>
<div class="sr"><span class="sn">3</span><div class="st"><strong>Schultern</strong> fallen, Achseln offen.</div></div>
<div class="sr"><span class="sn">4</span><div class="st"><strong>Wirbelsäule</strong> wie eine Münzsäule — gestapelt, aufgerichtet.</div></div>
<div class="sr"><span class="sn">5</span><div class="st"><strong>Dhyana-Mudra</strong>: rechte Hand auf linker, Daumenspitzen berühren.</div></div>
<div class="sr"><span class="sn">6</span><div class="st"><strong>Lotus oder bequem</strong> — Hauptsache stabil.</div></div>
</div>
</div></div>

<h2 class="t2">Schritt-für-Schritt: Deine Meditationspraxis</h2>
<div class="pb"><div class="pt">Die tägliche Sitzmeditation</div>
<div class="sr"><span class="sn">1</span><div class="st"><strong>Ort wählen.</strong> Täglich gleicher Ort — das Gehirn assoziiert ihn mit Stille.</div></div>
<div class="sr"><span class="sn">2</span><div class="st"><strong>Sieben Punkte einstellen.</strong> Kiefer locker. Zunge am Gaumen. Schultern fallen.</div></div>
<div class="sr"><span class="sn">3</span><div class="st"><strong>Atem zentrieren.</strong> Mindestens neun Atemzüge — voll und langsam.</div></div>
<div class="sr"><span class="sn">4</span><div class="st"><strong>Dan Tian als Anker.</strong> Aufmerksamkeit drei Fingerbreit unter den Nabel.</div></div>
<div class="sr"><span class="sn">5</span><div class="st"><strong>Gedanken benennen.</strong> „Planung." „Sorge." — benannt, losgelassen.</div></div>
<div class="sr"><span class="sn">6</span><div class="st"><strong>Dauer steigern.</strong> Anfänger 10–15 Min. · Mittelstufe 20–30 Min. · Tempel 45–60 Min.</div></div>
</div>

<div class="exrow">
<div class="exfig">{fig_kinhin()}</div>
<div class="exdesc">
<div class="exhdr">Kinhin — Gehmeditation</div>
<div class="exmeta">5–10 Min. zwischen den Sitzphasen</div>
<p style="font-size:10pt;">Kinhin bringt die innere Stille in Bewegung — ein Schritt pro Atemzug, halbe Fußlänge, Hände in Gassho vor der Brust. Das Tempo: halb so schnell wie normales Gehen.</p>
<div class="kp" style="margin-top:2mm;"><p>Rechter Fuß beim Einatmen — linker beim Ausatmen.</p><p>Blick weich auf den Boden zwei Meter vor dir.</p></div>
</div></div>

<h2 class="t2">Metta — Mitgefühl kultivieren</h2>
<p style="text-align:center;font-size:9pt;color:#8B1A0E;font-style:italic;margin-bottom:3mm;">Ci Bei Guan — Loving-Kindness Meditation · 15 Minuten täglich</p>
<div class="pb">
<div class="sr"><span class="sn">1</span><div class="st"><strong>Für dich selbst (4 Min.).</strong> <em>„Möge ich glücklich, gesund, in Frieden sein."</em></div></div>
<div class="sr"><span class="sn">2</span><div class="st"><strong>Für nahe Menschen (3 Min.).</strong> Dieselben Worte, auf sie gerichtet.</div></div>
<div class="sr"><span class="sn">3</span><div class="st"><strong>Für neutrale Menschen (3 Min.).</strong> Jemand, den du kaum kennst.</div></div>
<div class="sr"><span class="sn">4</span><div class="st"><strong>Für schwierige Menschen (2 Min.).</strong> Mut, hier wirklich zu wünschen.</div></div>
<div class="sr"><span class="sn">5</span><div class="st"><strong>Für alle Wesen (3 Min.).</strong> Das Feld der liebenden Güte — ohne Grenzen.</div></div>
</div>
</div>'''

# ═══ TEIL III — ZHAN ZHUANG ════════════════════════════════════════════════

def teil3():
    return f'''{ch("Teil III","III","Zhan Zhuang","Stehen wie ein Pfahl. In äußerer Stille — maximale innere Arbeit.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Das Prinzip · Song</h2>
<p>Zhan Zhuang verbindet seit 27 Jahrhunderten körperliche Kraft mit innerer Kultivierung. Von außen: nichts passiert. Von innen: der Geist spürt Spannungen auf, der Körper entwickelt elastische innere Kraft.</p>
<div class="kp">
<p><strong>Physisch:</strong> Muskeln hängen. Gelenke öffnen. Schwere sinkt in den Boden.</p>
<p><strong>Atem:</strong> Lang, leise, durch die Nase. Dan Tian dehnt sich allseitig.</p>
<p><strong>Mental:</strong> <em>„Let the drama out of your mind."</em> — Shi Heng Yi</p>
</div>

<h2 class="t2">Vier Stehhaltungen</h2>

<div class="exrow">
<div class="exfig">{fig_wuji()}</div>
<div class="exdesc">
<div class="exhdr">1 · Wuji — Der Grundstand</div>
<div class="exmeta">Dauer: 3–30 Min. · Ausgangspunkt aller Praxis</div>
<p style="font-size:10pt;">Wuji bedeutet die Leere vor dem Beginn. Aus ihr entsteht alle Form. Wer Wuji nicht kann, kann nichts anderes.</p>
<div class="kp" style="margin-top:2mm;">
<p>Füße parallel, schulterbreit. Gewicht auf Yongquan.</p>
<p>Knie minimal weich — nie durchgestreckt.</p>
<p>Becken neutral. Baihui zieht nach oben.</p>
<p>Schultern locker. Zunge am Gaumen.</p>
</div></div></div>

<div class="exrow">
<div class="exfig">{fig_baum()}</div>
<div class="exdesc">
<div class="exhdr">2 · Den Baum halten — Cheng Bao</div>
<div class="exmeta">Dauer: 5–20 Min. · Die berühmteste Haltung</div>
<p style="font-size:10pt;">Arme auf Brusthöhe, als umarmst du einen großen Baum. Ellbogen tiefer als Handgelenke. Achseln offen — Tischtennisbälle eingeklemmt. Handflächen zum Körper. Visualisiere einen Qi-Ball zwischen Händen und Brust.</p>
<div class="kp" style="margin-top:2mm;"><p>Schultern fallen — sie tragen nichts.</p><p>Finger leicht gespreizt.</p></div>
</div></div>

<div class="exrow">
<div class="exfig">{fig_mabu()}</div>
<div class="exdesc">
<div class="exhdr">3 · Ma Bu — Reiterhaltung</div>
<div class="exmeta">Dauer: 2–10 Min. · „Das ist Willenskraft"</div>
<p style="font-size:10pt;">Zwei Schulterbreiten, Knie tief gebeugt bis Oberschenkel parallel. Rücken aufrecht. Fäuste an den Hüften. Knie über den Fußspitzen — nie nach innen. Steißbein senkrecht — kein Hohlkreuz.</p>
<div class="qb" style="margin-top:2mm;font-size:9.5pt;">„Zittern ist Fortschritt. Tiefe Muskelschichten erwachen."<div class="au">— Shi Heng Yi</div></div>
</div></div>

<div class="exrow">
<div class="exfig">{fig_squat()}</div>
<div class="exdesc">
<div class="exhdr">4 · Squatting Monkey — Dun Hou</div>
<div class="exmeta">Dauer: 5–15 Min. · Mit Zittern</div>
<p style="font-size:10pt;">Tiefe Hocke, Knie gebeugt, Hüfte sinkt nahezu auf die Fersen. Hände vor der Brust. Shi Heng Yi: <em>„Täglich 15 Minuten — unmittelbar in dem Zustand, bei dem der ganze Körper schüttelt. Brennen ist gut. Feuer transformiert."</em></p>
<div class="kp" style="margin-top:2mm;"><p>Fersen am Boden — sonst Halbhocke.</p><p>Atem nie anhalten — das Zittern fließt durch.</p></div>
</div></div>

<h2 class="t2">Was während des Stehens passiert</h2>
<table class="pl">
<thead><tr><th>Phase</th><th>Empfindung</th><th>Anweisung</th></tr></thead>
<tbody>
<tr><td>0–3 Min.</td><td>Anfängliches Behagen, Geist schweift</td><td>Körper wahrnehmen, nicht bewerten</td></tr>
<tr><td>3–7 Min.</td><td>Brennen, Knieschmerz</td><td>Atem fließen lassen. Lächeln.</td></tr>
<tr><td>7–15 Min.</td><td>Zittern, Schwitzen</td><td>Song. Tiefer sinken.</td></tr>
<tr><td>15–30 Min.</td><td>Tiefe Wärme, Dan Tian glüht</td><td>Awareness halten</td></tr>
<tr><td>30+ Min.</td><td>Elastische Kraft, vertiefte Atmung</td><td>Stille im Sturm</td></tr>
</tbody></table>
</div>'''

# ═══ TEIL IV — ATEMTECHNIKEN ════════════════════════════════════════════════

def teil4():
    return f'''{ch("Teil IV","IV","Atemtechniken","Jeder Atemzug ist eine Tür zur Lebenskraft.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Die drei Säulen des Qi Gong</h2>
<div class="row">
<div class="col"><div class="cb"><div class="ct">Tiao Shen — Körper</div>
<p style="font-size:9.8pt;margin:0;">Physische Struktur, Ausrichtung der Knochen, Lockerheit der Muskeln.</p></div></div>
<div class="col"><div class="cb"><div class="ct">Tiao Xi — Atem</div>
<p style="font-size:9.8pt;margin:0;">Tiefe, Dauer, Intensität, Volumen. Lang, leise, sanft, gleichmäßig.</p></div></div>
<div class="col"><div class="cb"><div class="ct">Tiao Xin — Geist</div>
<p style="font-size:9.8pt;margin:0;">Yi — Intention. Wo die Aufmerksamkeit ist, fließt das Qi.</p></div></div>
</div>
<div class="ib">{fig_atem()}<div class="ic">Bauchatmung: tief in den Dan Tian — Ausatmung länger als Einatmung</div></div>

<h2 class="t2">Sechs Stufen der Atemverfeinerung</h2>
<table class="pl">
<thead><tr><th>Stufe</th><th>Name</th><th>Beschreibung</th></tr></thead>
<tbody>
<tr><td>1</td><td>Lungenatmung</td><td>Brustatmung — flach, schnell. Häufigste Alltagsform.</td></tr>
<tr><td>2</td><td>Bauchatmung</td><td>Tief ins Dan Tian. Grundlage aller Qigong-Praxis.</td></tr>
<tr><td>3</td><td>Umgekehrte Bauchatmung</td><td>Bauch zieht beim Einatmen ein — Qi-Verdichtung.</td></tr>
<tr><td>4</td><td>Fersenatmung</td><td>Energie fließt bis in die Fersen (Zhuangzi).</td></tr>
<tr><td>5</td><td>Porenatmung</td><td>Jede Pore atmet. Körper und Umgebung durchlässig.</td></tr>
<tr><td>6</td><td>Embryonalatmung</td><td>Kaum merklicher Atem. Vollständige Stille.</td></tr>
</tbody></table>

<h2 class="t2">Sieben zentrale Atemübungen</h2>
<div class="exgrid2"><div class="gcol"><div class="glbl">1 · Achtsame Atmung</div>
<div class="gtxt">Wuji-Stand. Atemstrom beobachten ohne zu verändern. Neun Atemzüge zum Einstieg.</div></div>
<div class="gcol"><div class="glbl">2 · Tiefe Bauchatmung</div>
<div class="gtxt">Ein: Bauch wölbt sich wie ein Ballon. Aus: sanft einziehen. Verhältnis 4:6 bis 8:12 Sek.</div></div></div>

<div class="exgrid2"><div class="gcol"><div class="glbl">3 · Umgekehrte Bauchatmung</div>
<div class="gtxt">Beim Einatmen zieht der Bauch sich EIN. Qi-Verdichtung für innere Kraft. Erst nach stabiler Bauchatmung. Nicht bei Bluthochdruck.</div></div>
<div class="gcol"><div class="glbl">4 · Atem in Bewegung</div>
<div class="gtxt">Einatmen bei Heben/Öffnen/Strecken/Aufwärts. Ausatmen bei Senken/Schließen/Kraft/Abwärts.</div></div></div>

<div class="exgrid2"><div class="gcol"><div class="glbl">5 · Großer Atemzyklus</div>
<div class="gtxt">8 Sek. ein — 12 Sek. aus. Ziel: 4–6 Atemzüge pro Minute. 5–10 Min. Abschluss.</div></div>
<div class="gcol"><div class="glbl">6 · Liu Zi Jue — Sechs Heiltöne</div>
<div class="gtxt">Xu (Leber), Ha (Herz), Hu (Milz), Si (Lunge), Chui (Nieren), Xi (San Jiao). Je 6–9 Wiederholungen.</div></div></div>

<div class="cb" style="margin-top:3mm;"><div class="ct">7 · Zhan Zhuang Atmung</div>
<p style="font-size:9.8pt;margin:0;">Natürliche Bauchatmung durch die Nase. Ausatmen: Spannung in den Boden entladen. Einatmen: Erdenergie durch Yongquan aufwärts. Nach 15 Min. vertieft sich der Atem automatisch.</p></div>
</div>'''

# ═══ TEIL V — SHAOLIN QIGONG ════════════════════════════════════════════════

def teil5():
    return f'''{ch("Teil V","V","Shaolin Qigong","Ba Duan Jin · Yi Jin Jing — die klassischen Formen.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Ba Duan Jin — Die Acht Brokate</h2>
<p style="text-align:center;font-size:9pt;color:#8B1A0E;font-style:italic;margin-bottom:3mm;">Song-Dynastie (960 n. Chr.) · „Schön wie kostbarer Brokatstoff"</p>
<p>Shi Heng Yi: <em>„Bleibe in jeder Haltung. Mindestens vier Atemzyklen. Halte die Kraft gleichmäßig."</em></p>

<div class="exrow">
<div class="exfig">{fig_bogen()}</div>
<div class="exdesc">
<div class="exhdr">Brokat 2 · Den Bogen spannen</div>
<div class="exmeta">3× je Seite — Lungen- und Herzmeridian</div>
<p style="font-size:10pt;">Aus Ma Bu. Linker Zeigefinger zeigt zur Seite (BaZi). Rechte Faust zieht einen unsichtbaren goldenen Bogen. Blick folgt dem Zeigefinger. Brustwirbelsäule dreht aktiv.</p>
<div class="kp" style="margin-top:2mm;"><p>Schultern bleiben tief — kein Hochziehen.</p><p>Rücken aufrecht, kein Einsinken.</p></div>
</div></div>

<table class="pl" style="margin-top:4mm;">
<thead><tr><th>#</th><th>Name</th><th>Hauptwirkung</th><th>Wdh.</th></tr></thead>
<tbody>
<tr><td>1</td><td>Himmel stützen</td><td>San Jiao · Lunge · Faszienketten</td><td>6×</td></tr>
<tr><td>2</td><td>Bogen spannen</td><td>Herz- und Lungenmeridian</td><td>3× je S.</td></tr>
<tr><td>3</td><td>Himmel und Erde spalten</td><td>Milz · Magen · Verdauung</td><td>6×</td></tr>
<tr><td>4</td><td>Eule blickt zurück</td><td>Nacken · Wirbelsäule · Du Mai</td><td>3× je S.</td></tr>
<tr><td>5</td><td>Bär bewegt sich</td><td>Herzfeuer kühlen</td><td>6×</td></tr>
<tr><td>6</td><td>Zehen berühren</td><td>Nieren · Lende · Ren Mai</td><td>6×</td></tr>
<tr><td>7</td><td>Fäuste ballen, grimmig schauen</td><td>Leber · Muskelkraft</td><td>6×</td></tr>
<tr><td>8</td><td>Siebenmaliges Wippen</td><td>Qi glätten · Nieren</td><td>7×</td></tr>
</tbody></table>

<h2 class="t2">Yi Jin Jing — Muskel-Sehnen-Wandlung</h2>
<p>12 Übungen, stehend, Bodhidharma zugeschrieben. <em>„Du musst fühlen, welchen Teil des Körpers jede Übung beeinflusst."</em></p>

<div class="exrow">
<div class="exfig">{fig_weituo()}</div>
<div class="exdesc">
<div class="exhdr">Yi Jin Jing 1 · Wei Tuo bringt den Stab dar</div>
<div class="exmeta">Stille Eröffnung — Atem beruhigen</div>
<p style="font-size:10pt;">Stehe ruhig, Füße schulterbreit. Hände gefaltet vor der Brust, Daumen berühren das Brustbein. Atme neun lange Atemzüge in die Hände hinein. Spüre die Wärme, die zwischen den Handflächen entsteht.</p>
</div></div>

<table class="pl">
<thead><tr><th>#</th><th>Name</th><th>Hauptwirkung</th></tr></thead>
<tbody>
<tr><td>1</td><td>Wei Tuo bringt den Stab</td><td>Geist beruhigen · Atem regulieren</td></tr>
<tr><td>2</td><td>Schultern öffnen</td><td>Schultergürtel · Qi-Zirkulation</td></tr>
<tr><td>3</td><td>Den Himmel stützen</td><td>San Jiao öffnen</td></tr>
<tr><td>4</td><td>Sterne pflücken</td><td>Nieren · Mingmen</td></tr>
<tr><td>5</td><td>Neun Ochsen am Schwanz ziehen</td><td>Herz- und Lungenmeridian</td></tr>
<tr><td>6</td><td>Krallen zeigen, Flügel breiten</td><td>Lunge öffnen · Brustkorb weiten</td></tr>
<tr><td>7</td><td>Neun Geister ziehen das Pferdeschwert</td><td>Yin-Meridiane · Herz-Niere-Achse</td></tr>
<tr><td>8</td><td>Drei Teller auf dem Boden</td><td>Nieren stärken</td></tr>
<tr><td>9</td><td>Schwarzer Drache zeigt die Klauen</td><td>Leber · Schulterblatt</td></tr>
<tr><td>10</td><td>Tiger springt auf die Beute</td><td>Du Mai · Wirbelsäule</td></tr>
<tr><td>11</td><td>Verbeugen und grüßen</td><td>Gehirndurchblutung</td></tr>
<tr><td>12</td><td>Den Schwanz schwingen</td><td>Integration · alle Meridiane</td></tr>
</tbody></table>
<div class="cb" style="margin-top:3mm;"><div class="ct">Stufenweise Wirkungen — Klassische Lehre</div>
<p style="font-size:9.8pt;margin:0;">Jahr 1: Vitalität · Jahr 2: Blutzirkulation · Jahr 3: Sehnen elastisch · Jahr 4: Meridiane · Jahr 5: Knochenmark</p></div>
</div>'''

# ═══ TEIL VI — SHAOLIN KUNG FU ═════════════════════════════════════════════

def teil6():
    return f'''{ch("Teil VI","VI","Shaolin Kung Fu","Die fünf Stände sind die Mutter aller Formen.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Die fünf Grundstände — Wu Bu</h2>
<p>Wu Bu sind das anatomische Alphabet des Kung Fu. Jede Bewegung, jede Form ruht auf ihnen. Shi Heng Yi empfiehlt: <em>„Halte jeden Stand. Beginne kurz, steigere stetig."</em></p>

<div class="exrow">
<div class="exfig">{fig_mabu()}</div>
<div class="exdesc">
<div class="exhdr">1 · Ma Bu — Pferdestand</div>
<div class="exmeta">Gewicht 50/50 · Aufbau der Beinkraft, Senkung des Qi</div>
<p style="font-size:10pt;">Füße parallel, etwa zwei Schulterbreiten auseinander. Knie tief gebeugt bis Oberschenkel waagerecht (oder so tief wie möglich). Rücken aufrecht, Becken neutral. Mutter aller Stände. Schult mentale Standhaftigkeit wie kaum eine andere Übung.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_gongbu()}</div>
<div class="exdesc">
<div class="exhdr">2 · Gong Bu — Bogenstand</div>
<div class="exmeta">Gewicht 70/30 vorne · Vorwärtskraft, Verwurzelung</div>
<p style="font-size:10pt;">Vorderes Bein tief gebeugt, Knie genau über dem Fuß. Hinteres Bein gestreckt, hintere Ferse am Boden, Fuß 45° geöffnet. Schultern parallel zur vorderen Fußspitze. Schult Hüftrotation und Schlagkraft.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_xubu()}</div>
<div class="exdesc">
<div class="exhdr">3 · Xu Bu — Leerer Stand</div>
<div class="exmeta">Gewicht 90/10 · Schnelle Trittbereitschaft, Sensibilität</div>
<p style="font-size:10pt;">Hinteres Bein trägt nahezu das gesamte Gewicht, tief gebeugt. Vorderer Fuß berührt nur mit dem Ballen leicht den Boden. Knie locker. Wer Xu Bu beherrscht, kann jederzeit ausweichen oder treten.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_pubu()}</div>
<div class="exdesc">
<div class="exhdr">4 · Pu Bu — Geduckter Stand</div>
<div class="exmeta">Gewicht 80/20 · Hüftöffnung, tiefe Bewegungen</div>
<p style="font-size:10pt;">Ein Bein vollständig gestreckt seitwärts, Fuß flach. Anderes Bein vollständig gebeugt unter dem Körper. Wirbelsäule aufrecht. Eine der härtesten Bewegungen — geduldig öffnen, niemals erzwingen.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_xiebu()}</div>
<div class="exdesc">
<div class="exhdr">5 · Xie Bu — Kreuzstand</div>
<div class="exmeta">Vorbereitung für Wendungen, versteckte Tritte</div>
<p style="font-size:10pt;">Beine überkreuzt, hinteres Knie sinkt fast zum Boden hinter dem vorderen Bein. Hintere Ferse abgehoben. Tarnstellung und Drehkraft in einer Haltung — Übergang in viele Formen.</p>
</div></div>

<h2 class="t2">Faustschläge und Tritte</h2>

<div class="exrow">
<div class="exfig">{fig_chongquan()}</div>
<div class="exdesc">
<div class="exhdr">Chong Quan — Geradeschlag</div>
<div class="exmeta">Hauptwaffe für Distanz · Hüftkraft</div>
<p style="font-size:10pt;">Faust schießt aus der Hüfte gerade nach vorne. Im letzten Drittel dreht sich die Hand von Handfläche nach oben in Handfläche nach unten. Andere Faust zieht gleichzeitig zur Hüfte zurück (Gegenkraft).</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_piquan()}</div>
<div class="exdesc">
<div class="exhdr">Pi Quan — Hackschlag</div>
<div class="exmeta">Bricht Deckung von oben</div>
<p style="font-size:10pt;">Faust hebt sich am Ohr vorbei und schlägt vertikal von oben nach unten. Trefffläche ist die Faustunterseite. Hüfte sinkt mit der Bewegung. Ziel: Schlüsselbein oder Schädeldach.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_tantui()}</div>
<div class="exdesc">
<div class="exhdr">Tan Tui — Federtritt</div>
<div class="exmeta">Schneller Frontkick mit Fußballen</div>
<p style="font-size:10pt;">Knie schnellt zum Körper hoch, Unterschenkel schießt federnd nach vorne. Schlagfläche ist der Fußballen oder Spann. Peitschenartig — Kraft kommt aus dem Knie, nicht aus dem Schwung des ganzen Beins.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_cechuai()}</div>
<div class="exdesc">
<div class="exhdr">Ce Chuai — Seittritt</div>
<div class="exmeta">Mächtigster Tritt im Shaolin-Repertoire</div>
<p style="font-size:10pt;">Knie zum Körper gezogen, Bein streckt sich seitlich aus mit Fußaußenkante oder Ferse als Trefffläche. Standbein leicht eingedreht, Hüfte schiebt mit. Treffer in Bauch, Knie oder Rippen.</p>
</div></div>

<div class="exgrid2">
<div class="gcol"><div class="glbl">Liao Quan — Aufwärtsschlag</div>
<div class="gtxt">Faust steigt von tief unten aufwärts, Handfläche zeigt am Ende zum Körper. Ziel: Kinn oder Solarplexus aus geduckter Position.</div></div>
<div class="gcol"><div class="glbl">Beng Quan — Stoßschlag</div>
<div class="gtxt">Kurzer, schneller Vorwärtsstoß aus dem Ellenbogen. Faust dreht nicht vollständig. Direkter Treffer auf kurze Distanz mit explosivem Hüftruck.</div></div>
</div>
<div class="exgrid2">
<div class="gcol"><div class="glbl">Hou Tui — Rücktritt</div>
<div class="gtxt">Blick über die Schulter, Ferse stößt nach hinten gerade aus. Körper neigt sich leicht nach vorne als Gegengewicht.</div></div>
<div class="gcol"><div class="glbl">Wai Bai / Li He — Sichelschritte</div>
<div class="gtxt">Bein schwingt halbkreisförmig in Kopfhöhe. Wai Bai von innen nach außen, Li He von außen nach innen — der Test für Hüftöffnung.</div></div>
</div>

<h2 class="t2">Wu Bu Quan — Die Fünf-Stand-Faust</h2>
<p>Die klassische Anfänger-Form aller Shaolin-Schulen. Sie enthält die fünf Grundstände, drei Schlagarten und zwei Tritte in zehn fließenden Bewegungen.</p>
<div class="pb"><div class="pt">Die zehn Schritte</div>
<div class="sr"><span class="sn">1</span><div class="st">Bing Bu — Schließstellung mit Faustgruß (Bao Quan Li).</div></div>
<div class="sr"><span class="sn">2</span><div class="st">Schritt nach links in Ma Bu mit doppeltem Faustziehen an die Hüfte.</div></div>
<div class="sr"><span class="sn">3</span><div class="st">Drehung nach links in Gong Bu mit Chong Quan.</div></div>
<div class="sr"><span class="sn">4</span><div class="st">Wechsel in Xu Bu mit aufsteigendem Block (Liao Zhang).</div></div>
<div class="sr"><span class="sn">5</span><div class="st">Übergang in Pu Bu mit Handflächenstreich entlang des gestreckten Beins.</div></div>
<div class="sr"><span class="sn">6</span><div class="st">Aufrichten in Gong Bu mit Chong Quan.</div></div>
<div class="sr"><span class="sn">7</span><div class="st">180°-Drehung in Xie Bu mit Pi Quan nach unten.</div></div>
<div class="sr"><span class="sn">8</span><div class="st">Aufstehen, Knieheben (Ti Xi) mit hochsteigender Faust.</div></div>
<div class="sr"><span class="sn">9</span><div class="st">Tan Tui vorwärts, Landung in Gong Bu mit Doppelfaust.</div></div>
<div class="sr"><span class="sn">10</span><div class="st">Rückkehr in Bing Bu, Faustgruß — Abschluss.</div></div>
</div>

<h2 class="t2">Tan Tui — Linie 1 (Lu Yi)</h2>
<p>Die erste der zwölf Linien — Federbeine, das tägliche Brot des Shaolin-Trainings. Schult Punch-Kick-Koordination und Hüftantrieb.</p>
<div class="pb">
<div class="sr"><span class="sn">1</span><div class="st">Aus Bing Bu vorwärts in rechten Gong Bu mit rechtem Chong Quan auf Brusthöhe.</div></div>
<div class="sr"><span class="sn">2</span><div class="st">Rechte Faust zur Hüfte zurück, linke Faust schießt geradeaus.</div></div>
<div class="sr"><span class="sn">3</span><div class="st">Linker Tan Tui auf Bauchhöhe.</div></div>
<div class="sr"><span class="sn">4</span><div class="st">Landung in linkem Gong Bu mit rechtem Chong Quan.</div></div>
<div class="sr"><span class="sn">5</span><div class="st">Faustwechsel: rechte zurück, linke vor.</div></div>
<div class="sr"><span class="sn">6</span><div class="st">180°-Drehung. Wiederholung in Gegenrichtung.</div></div>
</div>
</div>'''

# ═══ TEIL VII — WU QIN XI ══════════════════════════════════════════════════

def teil7():
    return f'''{ch("Teil VII","VII","Wu Qin Xi","Das Spiel der fünf Tiere — Hua Tuo, 2. Jahrhundert.")}
<div class="content">
<p class="intro">Hua Tuo, einer der größten Heiler der chinesischen Geschichte, sagte: <em>„Bewegung verhindert Krankheit, wie eine Tür, deren Angeln nicht rosten."</em> Seine fünf Tierübungen sind die älteste belegte Qigong-Form. Jedes Tier kultiviert ein Organsystem und einen Charakterzug.</p>

<div class="exrow">
<div class="exfig">{fig_tiger()}</div>
<div class="exdesc">
<div class="exhdr">Hu Xi — Der Tiger erhebt die Pranke</div>
<div class="exmeta">Organ: Leber · Tugend: Mut · Wirkung: Muskelkraft, Wirbelsäule</div>
<p style="font-size:10pt;">Aus Ma Bu. Hände werden zu Tigerklauen (Finger gekrümmt, Daumen abgespreizt). Kraftvoll von der Hüfte nach vorne und oben drücken, als würdest du eine Wand wegschieben. Begleitendes Brüllen mit der Ausatmung ist erlaubt. Stärkt Lendenmuskulatur, Leber-Qi und den kämpferischen Geist.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_deer()}</div>
<div class="exdesc">
<div class="exhdr">Lu Xi — Der Hirsch stößt das Geweih</div>
<div class="exmeta">Organ: Nieren · Tugend: Anmut · Wirkung: Wirbelsäule, Beweglichkeit</div>
<p style="font-size:10pt;">Stand schmal. Zeige- und kleiner Finger gestreckt wie Hirschgeweih, andere Finger eingerollt. Hände kreisen seitlich, dabei rotiert die Hüfte sanft. Atem fließt mit den Kreisen. Lockert die Nieren, dehnt die Wirbelsäule, schult geschmeidige Wachsamkeit.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_bear()}</div>
<div class="exdesc">
<div class="exhdr">Xiong Xi — Der Bär dreht die Hüfte</div>
<div class="exmeta">Organ: Milz · Tugend: Stabilität · Wirkung: Verdauung, Erdung</div>
<p style="font-size:10pt;">Schwerer, langsamer Schritt. Schultern rollen abwechselnd, Hüften kreisen weit. Hände hängen wie Bärentatzen. Gewicht sinkt tief, Atem geht in den Bauch. Stärkt Milz und Magen, erdet das Nervensystem nach hektischen Tagen.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_monkey()}</div>
<div class="exdesc">
<div class="exhdr">Hou Xi — Der Affe pflückt die Frucht</div>
<div class="exmeta">Organ: Herz · Tugend: Wendigkeit · Wirkung: Reflexe, Leichtigkeit</div>
<p style="font-size:10pt;">Schneller Stellungswechsel auf Zehenballen. Eine Hand greift nach oben (Frucht pflücken), die andere zieht zurück in geduckte Haltung. Wechselseitig. Trainiert Reflexe, Herz-Geist und freudige Leichtigkeit — das Mittel gegen Schwere.</p>
</div></div>

<div class="exrow">
<div class="exfig">{fig_crane()}</div>
<div class="exdesc">
<div class="exhdr">He Xi — Der Kranich breitet die Flügel</div>
<div class="exmeta">Organ: Lunge · Tugend: Gleichmut · Wirkung: Atmung, Balance</div>
<p style="font-size:10pt;">Einbeinstand. Knie hochgezogen. Arme weit seitlich öffnen mit langer Einatmung, schließen mit Ausatmung. Wiegt sich wie ein Kranich am Teich. Schult Atmung, Lungenfunktion und innere Ruhe in Bewegung. Standbein wechseln.</p>
</div></div>

<div class="cb" style="margin-top:4mm;"><div class="ct">Praxisempfehlung</div>
<p style="font-size:9.8pt;margin:0;">Pro Tier 2–3 Minuten. Gesamte Sequenz: 10–15 Minuten. Beginne mit dem Tier, das dir am leichtesten fällt. Beobachte über Wochen, welches Tier dich heute braucht.</p></div>
</div>'''

# ═══ TEIL VIII — VIER KERNÜBUNGEN ══════════════════════════════════════════

def teil8():
    return f'''{ch("Teil VIII","VIII","Die vier Kernübungen","Vier Praktiken für jeden Tag — das tägliche Brot.")}
<div class="content">
<p class="intro">Wenn du wenig Zeit hast und dennoch jeden Tag das Wesentliche üben willst, sind dies deine vier Stützen. Faust sammelt Willen. Reiter wurzelt dich. L-Stand löst Stress. Seitenarme öffnen Herz und Schultern.</p>

<div class="exrow">
<div class="exfig">{fig_fist_pose()}</div>
<div class="exdesc">
<div class="exhdr">1 · Faust ballen und halten — Wo Quan</div>
<div class="exmeta">Woche 1: 4 Min. · ab Woche 3: 6 Min.</div>
<p style="font-size:10pt;">Daumen liegt außen über Zeige- und Mittelfinger. Knöchel ausgerichtet. Spannung ca. 70 %. Fäuste hängen seitlich am Oberschenkel, leicht vor dem Körper. Atem fließt ruhig in den Dan Tian.</p>
<div class="exgrid2" style="margin-top:2mm;">
<div class="gcol"><div class="glbl">Wirkung</div>
<div class="gtxt">Sammelt zerstreute Energie. Baut isometrische Unterarmkraft. Beruhigt Unruhe.</div></div>
<div class="gcol"><div class="glbl">Fehler vermeiden</div>
<div class="gtxt">Schultern hochziehen · Atem anhalten · Gesicht verspannen · Knie durchdrücken.</div></div></div>
</div></div>

<div class="exrow">
<div class="exfig">{fig_mabu()}</div>
<div class="exdesc">
<div class="exhdr">2 · Ma Bu — Reiterhaltung</div>
<div class="exmeta">Woche 1: 2 Min. · ab Woche 4: 5 Min.</div>
<p style="font-size:10pt;">Zwei Schulterbreiten, Knie tief, Oberschenkel parallel. Becken neutral, Steißbein senkrecht. Fäuste an den Hüften. Atem nie anhalten. Detail siehe Teil III und Teil VI.</p>
<div class="qb" style="margin-top:2mm;font-size:9.5pt;">„Zittern ist Fortschritt — nicht dagegen kämpfen."<div class="au">— Shi Heng Yi</div></div>
</div></div>

<div class="exrow">
<div class="exfig">{fig_lbend_pose()}</div>
<div class="exdesc">
<div class="exhdr">3 · L-Stand mit Ausschütteln — Yao Bai</div>
<div class="exmeta">Alle Wochen: 3 Min.</div>
<p style="font-size:10pt;">Aus der Hüfte (nicht aus dem Rücken!) nach vorne klappen — Oberkörper im 90°-Winkel zum aufrechten Stand. Rücken lang. Arme hängen schwer, dann sanftes Schütteln der Hände, Unterarme, ganzer Arme.</p>
<div class="exgrid2" style="margin-top:2mm;">
<div class="gcol"><div class="glbl">Wirkung</div>
<div class="gtxt">Löst Nacken-Schultern. Durchblutet Kopf. Lässt Tagesstress aus den Händen tropfen.</div></div>
<div class="gcol"><div class="glbl">Vorsicht</div>
<div class="gtxt">Bei Bandscheiben oder Bluthochdruck: nur 45° beugen. Langsam aufrichten.</div></div></div>
</div></div>

<div class="exrow">
<div class="exfig">{fig_sidearms_pose()}</div>
<div class="exdesc">
<div class="exhdr">4 · Seitenarme — Zhang Bi</div>
<div class="exmeta">Alle Wochen: 3 Min.</div>
<p style="font-size:10pt;">Beide Arme parallel zum Boden zur Seite. Handflächen nach unten, Finger weit gespreizt. Stelle dir vor: ein feiner Faden zieht beide Mittelfinger nach außen. Die Arme werden länger. <strong>Paradox:</strong> während die Finger ziehen, sinken die Schultern.</p>
<div class="kp" style="margin-top:2mm;">
<p>Yi (Vorstellung) erzeugt den Zug, nicht die Muskeln.</p>
<p>Beim Ausatmen: mehr Sinken der Schultern, mehr Ziehen der Finger.</p>
<p>Brennen in den Deltoiden ist erwünscht.</p>
</div>
</div></div>

<hr class="or">
<h2 class="t2">Übergänge und Atem</h2>
<div class="kp">
<p><strong>Reihenfolge:</strong> 1 → 2 → 3 → 4. Erst Hände/Wille, dann Beine/Wurzel, dann Wirbelsäule lösen, zum Schluss öffnen.</p>
<p><strong>Pausen:</strong> 30 Sek. Wuji-Stand zwischen jeder Übung. Atem zentrieren. Spüren, was bleibt.</p>
<p><strong>Atemverhältnis:</strong> 4:6 bis 6:8 Sek. Niemals anhalten — auch im Brennen weiter atmen.</p>
<p><strong>Nachspüren:</strong> 60 Sek. still am Ende. Hände auf Dan Tian.</p>
</div>
</div>'''

# ═══ TRAININGSPLAN ═════════════════════════════════════════════════════════

def trainingsplan():
    return f'''{ch("Dein Weg","","Trainingsplan","12 Wochen vom Anfänger zum Tempel-Rhythmus.")}
<div class="content">
<div class="ib">{fig_progression()}<div class="ic">Tägliche Übungsdauer pro Woche — sanfte Steigerung von 20 auf 75 Minuten</div></div>

<h2 class="t2">Die tägliche Einheit — Struktur</h2>
<div class="pb"><div class="pt">Jeder Tag folgt diesem Aufbau</div>
<div class="sr"><span class="sn">1</span><div class="st"><strong>Atemzentrierung</strong> (2 Min.) — Wuji-Stand. Bauchatmung. Körper scannen.</div></div>
<div class="sr"><span class="sn">2</span><div class="st"><strong>Vier Kernübungen</strong> — Faust, Ma Bu, L-Stand, Seitenarme.</div></div>
<div class="sr"><span class="sn">3</span><div class="st"><strong>Zhan Zhuang</strong> (ab W2) — Baum halten oder Squatting Monkey.</div></div>
<div class="sr"><span class="sn">4</span><div class="st"><strong>Shaolin Qigong</strong> (ab W3) — Ba Duan Jin und Yi Jin Jing.</div></div>
<div class="sr"><span class="sn">5</span><div class="st"><strong>Kung Fu Grundlagen</strong> (ab W5) — Stände, Faust- und Tritt-Drills.</div></div>
<div class="sr"><span class="sn">6</span><div class="st"><strong>Wu Qin Xi</strong> (ab W7) — die fünf Tiere als Bewegungsspiel.</div></div>
<div class="sr"><span class="sn">7</span><div class="st"><strong>Form-Praxis</strong> (ab W10) — Wu Bu Quan oder Tan Tui Linie 1.</div></div>
<div class="sr"><span class="sn">8</span><div class="st"><strong>Sitzmeditation</strong> — Abschluss, Dauer wächst mit den Wochen.</div></div>
<div class="sr"><span class="sn">9</span><div class="st"><strong>Nachspüren</strong> (2 Min.) — Hände auf Dan Tian. Stille.</div></div>
</div>

<h2 class="t2">12-Wochen-Progression</h2>
<table class="pl">
<thead><tr><th>Block</th><th>Woche</th><th>Schwerpunkt</th><th>Min./Tag</th></tr></thead>
<tbody>
<tr><td rowspan="3"><strong>I · Fundament</strong></td><td>1</td><td>Vier Kernübungen · Sitzmeditation 10 Min.</td><td>20</td></tr>
<tr><td>2</td><td>Kernübungen + Baum halten 5 Min.</td><td>26</td></tr>
<tr><td>3</td><td>Kernübungen + Wuji + erste Atemübungen</td><td>32</td></tr>
<tr><td rowspan="3"><strong>II · Qigong</strong></td><td>4</td><td>Ba Duan Jin Brokat 1–4</td><td>38</td></tr>
<tr><td>5</td><td>Ba Duan Jin vollständig (alle 8)</td><td>44</td></tr>
<tr><td>6</td><td>Ba Duan Jin + Yi Jin Jing 1–4</td><td>50</td></tr>
<tr><td rowspan="3"><strong>III · Kung Fu</strong></td><td>7</td><td>Wu Bu — alle fünf Stände halten</td><td>56</td></tr>
<tr><td>8</td><td>Wu Bu + Faustschläge (Chong, Pi, Liao, Beng)</td><td>62</td></tr>
<tr><td>9</td><td>+ Tritte (Tan Tui, Ce Chuai) · Wu Qin Xi vollständig</td><td>66</td></tr>
<tr><td rowspan="3"><strong>IV · Form</strong></td><td>10</td><td>Wu Bu Quan lernen — Schritt für Schritt</td><td>70</td></tr>
<tr><td>11</td><td>Wu Bu Quan flüssig · Tan Tui Linie 1 lernen</td><td>72</td></tr>
<tr><td>12</td><td>Alles verbinden · Tempel-Tagesrhythmus</td><td>75</td></tr>
</tbody></table>

<h2 class="t2">Wochenrhythmus — Was wann?</h2>
<table class="pl">
<thead><tr><th>Tag</th><th>Morgen (20–40 Min.)</th><th>Abend (20–35 Min.)</th></tr></thead>
<tbody>
<tr><td>Montag</td><td>Vier Kernübungen + Ba Duan Jin</td><td>Sitzmeditation + Atemübungen</td></tr>
<tr><td>Dienstag</td><td>Vier Kernübungen + Wu Bu (Stände)</td><td>Wu Qin Xi + Sitzmeditation</td></tr>
<tr><td>Mittwoch</td><td>Vier Kernübungen + Yi Jin Jing</td><td>Sitzmeditation + Metta</td></tr>
<tr><td>Donnerstag</td><td>Vier Kernübungen + Faust- und Trittdrills</td><td>Zhan Zhuang + Sitzmeditation</td></tr>
<tr><td>Freitag</td><td>Vier Kernübungen + Wu Bu Quan</td><td>Wu Qin Xi + Sitzmeditation</td></tr>
<tr><td>Samstag</td><td>Lange Einheit: alles verbinden (60–90 Min.)</td><td>Stille — nur Sitzmeditation</td></tr>
<tr><td>Sonntag</td><td>Sanft: Wu Qin Xi + Zhan Zhuang</td><td>Lange Sitzmeditation (30–45 Min.)</td></tr>
</tbody></table>

<h2 class="t2">Tempel-Tagesrhythmus — nach Shi Heng Yi</h2>
<table class="pl">
<thead><tr><th>Zeit</th><th>Aktivität</th></tr></thead>
<tbody>
<tr><td>Aufwachen</td><td>„Wake up empty" — ohne Gedanken vom Vortag</td></tr>
<tr><td>Morgen</td><td>Sitzen, atmen, Körper scannen (1 Stunde)</td></tr>
<tr><td>Früh</td><td>Push-ups, Squatting Monkey (15 Min. halten)</td></tr>
<tr><td>Vormittag</td><td>Qigong-Praxis: Ba Duan Jin, Yi Jin Jing</td></tr>
<tr><td>Mittag</td><td>90 % vegetarische Mahlzeit, bewusstes Essen</td></tr>
<tr><td>Nachmittag</td><td>Kung Fu, Zhan Zhuang, Studium</td></tr>
<tr><td>Abend</td><td>Sitzmeditation, Stille, früh schlafen gehen</td></tr>
</tbody></table>

<h2 class="t2">Die sieben Praxis-Prinzipien</h2>
<div class="kp">
<p><strong>Atem ist der Dirigent.</strong> Niemals anhalten — auch in schmerzhaften Momenten.</p>
<p><strong>Zittern ist Fortschritt.</strong> Tiefe Muskelschichten werden aktiviert.</p>
<p><strong>Drei verborgene Spannungsfelder:</strong> Kiefer locker · Zunge am Gaumen · Nacken lang.</p>
<p><strong>Yi — Vorstellung führt das Qi.</strong> Erst Bild im Geist, dann Bewegung im Körper.</p>
<p><strong>Schmerz vs. Brennen.</strong> Muskelfeuer: willkommen. Gelenkschmerz: aufhören.</p>
<p><strong>Regelmäßigkeit schlägt Intensität.</strong> Täglich 20 Min. schlägt 90 Min. wöchentlich.</p>
<p><strong>Nachspüren ist Pflicht.</strong> Nie abrupt aufhören. 60 Sek. stilles Nachspüren.</p>
</div>

<div class="qb" style="margin-top:5mm;text-align:center;font-size:11pt;">
„Du wirst nicht über Nacht ankommen. Aber wenn du weitermachst, wirst du ankommen."<div class="au">— Shi Heng Yi</div></div>
</div>'''

# ═══ ZITATE ═════════════════════════════════════════════════════════════════

def zitate():
    def z(t, s="Shi Heng Yi"): return f'<div class="zi"><div class="zt">„{t}"</div><div class="zs">— {s}</div></div>'
    return f'''{ch("Anhang I","","Lehren Shi Heng Yi","Worte zur täglichen Begleitung.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Über Selbstmeisterschaft</h2>
{z("Es gibt zwei Fehler auf dem Weg zur Selbstmeisterschaft: Nicht damit anzufangen. Und nicht den ganzen Weg zu gehen.")}
{z("Selbstmeisterschaft bedeutet zu erkennen: Wenn du glücklich sein willst, bist du derjenige, der es erzeugen muss.")}
{z("Freiheit geht Hand in Hand mit deiner Fähigkeit, dich selbst einzuschränken. Disziplin ist Freiheit.")}
{z("Vervollkommnung kommt durch Wiederholung.")}
{z("Was man will, ist nicht so wichtig. Entscheidend ist, welche Opfer, welches Leid man bereit ist, auf sich zu nehmen.")}

<h2 class="t2">Über Geist und Bewusstsein</h2>
{z("Du bist nicht deine Gedanken. Du bist der Himmel. Manchmal ist er klar, manchmal gibt es Wolken.")}
{z("Wenn der See still ist, siehst du den Grund. Wenn dein Geist still ist, erkennst du dich selbst.")}
{z("Ich suche nicht nach Glück. Ich suche nach Frieden. Wenn es Glück gibt, gibt es Trauer.")}
{z("Gefühl ist die Verkündigung des Geistes. Was du fühlst, wurde zuerst in deinem Geist aufgebaut.")}

<h2 class="t2">Über Körper, Übung und den Weg</h2>
{z("Mentale Stärke benötigt eine sichtbare Form. Nutze deinen Körper, um zum Geist zu gelangen.")}
{z("Leben ist Bewegung. Je fließender du bist, desto mehr bist du lebendig.")}
{z("Warte nicht darauf, dass sich die Welt ändert. Beginne mit dir selbst.")}
{z("Du wirst nicht über Nacht ankommen. Aber wenn du weitermachst, wirst du ankommen.")}
{z("Spare dir dein Grimassieren, dein Klagen, dein Leiden — und wandle es in innere Energie um.")}
{z("Im Shaolin ist Natur nicht etwas außerhalb von uns. Wir sind ein Teil davon.")}

<div class="qb" style="margin-top:7mm;font-size:11.5pt;text-align:center;line-height:1.9;">
„Dorthin, wo deine Aufmerksamkeit fließt,<br>dorthin fließt auch deine Energie."
<div class="au" style="font-size:10pt;margin-top:3mm;">— Daoyin-Tradition</div></div>
</div>'''

def glossar():
    def g(t, d): return f'<div class="gi"><div class="gt">{t}</div><div class="gd">{d}</div></div>'
    return f'''{ch("Anhang II","","Glossar","Chinesische Begriffe und ihre Bedeutungen.")}
<div class="content">
<h2 class="t2" style="page-break-before:avoid;">Grundbegriffe</h2>
{g("Qi", "Lebensenergie. Fließt durch Meridiane. Folgt der Intention. Wird durch Qigong kultiviert.")}
{g("Jing", "Essenz. Die dichteste Lebensenergie — in den Nieren gespeichert.")}
{g("Shen", "Geist, Bewusstsein. Das Subtilste der drei Schätze. Residiert im Herzen.")}
{g("Yi", "Intention. Formel: Yi → Qi → Bewegung. Wo die Aufmerksamkeit ist, fließt das Qi.")}
{g("Dan Tian", "Energiezentrum. Drei Fingerbreit unter dem Nabel. Primäres Zentrum der Qigong-Praxis.")}
{g("Song", "Durchlässigkeit, Loslassen. Aktives Lösen von Spannung. Grundprinzip des Zhan Zhuang.")}
{g("Chan", "Zen. Meditationstradition, die Bodhidharma im Shaolin-Kloster begründete.")}
{g("Wu De", "Kriegerische Tugend. Die 14 ethischen Grundsätze der Shaolin-Praxis.")}

<h2 class="t2">Übungsbegriffe</h2>
{g("Zhan Zhuang", "Stehende Pfahlarbeit. Statische Stehübung zur Entwicklung innerer Kraft.")}
{g("Ba Duan Jin", "Acht-Brokate-Qigong. 8 Haupthaltungen aus der Song-Dynastie.")}
{g("Yi Jin Jing", "Muskel-Sehnen-Wandlungsklassiker. 12 Übungen, Bodhidharma zugeschrieben.")}
{g("Wu Qin Xi", "Spiel der fünf Tiere. Ältestes belegtes Qigong-System, Hua Tuo zugeschrieben.")}
{g("Wu Bu", "Die fünf Grundstände: Ma Bu, Gong Bu, Xu Bu, Pu Bu, Xie Bu.")}
{g("Ma Bu", "Pferdestand. Tiefer paralleler Stand. Grundlegende Kraftübung.")}
{g("Gong Bu", "Bogenstand. Vorderes Bein gebeugt, hinteres gestreckt. Vorwärtskraft.")}
{g("Xu Bu", "Leerer Stand. Vorderer Fuß nur mit Ballen — Trittbereitschaft.")}
{g("Wuji", "Leere vor dem Beginn. Der neutrale Grundstand.")}
{g("Wu Bu Quan", "Fünf-Stand-Faust. Klassische Anfänger-Form aller Shaolin-Schulen.")}
{g("Tan Tui", "Federbeine. Zwölf-Linien-Drillform — Brot des Shaolin-Trainings. Auch der Federtritt selbst.")}
{g("Kinhin", "Gehmeditation der Chan-Tradition. Bringt innere Stille in Bewegung.")}

<h2 class="t2">Anatomie und Punkte</h2>
{g("Baihui", "Scheitelpunkt (GV20). Verbindung mit dem Yang des Himmels.")}
{g("Yongquan", "Sprudelnde Quelle (KD1). Im vorderen Fußdrittel. Erdungspunkt.")}
{g("Mingmen", "Tor des Lebens (GV4). Auf Höhe der Nieren — Sitz des vorgeburtlichen Qi.")}
{g("Nei Gong", "Innere Arbeit. Bewusste Lenkung von Yi und Qi durch den Körper.")}
{g("San Xiu", "Der dreifache Weg. Gleichzeitige Kultivierung von Körper, Atem und Geist.")}

<hr class="or">
<p style="text-align:center;font-size:9.5pt;color:#8B1A0E;font-style:italic;margin-top:5mm;line-height:1.85;">
Dieses Buch ist ein Werkzeug für die tägliche Praxis.<br>
Kein Buch ersetzt die direkte Erfahrung.<br>
Beginne. Bleibe dran. Gehe den ganzen Weg.</p>
<p style="text-align:center;font-size:14pt;color:#8B1A0E;margin-top:6mm;letter-spacing:5px;font-style:italic;">— SAN XIU —</p>
</div>'''

# ═══ RENDER ═════════════════════════════════════════════════════════════════

def render_part(sections, name):
    html = H() + ''.join(sections) + E
    tmp = f'/tmp/san_{name}.pdf'
    print(f"  Rendere {name} ({len(html):,} Zeichen)...", flush=True)
    t0 = time.time()
    HTML(string=html).write_pdf(tmp)
    print(f"  {name} fertig: {time.time()-t0:.1f}s", flush=True)
    return tmp

if __name__ == '__main__':
    print("SAN XIU — Das Buch | Start", flush=True)
    t_total = time.time()
    parts = [
        ('A', [cover(), titelblatt(), toc(), einleitung(), teil1()]),
        ('B', [teil2(), teil3()]),
        ('C', [teil4(), teil5()]),
        ('D', [teil6(), teil7()]),
        ('E', [teil8(), trainingsplan()]),
        ('F', [zitate(), glossar()]),
    ]
    pdfs = [render_part(s, n) for n, s in parts]
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
