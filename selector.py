from util import distance_between_points


class Selector:
    # can search for a new object close to x,y,color, and keep tracking the ID when it has found one
    def __init__(self):
        # search for object with these specs
        self.search_point = None
        self.search_color = None

        self.current_point = (0, 0)

    def reset(self):
        self.current_point = None

    def update(self, point, color_name):
        if self.search_color is not None and color_name != self.search_color:
            return

        if self.current_point is None or (self.search_point is not None
                                          and distance_between_points(point,
                                                                      self.search_point) < distance_between_points(
                    self.search_point,
                    self.current_point)):
            self.current_point = point
