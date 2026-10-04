"""
Procedural placeholder art: 4 realms x 3 depth layers (back / middle / front).
These only exist so the parallax slider works out of the box.
Replace them with the Nano Banana Pro images split by tools/split_layers.py.
Usage: python tools/make_placeholders.py   (needs numpy, opencv-python, pillow)
"""
import sys, math
import numpy as np
import cv2
from PIL import Image

W, H = 1920, 1080
OUT = sys.argv[1] if len(sys.argv) > 1 else "public/img/slides"


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def noise2d(h, w, scale, seed, octaves=5, pers=0.5):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh = max(2, int(h / scale * 2 ** o))
        gw = max(2, int(w / scale * 2 ** o))
        g = r.random((gh, gw)).astype(np.float32)
        out += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= pers
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def noise1d(w, scale, seed, octaves=6, pers=0.5, ridged=False):
    r = np.random.default_rng(seed)
    out = np.zeros(w, np.float32)
    amp, tot = 1.0, 0.0
    x = np.arange(w)
    for o in range(octaves):
        n = max(3, int(w / scale * 2 ** o))
        g = r.random(n).astype(np.float32)
        v = np.interp(x, np.linspace(0, w - 1, n), g)
        if ridged:
            v = 1 - np.abs(v * 2 - 1)
        out += amp * v
        tot += amp
        amp *= pers
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def vgrad(c1, c2, power=1.0, y0=0.0, y1=1.0):
    y = np.linspace(0, 1, H, dtype=np.float32)
    t = np.clip((y - y0) / (y1 - y0), 0, 1) ** power
    g = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    return np.repeat(g[:, None, :], W, axis=1)


def ridge_mask(line, feather=1.5):
    """line: array of y values (pixels) per x. mask = 1 below the line."""
    yy = np.arange(H, dtype=np.float32)[:, None]
    m = np.clip((yy - line[None, :]) / feather + 0.5, 0, 1)
    return m.astype(np.float32)


def poly_mask(polys, blur=0):
    m = np.zeros((H * 2, W * 2), np.uint8)
    for p in polys:
        pts = (np.array(p, np.float32) * 2).astype(np.int32)
        cv2.fillPoly(m, [pts], 255, lineType=cv2.LINE_AA)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    if blur:
        m = cv2.GaussianBlur(m, (0, 0), blur)
    return m


def stroke_mask(lines, width, blur=0):
    m = np.zeros((H * 2, W * 2), np.uint8)
    for pts in lines:
        p = (np.array(pts, np.float32) * 2).astype(np.int32)
        cv2.polylines(m, [p], False, 255, int(width * 2), lineType=cv2.LINE_AA)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    if blur:
        m = cv2.GaussianBlur(m, (0, 0), blur)
    return m


def over(dst_rgb, src_rgb, a):
    a = a[..., None]
    return dst_rgb * (1 - a) + src_rgb * a


def add_glow(rgb, mask, color, sigma, strength):
    g = cv2.GaussianBlur(mask, (0, 0), sigma)[..., None]
    return rgb + g * color[None, None, :] * strength


def texture(base, seed, amt=0.08, scale=60):
    n = noise2d(H, W, scale, seed, octaves=4)[..., None]
    return base * (1 - amt + n * amt * 2)


def bezier(p0, p1, p2, p3, n=80):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def dots(seed, count, ymin, ymax, rmin, rmax):
    r = np.random.default_rng(seed)
    m = np.zeros((H, W), np.uint8)
    for _ in range(count):
        x, y = int(r.uniform(0, W)), int(r.uniform(ymin, ymax))
        rad = int(r.uniform(rmin, rmax))
        cv2.circle(m, (x, y), max(1, rad), int(r.uniform(90, 255)), -1, lineType=cv2.LINE_AA)
    return m.astype(np.float32) / 255


def save(rgb, alpha, path):
    rgb = np.clip(rgb, 0, 1)
    if alpha is None:
        Image.fromarray((rgb * 255).astype(np.uint8), "RGB").save(path, "WEBP", quality=86, method=6)
    else:
        a = np.clip(alpha, 0, 1)
        arr = np.dstack([rgb, a])
        Image.fromarray((arr * 255).astype(np.uint8), "RGBA").save(path, "WEBP", quality=88, method=6)


def vignette(rgb, k=0.55):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = 1 - k * np.clip(d - 0.35, 0, 1) ** 1.6
    return rgb * v[..., None]


