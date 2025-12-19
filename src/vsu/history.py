import h5py
import plotext as plt
import numpy as np

from rich import print

from vsu import make

def createTimeseries(timeSeries):
    if timeSeries.attrs["vsKind"] == b"uniform":
        lowerBound = timeSeries.attrs["vsLowerBounds"][0]
        upperBound = timeSeries.attrs["vsUpperBounds"][0]
        numCells = timeSeries.attrs["vsNumCells"][0]

        return np.linspace(lowerBound, upperBound, numCells + 1), lowerBound, upperBound
    elif timeSeries.attrs["vsKind"] == b"rectilinear":
        return timeSeries["time"][:], timeSeries["time"][0], timeSeries["time"][-1]
    else:
        print("Unrecgonized timeseries format")
        exit(1)

def createTimeseriesLabels(ts, lower_time, upper_time, N=4):
    if upper_time < 1e-12:
        factor = 1e-15
        unit = 'fs'
    elif upper_time < 1e-9:
        factor = 1e-12
        unit = 'ps'
    elif upper_time < 1e-6:
        factor = 1e-9
        unit = 'ns'
    elif upper_time < 1e-3:
        factor = 1e-6
        unit = 'μs'
    elif upper_time < 1:
        factor = 1e-3
        unit = 'ms'
    else:
        factor = 1
        unit = 's'

    ticks = []
    labels = []
    for n in range(N):
        location = lower_time + ((upper_time - lower_time) * n / (N - 1))
        ticks.append(location)
        labels.append(f'{location / factor:.1f} {unit}')

    print(ts)
    print(ticks, labels)

    return ticks, labels

def history(config):
    basename = config["basename"]
    data_dir = config["data_dir"]

    txpp_args = make.get_params_str(config)

    file = h5py.File(f"{data_dir}/{txpp_args}/{basename}_History.h5")

    timeseries, lower_time, upper_time = createTimeseries(file["timeSeries"])
    ts_ticks, ts_labels = createTimeseriesLabels(timeseries, lower_time, upper_time)

    datasets = list(file.keys())
    for dataset_name in datasets:
        dataset = file[dataset_name]

        if not isinstance(dataset, h5py.Dataset):
            continue

        if len(dataset.shape) == 1 or dataset.shape[1] == 1:
            if len(dataset.shape) == 1:
                y_values = dataset[:]
            else:
                y_values = dataset[:, 0]

            plt.clear_figure()
            plt.scatter(timeseries, y_values)
            plt.title(dataset.name)
            # plt.xlabel('Time')
            plt.xlim(lower_time, upper_time)
            plt.xticks(ts_ticks, ts_labels)
            plt.plotsize(plt.terminal_width(), round(plt.terminal_height() / 5))
            plt.show()
        else:
            print(dataset.name)

    file.close()
