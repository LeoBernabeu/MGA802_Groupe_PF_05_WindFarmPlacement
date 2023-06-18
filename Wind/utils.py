import numpy as np
import warnings


def weight(point_coords, station_coords):
    x_ij, y_ij = point_coords[0], point_coords[1]
    x_k, y_k = station_coords[:, 0], station_coords[:, 1]

    sq_r = (x_ij - x_k) ** 2 + (y_ij - y_k) ** 2  # r²

    # https://stackoverflow.com/questions/15933741/how-do-i-catch-a-numpy-warning-like-its-an-exception-not-just-for-testing
    warnings.filterwarnings('error')
    try:
        W_k = 1 / sq_r
    except Warning:
        W_k = np.where(sq_r == 0, 1, 0)
    return W_k


def interp_point(x_ij, y_ij, data):
    # Source méthode bis plus complexe
    # https://www.researchgate.net/publication/234295032_A_Simple_Method_for_Spatial_Interpolation_of_the_Wind_in_Complex_Terrain
    values = data[:, 0]
    coords = data[:, 1:]

    Wk = weight([x_ij, y_ij], coords)
    U_ij = np.sum(Wk*values)/np.sum(Wk)
    return U_ij


def interp_grid(xx, yy, data):
    vfunc = np.vectorize(interp_point, excluded=['data'])
    interp_matrix = vfunc(xx, yy, data=data)
    return interp_matrix


def gather(condition):
    """Fonction qui regroupe en faisant un parcours en profondeur

    :param condition:
    :type condition:
    :return:
    :rtype:
    """

    groups = []

    x, y = np.where(condition)
    mark = np.zeros(x.size)

    def explore(k, group):
        mark[k] = 1
        group.append((x[k], y[k]))
        near_x = np.where(x-x[k] <= 1)
        near_y = np.where(y-y[k] <= 1)
        near = np.intersect1d(near_x, near_y)
        # Le premier élément est le point de la recherche en cours.
        for index in near[1:]:
            if not mark[index]:
                mark[index] = 1
                group.append((x[index], y[index]))
                group.extend(explore(index, []))
        return group

    for i in range(x.size):
        if not mark[i]:
            groups.append(explore(i, []))

    return groups

