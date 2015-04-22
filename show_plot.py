
from __future__ import division

import math

import matplotlib.pyplot as plt


def show_plot(bin_size, bin_list):
    bin_count = len(bin_list)
    column_count = 10
    row_count = int(math.ceil(bin_count / column_count))

    figure = plt.figure('Bin Packing')
    figure.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.95)
    figure.suptitle('{} bins'.format(bin_count))

    color_map = plt.cm.rainbow

    for number, bin in enumerate(bin_list, start=1):
        subplot = figure.add_subplot(row_count, column_count, number, aspect='equal')
        subplot.set_xlim(0, bin_size[0])
        subplot.set_ylim(0, bin_size[1])
        subplot.set_title('{:.1f}%'.format(100 * bin.filled_area_ratio))

        for shelf, shelf_position in bin.items():
            for item, item_position in shelf.items():
                rect_position = shelf_position + item_position
                rectangle = plt.Rectangle(rect_position, item.size.x, item.size.y, alpha=0.6, facecolor=color_map(item.color_index))
                subplot.add_artist(rectangle)
                subplot.annotate(str(item), rect_position + item.size / 2, ha='center', va='center', size=min(12, item.size.x * 1.5))

    plt.show()


if __name__ == '__main__':
    from binpacking import ItemList, FNF, FFF, FBF

    import task

    item_set = ItemList(task.ITEM_SET)
    # bin_list = FNF(task.BIN_SIZE, item_set).solve()
    # bin_list = FFF(task.BIN_SIZE, item_set).solve()
    bin_list = FBF(task.BIN_SIZE, item_set).solve()

    show_plot(task.BIN_SIZE, bin_list)
