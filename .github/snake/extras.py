#!/usr/bin/env python3
"""Genera activity.svg (grafica animada) y trophies.svg (trofeos) con tus datos reales.
Uso: GH_USER=usuario GH_TOKEN=... python extras.py   (o: python extras.py --demo)"""
import os, sys, json, math, random, urllib.request
USER = os.environ.get("GH_USER", "Michael383883")
TOKEN = os.environ.get("GH_PAT") or os.environ.get("GH_TOKEN", "")
OUTDIR = os.environ.get("OUTDIR", "dist")
MONO = "'Fira Code','JetBrains Mono','Courier New',monospace"
SANS = "'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

def fetch():
    q = ("query($u:String!){user(login:$u){followers{totalCount} repositories(ownerAffiliations:[OWNER],first:100,privacy:PUBLIC){totalCount nodes{stargazerCount}} "
         "pullRequests{totalCount} issues{totalCount} contributionsCollection{totalCommitContributions contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}}}")
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "snake-pro"})
    with urllib.request.urlopen(req, timeout=30) as r: u = json.load(r)["data"]["user"]
    cc = u["contributionsCollection"]; cal = cc["contributionCalendar"]
    weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    stats = {"Commits": cc["totalCommitContributions"], "Pull Requests": u["pullRequests"]["totalCount"], "Issues": u["issues"]["totalCount"],
             "Repositorios": u["repositories"]["totalCount"], "Estrellas": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]), "Seguidores": u["followers"]["totalCount"]}
    return cal["totalContributions"], weeks, stats

def demo():
    random.seed(5); weeks = []
    for w in range(53):
        m = (w*12)//53 + 1
        weeks.append([(f"2025-{m:02d}-{d+1:02d}", 0 if random.random() < .4 else random.randint(1, 9)) for d in range(7)])
    return sum(c for w in weeks for _, c in w), weeks, {"Commits": 842, "Pull Requests": 12, "Issues": 3, "Repositorios": 9, "Estrellas": 4, "Seguidores": 0}

def activity(total, weeks):
    W, H, L, R, T, B = 900, 300, 50, 30, 70, 50
    vals = [sum(c for _, c in w) for w in weeks]; n = len(vals); mx = max(vals) or 1
    step = max(1, math.ceil(mx/4)); top = step*4
    X = lambda i: L + (W-L-R)*i/(n-1); Y = lambda v: T + (H-T-B)*(1-v/top)
    pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
    cl = lambda y: min(max(y, T), H-B)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n-1):
        p0 = pts[i-1] if i else pts[i]; p1, p2 = pts[i], pts[i+1]; p3 = pts[i+2] if i+2 < n else p2
        d += f" C{p1[0]+(p2[0]-p0[0])/6:.1f},{cl(p1[1]+(p2[1]-p0[1])/6):.1f} {p2[0]-(p3[0]-p1[0])/6:.1f},{cl(p2[1]-(p3[1]-p1[1])/6):.1f} {p2[0]:.1f},{p2[1]:.1f}"
    D = 9; k = .4; dur = f'dur="{D}s" repeatCount="indefinite"'
    grid = "".join(f'<line x1="{L}" x2="{W-R}" y1="{Y(step*g):.1f}" y2="{Y(step*g):.1f}" stroke="#21262d" stroke-dasharray="3 5"/><text x="{L-10}" y="{Y(step*g)+4:.1f}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#6e7681">{step*g}</text>' for g in range(5))
    meses, prev = "", None
    for i, w in enumerate(weeks):
        m = int(w[0][0][5:7])
        if m != prev: meses += f'<text x="{X(i):.1f}" y="{H-B+24}" font-family="{MONO}" font-size="11" fill="#6e7681">{MES[m-1]}</text>'
        prev = m
    pk = vals.index(max(vals)); px, py = pts[pk]; tx = min(max(px, L+40), W-R-40)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
      f'<defs><linearGradient id="ls" gradientUnits="userSpaceOnUse" x1="{L}" y1="0" x2="{W-R}" y2="0"><stop offset="0" stop-color="#00f7ff"/><stop offset=".55" stop-color="#a78bfa"/><stop offset="1" stop-color="#ff4fd8"/></linearGradient>'
      '<linearGradient id="af" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a78bfa" stop-opacity=".45"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>'
      '<filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
      f'<rect width="{W}" height="{H}" rx="16" fill="#0b0f1a"/><rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="15" fill="none" stroke="#30363d" stroke-width="2"><animate attributeName="stroke" values="#30363d;#7c3aed;#06b6d4;#30363d" dur="8s" repeatCount="indefinite"/></rect>'
      f'<text x="{L}" y="38" font-family="{MONO}" font-size="15" font-weight="700" fill="#00f7ff" filter="url(#gl)">&gt; ACTIVITY.LOG</text>'
      f'<text x="{W-R}" y="38" text-anchor="end" font-family="{MONO}" font-size="13" fill="#ffd166">{total:,} contribuciones / 12 meses</text>{grid}{meses}'
      f'<path d="{d} L{pts[-1][0]:.1f},{Y(0):.1f} L{pts[0][0]:.1f},{Y(0):.1f} Z" fill="url(#af)" opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;.15;{k+.1};1" {dur}/></path>'
      f'<path id="ln" d="{d}" pathLength="1" fill="none" stroke="url(#ls)" stroke-width="3" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1" filter="url(#gl)"><animate attributeName="stroke-dashoffset" values="1;0;0" keyTimes="0;{k};1" {dur}/></path>'
      f'<circle r="6" fill="#fff" filter="url(#gl)"><animateMotion calcMode="linear" keyPoints="0;1;1" keyTimes="0;{k};1" {dur}><mpath xlink:href="#ln"/></animateMotion></circle>'
      f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{k};{k+.05};1" {dur}/><circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#ffd166" filter="url(#gl)"><animate attributeName="r" values="4;9;4" dur="2s" repeatCount="indefinite"/></circle>'
      f'<text x="{tx:.1f}" y="{max(py-16, 56):.1f}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="#ffd166">PICO: {vals[pk]}</text></g></svg>')