# ---------------------------------------------------------------- FROST
def frost():
    sky = vgrad(hexc("#06121D"), hexc("#3D6575"), 1.4, 0, 0.66)
    # aurora ribbons
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    aur = np.zeros((H, W), np.float32)
    for i, (amp, off, ph, wid) in enumerate([(60, 210, 0.0, 26), (45, 290, 1.7, 18), (35, 150, 3.1, 14)]):
        cy = off + amp * np.sin(xx / 260 + ph) + 25 * np.sin(xx / 90 + ph * 2)
        aur += np.exp(-((yy - cy) / wid) ** 2) * (0.9 - i * 0.2)
    curtain = noise2d(H, W, 40, 5, octaves=3)
    aur *= (0.45 + 0.8 * cv2.GaussianBlur(curtain, (0, 0), 3)) * np.clip(1 - yy / 520, 0, 1)
    sky += aur[..., None] * hexc("#54E3B4")[None, None, :] * 0.55
    sky += cv2.GaussianBlur(aur, (0, 0), 30)[..., None] * hexc("#2E9C93") * 0.35
    stars = dots(11, 380, 0, 560, 0.4, 1.3) * np.clip(1 - yy / 600, 0, 1)
    sky += stars[..., None] * 0.7

    back = sky
    # far glacier range
    far = H * 0.43 + (1 - noise1d(W, 520, 3, ridged=True)) * -170 + noise1d(W, 80, 4) * 30
    fm = ridge_mask(far)
    snow = np.clip(1 - (yy - far[None, :]) / 140, 0, 1) ** 1.5
    tex = noise2d(H, W, 30, 7, octaves=5)
    col = hexc("#3C5966")[None, None, :] * (1 - snow[..., None]) + hexc("#B9D5DD")[None, None, :] * snow[..., None]
    col *= (0.75 + 0.45 * tex[..., None])
    fog = np.clip((yy - far[None, :]) / 260, 0, 1)[..., None]
    col = col * (1 - fog * 0.7) + hexc("#5E8796") * fog * 0.7
    back = over(back, col, fm)
    # frozen sea plane
    sea_y = H * 0.66
    sm = np.clip((yy - sea_y) / 2, 0, 1)
    sea = vgrad(hexc("#6E95A2"), hexc("#1C3440"), 1.0, 0.66, 1.0)
    cracks = noise2d(H, W, 25, 9, octaves=5)
    cracks = np.exp(-((cracks - 0.5) / 0.012) ** 2) * np.clip((yy - sea_y) / 300, 0, 1)
    sea += cracks[..., None] * 0.35
    back = over(back, sea, sm)
    back = vignette(back, 0.5)

    # middle: ice shelf + wrecked longship
    mid_line = H * 0.70 + noise1d(W, 300, 21) * 70 - np.exp(-((np.arange(W) - 1350) / 260) ** 2) * 120
    mm = ridge_mask(mid_line, 2)
    mid = vgrad(hexc("#2C4A57"), hexc("#0D1A22"), 0.8, 0.6, 1.0)
    rim = np.clip(1 - (yy - mid_line[None, :]) / 18, 0, 1) * mm
    mid = texture(mid, 22, 0.18, 35) + rim[..., None] * hexc("#9CD3DF") * 0.55
    # longship hull tilted in the ice
    hull = bezier((1150, 640), (1250, 720), (1480, 705), (1600, 610), 60).tolist()
    hull += bezier((1600, 610), (1520, 670), (1290, 690), (1150, 640), 60).tolist()
    stem = bezier((1590, 615), (1625, 560), (1640, 520), (1615, 490), 30)
    hull_m = poly_mask([hull])
    stem_m = stroke_mask([stem], 9)
    mast = stroke_mask([[(1355, 690), (1330, 470)], [(1250, 540), (1420, 520)]], 6)
    sail = poly_mask([[(1332, 488), (1410, 522), (1395, 610), (1345, 600)]])
    ship_m = np.clip(hull_m + stem_m + mast + sail * 0.85, 0, 1)
    mid = over(mid, hexc("#0B141A") + 0 * mid, ship_m)
    mid_a = np.clip(mm + ship_m, 0, 1)

    # front: ice shards + snow
    r = np.random.default_rng(31)
    polys = []
    x = -40
    while x < W + 40:
        w = r.uniform(110, 240)
        edge_zone = x < 420 or x > 1480
        h = r.uniform(180, 420) if edge_zone else r.uniform(40, 120)
        tip = x + r.uniform(0.2, 0.8) * w
        polys.append([(x, H + 5), (tip, H - h), (x + w, H + 5)])
        x += w * r.uniform(0.45, 0.8)
    fm2 = poly_mask(polys)
    front = vgrad(hexc("#A6D3DD"), hexc("#0E202A"), 1.7, 0.6, 1.0)
    facet = (np.sin(xx / 23.0) * 0.5 + 0.5)[..., None]
    front = texture(front * (0.8 + 0.35 * facet), 33, 0.2, 20)
    edge = np.clip(fm2 - cv2.GaussianBlur(fm2, (0, 0), 4), 0, 1)
    front += edge[..., None] * hexc("#D8F4FA") * 0.5
    snow = dots(41, 260, 0, H, 0.8, 3.2)
    snow = cv2.GaussianBlur(snow, (0, 0), 1.1)
    front_rgb = front * (1 - snow[..., None]) + hexc("#E6F4F7") * snow[..., None]
    front_a = np.clip(fm2 + snow * 0.85, 0, 1)
    return back, (mid, mid_a), (front_rgb, front_a)


