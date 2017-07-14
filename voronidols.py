#!/usr/bin/env python

import random, subprocess, argparse, itertools

COLORFILE = './rgb.txt'
NC = 4
NP = 20
SCALE = 8
PSCALE = 4

def mkcolours(cl=None, mono=False):
    colours = []

    if cl:
        colours = cl.split(',')
    else:
        with open(COLORFILE, 'r') as cf:
            for line in cf:
                if line[0] == '#':
                    next
                parts = line[:-1].split()
                if len(parts) == 4:
                    if mono:
                        if parts[0] == parts[1] and parts[1] == parts[2]:
                            colours.append(parts[3])
                    else:
                        colours.append(parts[3])
    return colours

def randpt():
    x = random.uniform(0, 1)
    y = random.uniform(0, 1)
    return (x, y)

def pt(x, y, c):
    return "{},{} {}".format(x, y, c)


def makepts(w, h, cs, n, s):
    pts = []
    for c in itertools.cycle(cs):
        x, y = randpt()
        pts.append((x, y, c)) 
        if s == 'vertical' or s == 'both':
            pts.append((1 - x, y, c))
        if s == 'horizontal' or s == 'both':
            pts.append((x, 1 - y, c))
        if s == 'both' or s == 'rot2' or s == 'rot4':
            pts.append((1 - x, 1 - y, c))
        if s == 'rot4':
            pts.append((y, 1 - x, c))
            pts.append((1 - y, x, c))
        if len(pts) >= n:
            break
    spts = []
    x0 = w * SCALE / 2
    y0 = h * SCALE / 2
    xk = w * PSCALE
    yk = h * PSCALE
    for x, y, c in pts:
        u = x0 + xk * (x - .5)
        v = y0 + yk * (y - .5)
        spts.append(pt(u, v, c))
    return "'" + ' '.join(spts) + "'"


def sparse(w, h, algorithm, points, filename):
    geom = '{}x{}'.format(w * SCALE, h * SCALE)
    scale = '{}%'.format(100 / SCALE)
    im = [ 'convert', '-size', geom, 'xc:', '-sparse-color', algorithm, points, '-scale', scale, filename ]
    cmd = ' '.join(im)
    #print(cmd)
    rv = subprocess.run(cmd, shell=True)
    return (not rv)


def voronidol(w, h, npoints, symmetry, ncols, cols, output, **kwargs):
    geometry = "{}x{}".format(w, h)
    cs = random.sample(cols, ncols)
    points = makepts(w, h, cs, npoints, symmetry)
    if 'algorithm' in kwargs:
        alg = kwargs.algorithm
    else:
        alg = 'Voronoi'
    if 'blgorithm' in kwargs:
        sparse(w, h, alg, points, 'a1.jpg')
        sparse(w, h, kwargs.blgorithm, points, 'b1.jpg')
        merge = [ 'composite', '-blend', '50', 'a1.jpg', 'b1.jpg', output]
        rv = subprocess.run(' '.join(merge), shell=True)
    else:
        sparse(w, h, alg, points, output)

    if 'gradient' in kwargs:
        grad = [ 'convert', '-size', geometry, kwargs.gradient, 'fade.jpg' ]
        subprocess.run(' '.join(grad), shell=True)
        merge = [ 'composite', '-blend', '50', 'fade.jpg', output, output ]
        subprocess.run(' '.join(merge), shell=True)

    if 'blur' in kwargs:
        blur = [ 'convert', '-blur', kwargs.blur, output, output ]
        rv = subprocess.run(' '.join(kwargs.blur), shell=True)

    ensure_col = [ 'convert', output, '-colorspace', 'rgb', '-type', 'truecolor', output ]
    rv = subprocess.run(' '.join(ensure_col), shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a voronoi map')
    parser.add_argument('-x', '--width', type=int, default=XMAX, help="canvas width")
    parser.add_argument('-y', '--height', type=int, default=YMAX, help="canvas height")
    parser.add_argument('-a', '--algorithm', type=str, default='Voronoi', help='sparse algorithm 1')
    parser.add_argument('-b', '--blgorithm', type=str, default=None, help='sparse algorithm 2')
    parser.add_argument('-c', '--colours', type=int, default=NC, help='number of colours')
    parser.add_argument('-e', '--monochrome', action='store_true', help='grayscale only')
    parser.add_argument('-n', '--points', type=int, default=NP, help='number of points')
    parser.add_argument('-u', '--blur', type=str, help='blur')
    parser.add_argument('-s', '--symmetry', type=str, default="vertical", help="symmetry (vertical, horizontal, both, rot2, rot4)")
    parser.add_argument('-g', '--gradient', type=str, default=None, help='overlay gradient')
    parser.add_argument('-l', '--list', type=str, default=None, help="comma-separated list of colours")
    parser.add_argument('output', type=str, help='output file')
    
    args = parser.parse_args()

    colours = mkcolours(args.list, args.monochrome)
    
    kw = {}
    if args.blur:
        kw['blur'] = args.blur
    if args.gradient:
        kw['gradient'] = args.gradient
    if args.algorithm:
        kw['alg'] = args.algorithm
    if args.blgorithm:
        kw['blg'] = args.blgorithm
    
    voronidol(args.width, args.height, args.points, args.symmetry, args.colours, colours, args.output, **kw)
    
#def voronidol(w, h, npoints, symmetry, ncols, cols, output, **kwargs):