TH = {"Commits": [1,50,200,500,1500], "Pull Requests": [1,5,20,50,200], "Issues": [1,5,20,50,200], "Repositorios": [1,5,15,30,60], "Estrellas": [1,5,20,100,500], "Seguidores": [1,5,20,50,200]}
TIER = ["BLOQUEADO","BRONCE","PLATA","ORO","PLATINO","DIAMANTE"]; TCOL = ["#30363d","#cd7f32","#c0c8d4","#ffd166","#7dd3fc","#c084fc"]

def trophies(stats):
    CW, G, H = 135, 18, 190; W = 6*CW + 5*G; out = ""
    for i, (name, v) in enumerate(stats.items()):
        r = sum(1 for t in TH[name] if v >= t); c = TCOL[r]; x = i*(CW+G); dl = f"{i*.15:.2f}s"
        fl = ' filter="url(#gl)"' if r else ""
        icon = (f'<g transform="translate({CW/2},50)"{fl}>' + (f'<animateTransform attributeName="transform" type="translate" additive="sum" values="0 0;0 -4;0 0" dur="{2.5+i*.3:.1f}s" repeatCount="indefinite"/>' if r else "") +
                f'<path d="M-13,-16 H13 V-4 C13,6 6,12 0,12 C-6,12 -13,6 -13,-4 Z" fill="{c}"/>'
                f'<path d="M-13,-12 H-20 C-20,-2 -16,2 -11,3 M13,-12 H20 C20,-2 16,2 11,3" fill="none" stroke="{c}" stroke-width="3"/>'
                f'<rect x="-3" y="12" width="6" height="7" fill="{c}"/><rect x="-10" y="19" width="20" height="5" rx="2" fill="{c}"/></g>')
        dots = "".join(f'<circle cx="{CW/2-24+j*12}" cy="172" r="3.5" fill="{TCOL[r] if j < r else "#21262d"}"/>' for j in range(5))
        out += (f'<g transform="translate({x},0)"><g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{dl}" dur=".5s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="0 24" to="0 0" begin="{dl}" dur=".5s" fill="freeze"/>'
                f'<rect x="1" y="1" width="{CW-2}" height="{H-2}" rx="12" fill="#0d1117" stroke="{c}" stroke-width="2">' + (f'<animate attributeName="stroke-opacity" values=".45;1;.45" dur="3s" repeatCount="indefinite"/>' if r else "") + '</rect>'
                f'{icon}<text x="{CW/2}" y="110" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="700" fill="#e6edf3">{v:,}</text>'
                f'<text x="{CW/2}" y="132" text-anchor="middle" font-family="{SANS}" font-size="13" fill="#8b949e">{name}</text>'
                f'<text x="{CW/2}" y="153" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="{c}">{TIER[r]}</text>{dots}</g></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs><filter id="gl" x="-60%" y="-60%" width="220%" height="220%">'
            f'<feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>{out}</svg>')

if __name__ == "__main__":
    total, weeks, stats = demo() if "--demo" in sys.argv else fetch()
    from xml.dom import minidom
    os.makedirs(OUTDIR, exist_ok=True)
    for name, svg in (("activity.svg", activity(total, weeks)), ("trophies.svg", trophies(stats))):
        minidom.parseString(svg); open(os.path.join(OUTDIR, name), "w", encoding="utf-8").write(svg); print("OK ->", name, len(svg)//1024, "KB")