# ---------------------------------------------------------------- EMBER
def ember():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = vgrad(hexc("#0C0606"), hexc("#7C2A10"), 1.8, 0, 0.62)
    smoke = noise2d(H, W, 260, 51, octaves=6)
    sky = sky * (0.55 + 0.75 * smoke[..., None])
    glow = np.exp(-(((xx - 640) / 520) ** 2 + ((yy - 520) / 240) ** 2))
    sky += glow[..., None] * hexc("#FF7A2A") * 0.45
    back = sky
    # volcano
    vx = 640
    prof = np.clip(1 - np.abs(np.arange(W) - vx) / 900, 0, 1) ** 1.2
    far = H * 0.62 - prof * 330 + noise1d(W, 90, 52) * 40
    crater = np.abs(np.arange(W) - vx) < 70
    far[crater] += 26
    fm = ridge_mask(far)
    col = texture(np.zeros((H, W, 3), np.float32) + hexc("#24120D"), 53, 0.3, 25)
    rimg = np.clip(1 - (yy - far[None, :]) / 22, 0, 1)
    col += rimg[..., None] * hexc("#E2662A") * 0.35
    back = over(back, col, fm)
    plume = np.exp(-(((xx - vx - (yy - 300) * -0.15) / (60 + (300 - yy).clip(0) * 0.6)) ** 2)) * np.clip((300 - yy) / 300 + 0.2, 0, 1) * (yy < 300)
    back += plume[..., None] * hexc("#FF8A3A") * 0.25 * smoke[..., None]
    # plain + lava river
    plain_y = H * 0.64
    pm = np.clip((yy - plain_y) / 2, 0, 1)
    plain = texture(vgrad(hexc("#1E0F0B"), hexc("#0B0504"), 1, 0.64, 1), 55, 0.35, 30)
    t = np.linspace(0, 1, 120)
    riv = np.stack([200 + t * 1500 + 120 * np.sin(t * 9), plain_y + 10 + t * 360 + 30 * np.sin(t * 5)], 1)
    lava = stroke_mask([riv], 8)
    lava_wide = stroke_mask([riv], 26, blur=6)
    plain = add_glow(plain, lava_wide, hexc("#FF5A12"), 20, 0.9)
    plain = over(plain, hexc("#FFC15A") + 0 * plain, lava)
    plain = over(plain, hexc("#FF6A1A") + 0 * plain, np.clip(lava_wide - lava, 0, 1) * 0.8)
    back = over(back, plain, pm)
    back = vignette(back, 0.6)

    # middle: ruined forge — giant anvil on a basalt shelf + pillars
    shelf = H * 0.74 + noise1d(W, 260, 61) * 50
    sm = ridge_mask(shelf, 2)
    anvil = [[(1180, 700), (1240, 610), (1180, 585), (1270, 560), (1560, 560), (1660, 600), (1560, 612), (1520, 640), (1580, 700)]]
    pill = [[(260, 760), (270, 360), (330, 330), (360, 760)], [(420, 760), (430, 470), (480, 450), (505, 760)],
            [(1760, 760), (1772, 420), (1830, 400), (1850, 760)]]
    shapes = poly_mask(anvil + pill)
    mm = np.clip(sm + shapes, 0, 1)
    mid = texture(np.zeros((H, W, 3), np.float32) + hexc("#150A07"), 62, 0.35, 18)
    under = np.clip((yy - 500) / 420, 0, 1)
    edge = np.clip(mm - cv2.GaussianBlur(mm, (0, 0), 3), 0, 1)
    mid += edge[..., None] * hexc("#FF7A2A") * (0.6 + under[..., None])
    chains = stroke_mask([bezier((1300, 560), (1290, 470), (1260, 420), (1240, 300)),
                          bezier((1500, 560), (1530, 460), (1580, 400), (1620, 260))], 5)
    mid = over(mid, hexc("#120806") + 0 * mid, chains)
    mid_a = np.clip(mm + chains, 0, 1)

    # front: obsidian boulders with glowing seams + embers
    r = np.random.default_rng(71)
    polys = []
    for cx, base_r in [(120, 260), (420, 170), (1500, 190), (1800, 300), (980, 110)]:
        n = 11
        ang = np.linspace(0, 2 * np.pi, n, endpoint=False) + r.uniform(0, 0.3)
        rad = base_r * r.uniform(0.7, 1.1, n)
        pts = [(cx + math.cos(a) * rr * 1.3, H + 40 + math.sin(a) * rr) for a, rr in zip(ang, rad)]
        polys.append(pts)
    bm = poly_mask(polys)
    front = texture(np.zeros((H, W, 3), np.float32) + hexc("#0D0706"), 72, 0.4, 14)
    seams = noise2d(H, W, 90, 73, octaves=4)
    seams = np.exp(-((seams - 0.5) / 0.006) ** 2) * bm
    front = add_glow(front, seams, hexc("#FF6A1A"), 4, 1.2)
    front = over(front, hexc("#FFB04A") + 0 * front, seams * 0.9)
    edge = np.clip(bm - cv2.GaussianBlur(bm, (0, 0), 3), 0, 1)
    front += edge[..., None] * hexc("#FF8A3A") * 0.7
    emb = cv2.GaussianBlur(dots(81, 170, 0, H * 0.9, 0.8, 2.6), (0, 0), 1.2)
    front_rgb = over(front, hexc("#FFB46A") + 0 * front, emb)
    front_a = np.clip(bm + emb, 0, 1)
    return back, (mid, mid_a), (front_rgb, front_a)


