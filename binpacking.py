
from __future__ import division

from collections import namedtuple


class Point(namedtuple('Point', 'x y')):
    __slots__ = ()

    def __add__(self, other):
        return Point(self[0] + other[0], self[1] + other[1])

    def __radd__(self, other):
        return self.__add__(other)

    def __truediv__(self, other):
        return Point(self[0] / other, self[1] / other)

    def __repr__(self):
        return '({},{})'.format(*self)


class Item(object):
    __slots__ = ('size',)

    def __init__(self, size):
        self.size = Point(*size)

    def __repr__(self):
        return '{}x{}'.format(*self.size)

    @property
    def color_index(self):
        return hash(self.size) & 0xff

    @property
    def area(self):
        return self.size.x * self.size.y


class Shelf(dict):
    def __init__(self, width, height):
        super(Shelf, self).__init__()
        self.size = Point(width, height)
        self.filled_to_x = 0

    def __hash__(self):
        return object.__hash__(self)

    def pack(self, item, x, y):
        self[item] = Point(x, y)
        self.filled_to_x += item.size.x

    @property
    def empty_x(self):
        return self.size.x - self.filled_to_x

    @property
    def filled_area(self):
        return sum(item.area for item in self)


class Bin(dict):
    def __init__(self, size):
        super(Bin, self).__init__()
        self.size = Point(*size)
        self.filled_to_y = 0

    def pack(self, shelf, x, y):
        self[shelf] = Point(x, y)
        self.filled_to_y += shelf.size.y

    @property
    def empty_y(self):
        return self.size.y - self.filled_to_y

    @property
    def filled_area_ratio(self):
        return sum(shelf.filled_area for shelf in self) / (self.size.x * self.size.y)


class ItemList(list):
    def __init__(self, items):
        super(ItemList, self).__init__()
        for item_size, item_count in items.items():
            for i in range(item_count):
                self.append(Item(item_size))

    def sort_by_height(self):
        self.sort(key=lambda item: item.size.y, reverse=True)


class FXFBase(object):
    """
    Base for FNF, FFF, FBF classes
    """

    def __init__(self, bin_size, item_list):
        self.bin_size = Point(*bin_size)
        self.item_list = item_list

        self.bin_list = []

    @staticmethod
    def can_fit(shelf, item):
        return shelf.empty_x >= item.size.x

    def create_bin(self):
        bin = Bin(self.bin_size)
        self.bin_list.append(bin)
        return bin

    def create_and_pack_shelf(self, item):
        shelf = Shelf(self.bin_size.x, item.size.y)
        bin = self.get_fit_bin(shelf)
        bin.pack(shelf, 0, bin.filled_to_y)
        return shelf

    def get_fit_bin(self, shelf):
        raise NotImplementedError

    def get_fit_shelf(self, item):
        raise NotImplementedError

    def pack(self, item):
        shelf = self.get_fit_shelf(item)
        shelf.pack(item, shelf.filled_to_x, 0)

    def solve(self):
        self.item_list.sort_by_height()
        for item in self.item_list:
            self.pack(item)
        return self.bin_list


class FNF(FXFBase):
    """
    Finite Next-Fit
    """

    def __init__(self, *args, **kwargs):
        super(FNF, self).__init__(*args, **kwargs)
        self.current_bin = None
        self.current_shelf = None

    def get_fit_bin(self, shelf):
        if self.current_bin is None or self.current_bin.empty_y < shelf.size.y:
            self.current_bin = self.create_bin()
        return self.current_bin

    def get_fit_shelf(self, item):
        if self.current_shelf is None or not self.can_fit(self.current_shelf, item):
            self.current_shelf = self.create_and_pack_shelf(item)
        return self.current_shelf


class FFF(FXFBase):
    """
    Finite First-Fit
    """

    def get_fit_bin(self, shelf):
        for bin in self.bin_list:
            if bin.empty_y >= shelf.size.y:
                return bin
        return self.create_bin()

    def get_fit_shelf(self, item):
        for bin in self.bin_list:
            for shelf in bin:
                if self.can_fit(shelf, item):
                    return shelf

        return self.create_and_pack_shelf(item)


class FBF(FXFBase):
    """
    Finite Best-Fit
    """

    def get_fit_bin(self, shelf):
        min_empty_y_after_packing = float('Inf')
        fit_bin = None

        for bin in self.bin_list:
            empty_y_after_packing = bin.empty_y - shelf.size.y
            if 0 <= empty_y_after_packing < min_empty_y_after_packing:
                min_empty_y_after_packing = empty_y_after_packing
                fit_bin = bin

        if fit_bin is not None:
            return fit_bin
        else:
            return self.create_bin()

    def get_fit_shelf(self, item):
        min_empty_x_after_packing = float('Inf')
        fit_shelf = None

        for bin in self.bin_list:
            for shelf in bin:
                if self.can_fit(shelf, item):
                    empty_x_after_packing = shelf.empty_x - item.size.x
                    if empty_x_after_packing < min_empty_x_after_packing:
                        min_empty_x_after_packing = empty_x_after_packing
                        fit_shelf = shelf

        if fit_shelf is not None:
            return fit_shelf
        else:
            return self.create_and_pack_shelf(item)


def main():
    from pprint import pprint
    import task

    item_list = ItemList(task.ITEM_SET)
    # bin_list = FNF(task.BIN_SIZE, item_list).solve()
    # bin_list = FFF(task.BIN_SIZE, item_list).solve()
    bin_list = FBF(task.BIN_SIZE, item_list).solve()

    pprint(bin_list)


if __name__ == '__main__':
    main()
