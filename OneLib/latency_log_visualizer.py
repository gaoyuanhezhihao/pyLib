from matplotlib import pyplot as plt
import argparse
import numpy as np


def load_profiler_log(fp):
    with open(fp, 'r') as f:
        item_time_map = {}
        for l in f.readlines():
            s = l.rfind(':')
            k = l[:s]
            v = float(l[s+1:])
            item_time_map.setdefault(k, []).append(v)

    means = []
    # std_var = {}
    for k, times in item_time_map.items():
        # ts = np.array(times)
        means.append((np.mean(times), k))
        # std_var[k] = np.std(ts)

    means = sorted(means)
    sections = [key for _, key  in means]

    times_list = []
    for k in sections:
        times_list.append(np.array(item_time_map[k]))

    return sections, times_list

def PlotProfiler(sections, times_list, time_axis_limit):

    if time_axis_limit:
        plt.ylim(0, time_axis_limit)
    plt.boxplot(times_list,
                         vert=True,  # vertical box alignment
                         patch_artist=True,  # fill with color
                         labels=sections)  # will be used to label x-ticks
    print(time_axis_limit)
    plt.show()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path")
    parser.add_argument("time_axis_limit", default=None)
    args = parser.parse_args()
    print(type(args.time_axis_limit))
    PlotProfiler(*load_profiler_log(args.log_path), int(args.time_axis_limit))
