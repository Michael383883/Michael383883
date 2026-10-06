#!/usr/bin/env python3
"""Snake Pro: genera un SVG arcade neon con tus contribuciones reales.
Uso: GH_USER=tu_usuario GH_TOKEN=... python generate.py   (o: python generate.py --demo)"""
import os, sys, json, math, random, urllib.request
USER = os.environ.get("GH_USER", "Michael383883")
TOKEN = os.environ.get("GH_PAT") or os.environ.get("GH_TOKEN", "")
OUT = os.environ.get("OUT", "dist/snake-pro.svg")
MONO = "'Fira Code','JetBrains Mono','Courier New',monospace"

def fetch():
    q = "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount weekday}}}}}}"
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "snake-pro"})
    with urllib.request.urlopen(req, timeout=30) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[(x["weekday"], x["contributionCount"]) for x in w["contributionDays"]] for w in cal["weeks"]]
    return cal["totalContributions"], weeks

def demo():
    random.seed(3)
    weeks = [[(d, 0 if random.random() < .45 else random.randint(1, 12)) for d in range(7)] for _ in range(53)]
    weeks[-1] = weeks[-1][:3]
    return sum(c for w in weeks for _, c in w), weeks

def mix(a, b, t):
    pa = [int(a[i:i+2], 16) for i in (1, 3, 5)]; pb = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x+(y-x)*t):02x}" for x, y in zip(pa, pb))

