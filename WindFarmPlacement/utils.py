import numpy as np
import warnings


def number_days_for_month(month):
    days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    return days[month]


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


def interpolation(xx, yy, data):
    vfunc = np.vectorize(interp_point, excluded=['data'])
    interp_matrix = vfunc(xx, yy, data=data)
    return interp_matrix

# Les fonctions suivantes doivent être déplacés


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
        near = np.intersect1d(near_x, near_y, assume_unique=True)  # Si erreur désactiver assume_unique
        # Le premier élément est le point de la recherche en cours.
        for index in near[1:]:
            if not mark[index]:
                group.extend(explore(index, []))
        return group

    for i in range(x.size):
        if not mark[i]:
            groups.append(explore(i, []))

    return groups


def rectangle(group, width_x, width_y):
    """Fonction qui renvoie les coordonnées permettant de faire un rectangle"""

    array = np.array(group)
    x = array[:, 1]
    y = array[:, 0]

    lines = []

    i = 0
    while i < x.size:
        near_x = np.where(x == x[i])
        width_line = len(near_x[0])
        lines.append(near_x[0])
        i += width_line

    rectangles = []
    # S'il y a assez de lignes pour la largeur selon y, alors on continue
    if len(lines) >= width_y:
        sub_lines = []
        j = 0

        # On extrait de chaque ligne, toutes les sous-lignes possibles de bonne largeur.
        while j < len(lines):
            sub_line = []
            line = lines[j]
            width_line = len(line)
            if width_line >= width_x:
                for k in range(width_line - width_x + 1):
                    sub_line.append(line[k:k + width_x])
            sub_lines.append(sub_line)
            j += 1

        m = 0
        while m < len(lines) - width_y + 1:
            # Explication (width_y + 1) : Les lignes sont par indice croissant, donc si on arrive à l'avant-dernière
            # on ne peut plus faire de rectangle de largeur 3 par exemple

            sub_line_list = sub_lines[m]
            for sub_line in sub_line_list:
                # On commence à créer un rectangle
                columns = y[sub_line]
                width_rect = 1
                while width_rect < width_y:
                    if not check_consecutive_lines(x, lines, m):
                        # Normalement, elles sont forcément consécutives si utiliser avec StudyArea
                        break
                    next_sub_line_list = sub_lines[m + width_rect]
                    if not np.any(y[np.array(next_sub_line_list)] == columns):
                        break
                    else:
                        width_rect += 1
                if width_rect == width_y:
                    rectangles.append([m, m+width_rect, columns])  # Start, End, columns
            m += 1

    return rectangles


def check_consecutive_lines(x, lines, index):
    check_consecutive = True
    line = lines[index]
    next_line = lines[index + 1]
    if x[next_line[0]] - 1 != x[line[0]]:
        check_consecutive = False
    return check_consecutive

def print_message_console(message):
    print(f"\n-------------------\n{message}\n-------------------") 