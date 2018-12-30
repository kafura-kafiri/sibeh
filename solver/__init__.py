from random import shuffle
import numpy as np
import config
import asyncio
import ujson as json
from scipy.optimize import linear_sum_assignment
import math
from static import osrm_host

"""
for finding ( distance | duration ) matrix ->
    1. brute force
    2. bfs and find all with summation => d(vu) = d(vx) + d(xu) ~ d(vx) + d(xu)

http://download.xuebalib.com/xuebalib.com.13149.pdf

    patching rate
    porter customized for a region
    minimum matching
    release rate
    fcm delay send (for each some alternative)

listen on ...
"""


def homologous(frees, paths):
    if len(frees) > len(paths):
        return frees[:len(paths)], paths
    return frees, paths[:len(frees)]


async def rnd(frees, paths):
    frees, paths = homologous(frees, paths)
    shuffle(paths)
    return [(p, paths[i]) for i, p in enumerate(frees)]


async def matrix(frees, paths):
    m = np.zeros((len(frees), len(paths)))
    async def retrieve(f_head, f_tail, p_head, p_tail):
        points = '{};{}'.format(
            ';'.join(['{},{}'.format(f['location'][1], f['location'][0]) for f in frees[f_head:f_tail]]),
            ';'.join(['{},{}'.format(*reversed(p['points'][-1]['location'])) for p in paths[p_head:p_tail]]),
        )
        async with config.session.get(osrm_host + '/table/v1/driving/' + points, params={
            'sources': ';'.join([str(i) for i in range(f_tail - f_head)]),
            'destinations': ';'.join([str(i) for i in range(f_tail - f_head, f_tail - f_head + p_tail - p_head)])
        }) as response:
            m[f_head: f_tail, p_head: p_tail] = np.array(json.loads(await response.text())['durations'])

    chunk = 100
    chunked = lambda chunkee: [min(i * chunk, len(chunkee)) for i in range(1 + math.ceil(len(chunkee) / chunk))]
    nexted = lambda nextee: [(n, nextee[i + 1]) for i, n in enumerate(nextee[:-1])]

    await asyncio.gather(*[retrieve(f_head, f_tail, p_head, p_tail)
                          for f_head, f_tail in nexted(chunked(frees))
                          for p_head, p_tail in nexted(chunked(paths))])
    return m


async def grd(frees, paths):
    rows = []
    shuffle(paths)
    cost = (await matrix(frees, paths)).T
    for i in range(min(len(frees), len(paths))):
        rows.append(min([(i, v) for (i, v) in enumerate(cost[i]) if i not in rows], key=lambda x: x[1])[0])
    # print('greedy', sum([cost[i][v] for (i, v) in enumerate(rows)]))
    return [(frees[i], p) for i, p in enumerate(paths[:min(len(frees), len(paths))])]


async def hng(frees, paths):
    cost = await matrix(frees, paths)
    row_idx, col_idx = linear_sum_assignment(cost)
    # print('hungarian', cost[row_idx, col_idx].sum())
    return [(frees[row_idx[i]], paths[col_idx[i]]) for i in range(min(len(frees), len(paths)))]


async def test_batch(frees, paths):
    paths[0]['points'].extend(paths[1]['points'])
    paths[0]['points'][1], paths[0]['points'][2] = paths[0]['points'][2], paths[0]['points'][1]
    paths[0]['points'][0], paths[0]['points'][1] = paths[0]['points'][1], paths[0]['points'][0]
    return [(frees[0], paths[0])]


async def poo(frees, paths):
    # patch() -> $paths.sort(key=lambda:True).limit(len(frees)) -> hungarian -> END
    # patched(p1, p2).priority = max(p1.priority, p2.priority)
    paths = patch(paths)
    paths = sorted(paths, key=lambda p: p['priority'] * 1000 + sum([(lambda p1, p2:
                                                                     abs(p1['location'][0] - p2['location'][0]) +
                                                                     abs(p1['location'][0] - p2['location'][0]))
                                                                    (*domino)
                                                                    for domino in zip(p['points'], p['points'][1:])])
                                        / (len(p['points']) / 2 + 2))  # TODO
    paths = paths[:len(frees)]
    return await hng(frees, paths)


if __name__ == '__main__':
    matrix([None, None], [None, None])
