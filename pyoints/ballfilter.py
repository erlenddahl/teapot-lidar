import numpy as np
from numbers import Number

from . import (
    assertion,
    indexkd,
)

def ball(indexKD, r, order=None, inverse=False, axis=-1, min_pts=1):
    """Filters coordinates by radius. This algorithm is suitable to remove
    duplicate points or to get an almost uniform point density.
    Parameters
    ----------
    indexKD : IndexKD
        IndexKD containing `n` points to filter.
    r : positive float or array_like(float, shape=(n))
        Ball radius or radii to select neighbouring points.
    order : optional, array_like(int, shape=(m))
        Order to proceed. If m < n, only a subset of points is investigated. If
        none, ordered by `axis`.
    axis : optional, int
        Coordinate axis to use to generate the order.
    inverse : bool
        Indicates whether or not the `order` is inversed.
    min_pts : optional, int
        Specifies how many neighbouring points within radius `r` shall be
        required to yield a filtered point. This parameter can be used to
        filter noisy point sets.
    Yields
    ------
    positive int
        Indices of the filtered points.
    Notes
    -----
    Within a dense point cloud, the filter guarantees the distance of
    neighboured points in a range of `]r, 2*r[`.
    """
    # validation
    if not isinstance(indexKD, indexkd.IndexKD):
        raise TypeError("'indexKD' needs to be an instance of 'IndexKD'")
    coords = indexKD.coords

    if order is None:
        order = np.argsort(coords[:, axis])[::-1]
    order = assertion.ensure_indices(order, max_value=len(indexKD) - 1)
    if inverse:
        order = order[::-1]

    if not hasattr(r, '__len__'):
        r = np.repeat(r, len(indexKD))
    r = assertion.ensure_numvector(r)
    if not np.all(r) > 0:
        raise ValueError("radius greater zero required")

    # filtering
    not_classified = np.ones(len(indexKD), dtype=np.bool)
    for pId in order:
        if not_classified[pId]:
            nIds = indexKD.ball(coords[pId, :], r[pId])
            if len(nIds) >= min_pts:
                not_classified[nIds] = False
                yield pId