# ---------------------------------------------------------------- ROOTS
def roots():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = vgrad(hexc("#0E1712"), hexc("#6E846C"), 1.1, 0, 0.75)
    mist = noise2d(H, W, 300, 91, octaves=5)
    sky = sky * (0.75 + 0.45 * mist[..., None])
    # light shafts
    shafts = np.zeros((H, W), np.float32)
    for x0, w0 in [(820, 40), (980, 70), (1120, 30), (700, 22)]:
        xx0 = x0 + (yy) * 0.42
        shafts += np.exp(-((xx - xx0) / w0) ** 2) * np.clip(1 - yy / 900, 0, 1)
    sky += shafts[..., None] * hexc("#E8E2B0") * 0.22
    back = sky
    # distant colossal trunks
    tm = poly_mask([[(1420, -10), (1600, -10), (1640, 760), (1380, 760)],
                    [(240, -10), (330, -10), (350, 760), (205, 760)]], blur=2)
    trunk = texture(np.zeros((H, W, 3), np.float32) + hexc("#3E4F3F"), 92, 0.3, 30)
    back = over(back, trunk, tm * 0.75)
    floor_y = H * 0.70
    fl = np.clip((yy - floor_y) / 60, 0, 1)
    back = over(back, texture(vgrad(hexc("#4A5C47"), hexc("#18221A"), 1, 0.7, 1), 93, 0.3, 25), fl)
    back = vignette(back, 0.55)

    # middle: huge arching roots + rune stone
    root_lines = [bezier((-60, 560), (300, 300), (700, 360), (900, 780), 120),
                  bezier((2000, 520), (1650, 260), (1250, 330), (1080, 800), 120),
                  bezier((-60, 760), (380, 620), (620, 700), (760, 900), 120)]
    rm = np.zeros((H, W), np.float32)
    for i, ln in enumerate(root_lines):
        rm = np.maximum(rm, stroke_mask([ln], [70, 85, 55][i]))
    ground = ridge_mask(H * 0.80 + noise1d(W, 200, 95) * 40, 2)
    stone = poly_mask([[(930, 800), (945, 560), (1000, 520), (1050, 545), (1065, 800)]])
    mm = np.clip(rm + ground + stone, 0, 1)
    mid = texture(np.zeros((H, W, 3), np.float32) + hexc("#1A231B"), 96, 0.35, 16)
    bark = noise2d(H, W, 12, 97, octaves=3)
    mid *= (0.8 + 0.4 * bark[..., None])
    top_light = np.clip(mm - np.roll(cv2.GaussianBlur(mm, (0, 0), 3), 6, axis=0), 0, 1)
    mid += top_light[..., None] * hexc("#B9C78C") * 0.5
    runes = stroke_mask([[(975, 600), (975, 650), (995, 630)], [(1015, 590), (1030, 615), (1015, 640)],
                         [(980, 680), (1000, 700), (1020, 680), (1000, 660)], [(1030, 670), (1030, 720)]], 3)
    mid = add_glow(mid, runes, hexc("#E8D27A"), 8, 1.6)
    mid = over(mid, hexc("#FFE8A0") + 0 * mid, runes)
    mid_a = np.clip(mm + cv2.GaussianBlur(runes, (0, 0), 8) * 0.6, 0, 1)

    # front: fern fronds in bottom corners
    r = np.random.default_rng(101)
    lines = []
    for side in (0, 1):
        for _ in range(16):
            bx = (r.uniform(-40, 420) if side == 0 else r.uniform(1500, 1960))
            ang = (r.uniform(-1.35, -0.55) if side == 0 else r.uniform(-2.6, -1.8))
            L = r.uniform(220, 420)
            ex, ey = bx + math.cos(ang) * L, H + 20 + math.sin(ang) * L
            curve = bezier((bx, H + 20), (bx + math.cos(ang) * L * 0.4, H + 20 + math.sin(ang) * L * 0.5),
                           (ex - (40 if side == 0 else -40), ey - 30), (ex, ey), 40)
            lines.append(curve)
            for k in range(4, 38, 2):
                px, py = curve[k]
                d = curve[min(k + 1, 39)] - curve[k]
                n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
                ll = 46 * (1 - k / 40) + 8
                lines.append([(px, py), (px + n[0] * ll + d[0] * 3, py + n[1] * ll + d[1] * 3)])
                lines.append([(px, py), (px - n[0] * ll + d[0] * 3, py - n[1] * ll + d[1] * 3)])
    fm2 = stroke_mask(lines, 4)
    floor = ridge_mask(H * 0.93 + noise1d(W, 120, 103) * 30, 2)
    fm2 = np.clip(fm2 + floor, 0, 1)
    front = texture(np.zeros((H, W, 3), np.float32) + hexc("#0A110B"), 104, 0.3, 10)
    front += np.clip(fm2 - cv2.GaussianBlur(fm2, (0, 0), 2), 0, 1)[..., None] * hexc("#5E7A4A") * 0.6
    spores = cv2.GaussianBlur(dots(111, 90, 100, H * 0.9, 0.8, 2.2), (0, 0), 1.4)
    front_rgb = over(front, hexc("#F2E6A6") + 0 * front, spores)
    front_a = np.clip(fm2 + spores * 0.8, 0, 1)
    return back, (mid, mid_a), (front_rgb, front_a)


