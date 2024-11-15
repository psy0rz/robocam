from scipy.spatial import KDTree

color_list = [
    (0,0,255),
    (209, 89,11),
    (255,0,0),
    (0,255,0),
]

color_labels = [
    "blue",
    "orange",
    "red",
    "green",
]

color_tree = KDTree(color_list)


def find_closest_color(target_color):
    distance, index = color_tree.query(target_color)
    return color_labels[index], tuple(color_tree.data[index])