def build(total, weeks):
    P, C, X0, Y0 = 17, 14, 30, 64
    nw = len(weeks); W = 2*X0 + nw*P; H = Y0 + 7*P + 58
    mx = max((c for w in weeks for _, c in w), default=1) or 1
    lvl = lambda c: 0 if c == 0 else min(4, math.ceil(4*c/mx))
    COL = ["#161b22", "#0e7490", "#06b6d4", "#22d3ee", "#a5f3fc"]
    cells = []
    for wi, days in enumerate(weeks):
        ds = sorted(days)
        if wi % 2: ds = ds[::-1]
        for d, c in ds: cells.append((wi, d, c, X0+wi*P+C/2, Y0+d*P+C/2))
    cum = [0.0]
    for i in range(1, len(cells)):
        cum.append(cum[-1] + math.hypot(cells[i][3]-cells[i-1][3], cells[i][4]-cells[i-1][4]))
    SPEED = 17/0.055; travel = cum[-1]/SPEED; D = travel + 3.0; f = travel/D
    dur = f'dur="{D:.2f}s" repeatCount="indefinite"'
    path = "M" + " L".join(f"{c[3]:.1f},{c[4]:.1f}" for c in cells)
    # celdas + explosiones
    cl, fx = [], []
    for i, (wi, d, c, cx, cy) in enumerate(cells):
        x, y, L = X0+wi*P, Y0+d*P, lvl(c)
        if L == 0:
            cl.append(f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="3" fill="{COL[0]}"/>'); continue
        a = max(cum[i]/SPEED - .03, .01)/D; r = (D-.5)/D
        cl.append(f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="3" fill="{COL[L]}"><animate attributeName="fill" values="{COL[L]};{COL[0]};{COL[L]}" keyTimes="0;{a:.4f};{r:.4f}" calcMode="discrete" {dur}/></rect>')
        b = a + .55/D
        fx.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0" fill="none" stroke="#fff" stroke-width="2" opacity="0"><animate attributeName="r" values="0;0;{9+L*3};{9+L*3}" keyTimes="0;{a:.4f};{b:.4f};1" {dur}/><animate attributeName="opacity" values="0;.9;0;0" keyTimes="0;{a:.4f};{b:.4f};1" {dur}/></circle>')
    # marcador (score)
    NCP = 24; ev = [(cum[i]/SPEED, cells[i][2]) for i in range(len(cells))]; sc = []
    for j in range(NCP+1):
        s = j*travel/NCP/D; e = (j+1)*travel/NCP/D
        if j == NCP: txt, vals, kts = f"STAGE CLEAR  {total:,}", "0;1", f"0;{s:.4f}"
        else:
            n = sum(c for t, c in ev if t <= j*travel/NCP); txt = f"SCORE {n:,}"
            vals, kts = ("1;0", f"0;{e:.4f}") if j == 0 else ("0;1;0", f"0;{s:.4f};{e:.4f}")
        sc.append(f'<text x="{W-X0}" y="38" text-anchor="end" font-family="{MONO}" font-size="15" font-weight="700" fill="#ffd166" opacity="0"><animate attributeName="opacity" values="{vals}" keyTimes="{kts}" calcMode="discrete" {dur}/>{txt}</text>')
    # serpiente
    N, lag = 14, 15/SPEED; seg = []
    for k in range(N):
        sz = 15 - k*.55; col = mix("#ff4fd8", "#22d3ee", k/(N-1)); b = f"{k*lag:.3f}s"
        eyes = '<circle cx="3" cy="-3.2" r="2" fill="#fff"/><circle cx="3" cy="3.2" r="2" fill="#fff"/><circle cx="3.7" cy="-3.2" r="1" fill="#111"/><circle cx="3.7" cy="3.2" r="1" fill="#111"/>' if k == 0 else ""
        seg.append(f'<g opacity="0"><animateMotion dur="{D:.2f}s" begin="{b}" repeatCount="indefinite" rotate="{"auto" if k == 0 else "0"}" calcMode="linear" keyPoints="0;1;1" keyTimes="0;{f:.4f};1"><mpath xlink:href="#sp"/></animateMotion>'
                   f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{f:.4f};{f+.002:.4f};1" dur="{D:.2f}s" begin="{b}" repeatCount="indefinite"/>'
                   f'<rect x="{-sz/2:.1f}" y="{-sz/2:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="{sz*.32:.1f}" fill="{col}" filter="url(#glow)"/>{eyes}</g>')
    # portales
    def portal(c, col):
        return (f'<g transform="translate({c[3]:.1f},{c[4]:.1f})"><circle r="11" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="4 4" filter="url(#glow)">'
                f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite"/></circle></g>')
    random.seed(11)
    stars = "".join(f'<circle cx="{random.randint(8, W-8)}" cy="{random.randint(8, H-8)}" r="{random.uniform(.6, 1.6):.1f}" fill="#fff" opacity=".1"><animate attributeName="opacity" values=".08;.7;.08" dur="{random.uniform(2, 6):.1f}s" begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>' for _ in range(40))
    leg = "".join(f'<rect x="{W-X0-60+i*13}" y="{H-34}" width="10" height="10" rx="2" fill="{COL[i]}"/>' for i in range(5))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#fff" opacity=".035"/></pattern>'
        f'<path id="sp" d="{path}" fill="none"/></defs>'
        f'<rect width="{W}" height="{H}" rx="16" fill="#0b0f1a"/>{stars}'
        f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="15" fill="none" stroke="#7c3aed" stroke-width="2"><animate attributeName="stroke" values="#7c3aed;#06b6d4;#ff4fd8;#7c3aed" dur="8s" repeatCount="indefinite"/></rect>'
        f'<text x="{X0}" y="38" font-family="{MONO}" font-size="15" font-weight="700" fill="#ff4fd8" filter="url(#glow)">&gt; SNAKE.EXE</text>'
        f'<text x="{X0+130}" y="38" font-family="{MONO}" font-size="12" fill="#6e7681">@{USER}</text>{"".join(sc)}'
        f'{"".join(cl)}{portal(cells[0], "#7cffb2")}{portal(cells[-1], "#ff4fd8")}{"".join(fx)}{"".join(seg)}'
        f'<text x="{X0}" y="{H-25}" font-family="{MONO}" font-size="12" fill="#6e7681">{total:,} contributions en el ultimo anio</text>'
        f'<text x="{W-X0-68}" y="{H-25}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#6e7681">Menos</text>{leg}'
        f'<text x="{W-X0+2}" y="{H-25}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#6e7681">Mas</text>'
        f'<rect width="{W}" height="{H}" rx="16" fill="url(#sl)"/></svg>')

if __name__ == "__main__":
    total, weeks = demo() if "--demo" in sys.argv else fetch()
    svg = build(total, weeks)
    from xml.dom import minidom; minidom.parseString(svg)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print(f"OK -> {OUT} ({len(svg)//1024} KB, {total} contribuciones)")