# ---------------------------------------------------------------- STORM
def storm():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = vgrad(hexc("#0D0B1A"), hexc("#4B4675"), 1.3, 0, 0.65)
    cl = noise2d(H, W, 220, 121, octaves=6)
    sky *= (0.55 + 0.8 * cl[..., None])
    # lightning
    r = np.random.default_rng(122)
    pts = [(1260, -10)]
    x, y = 1260, -10
    while y < 520:
        y += r.uniform(30, 60)
        x += r.uniform(-45, 45)
        pts.append((x, y))
    branch = [pts[5]]
    bx, by = pts[5]
    for _ in range(5):
        by += r.uniform(25, 45)
        bx += r.uniform(10, 50)
        branch.append((bx, by))
    bolt = stroke_mask([pts, branch], 3)
    sky = add_glow(sky, bolt, hexc("#B9AEFF"), 26, 2.4)
    sky = add_glow(sky, bolt, hexc("#E8E4FF"), 6, 1.5)
    sky = over(sky, np.ones_like(sky), bolt)
    back = sky
    far = H * 0.58 - noise1d(W, 380, 123, ridged=True) * 210 - noise1d(W, 60, 124) * 25
    fm = ridge_mask(far)
    col = texture(np.zeros((H, W, 3), np.float32) + hexc("#2B2846"), 125, 0.3, 30)
    fog = np.clip((yy - far[None, :]) / 280, 0, 1)[..., None]
    col = col * (1 - fog * 0.6) + hexc("#57527E") * fog * 0.6
    back = over(back, col, fm)
    far2 = H * 0.68 - noise1d(W, 260, 126, ridged=True) * 140
    col2 = texture(np.zeros((H, W, 3), np.float32) + hexc("#1E1C33"), 127, 0.3, 25)
    back = over(back, col2, ridge_mask(far2))
    back = vignette(back, 0.55)

    # middle: summit with ring of standing stones
    summit = H * 0.80 - np.exp(-((np.arange(W) - 760) / 520) ** 2) * 120 + noise1d(W, 120, 131) * 30
    sm = ridge_mask(summit, 2)
    stones = []
    for sx, sh, sw in [(430, 170, 46), (560, 220, 52), (700, 250, 58), (860, 205, 50), (1000, 160, 42), (300, 120, 36)]:
        base = summit[int(sx)] + 10
        stones.append([(sx - sw / 2, base), (sx - sw / 2 + 6, base - sh), (sx + sw / 2 - 4, base - sh - 14), (sx + sw / 2, base)])
    lintel = [[(530, summit[560] - 210), (742, summit[700] - 262), (745, summit[700] - 236), (532, summit[560] - 186)]]
    stm = poly_mask(stones + lintel)
    mm = np.clip(sm + stm, 0, 1)
    mid = texture(np.zeros((H, W, 3), np.float32) + hexc("#15131F"), 132, 0.35, 14)
    rimL = np.clip(mm - np.roll(cv2.GaussianBlur(mm, (0, 0), 3), -5, axis=1), 0, 1)
    mid += rimL[..., None] * hexc("#B7AEF5") * 0.7
    mid_a = mm

    # front: rock ledge + hooded wanderer with spear, rain
    ledge = poly_mask([[(1180, H + 10), (1260, 900), (1420, 860), (1600, 870), (1760, 820), (1960, 840), (1960, H + 10)],
                       [(-20, H + 10), (-20, 930), (180, 960), (360, 1010), (420, H + 10)]])
    # figure on ledge at x~1560, feet at y~866
    fx, fy = 1560, 868
    cloak = [(fx - 52, fy), (fx - 34, fy - 120), (fx - 24, fy - 165), (fx, fy - 186), (fx + 24, fy - 166),
             (fx + 36, fy - 120), (fx + 58, fy), (fx + 10, fy + 4)]
    hood = [(fx - 22, fy - 168), (fx - 16, fy - 205), (fx + 2, fy - 222), (fx + 20, fy - 206), (fx + 24, fy - 170)]
    fur = [(fx - 42, fy - 150), (fx, fy - 172), (fx + 44, fy - 148), (fx + 30, fy - 132), (fx - 30, fy - 132)]
    fig = poly_mask([cloak, hood, fur])
    spear = stroke_mask([[(fx + 44, fy + 6), (fx + 70, fy - 300)]], 4)
    tip = poly_mask([[(fx + 64, fy - 298), (fx + 78, fy - 300), (fx + 74, fy - 340)]])
    fm2 = np.clip(ledge + fig + spear + tip, 0, 1)
    front = texture(np.zeros((H, W, 3), np.float32) + hexc("#0B0A12"), 141, 0.3, 12)
    rim = np.clip(fm2 - np.roll(cv2.GaussianBlur(fm2, (0, 0), 2.5), -4, axis=1), 0, 1)
    front += rim[..., None] * hexc("#C9C2F2") * 0.9
    rain = np.zeros((H, W), np.uint8)
    rr = np.random.default_rng(151)
    for _ in range(700):
        x0, y0 = rr.uniform(-200, W), rr.uniform(-50, H)
        L = rr.uniform(18, 46)
        cv2.line(rain, (int(x0), int(y0)), (int(x0 + L * 0.35), int(y0 + L)), int(rr.uniform(60, 160)), 1, cv2.LINE_AA)
    rain = rain.astype(np.float32) / 255
    front_rgb = over(front, hexc("#C8C6E8") + 0 * front, rain)
    front_a = np.clip(fm2 + rain * 0.6, 0, 1)
    return back, (mid, mid_a), (front_rgb, front_a)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    for i, fn in enumerate([frost, ember, roots, storm], start=1):
        back, (mid, ma), (front, fa) = fn()
        save(back, None, f"{OUT}/slide-{i}-layer-back.webp")
        save(mid, ma, f"{OUT}/slide-{i}-layer-middle.webp")
        save(front, fa, f"{OUT}/slide-{i}-layer-front.webp")
        print(f"slide {i}: placeholder layers written")
