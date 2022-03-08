import h5py
import plotille as plt
import numpy as np

from rich import print

def createTimeseries(timeSeries):
    if timeSeries["vsKind"] != b"uniform":
        print("Nonuniform timeseries are not supported")
        exit()

    lowerBound = timeSeries["vsLowerBounds"][0]
    upperBound = timeSeries["vsUpperBounds"][0]
    numCells = timeSeries["vsNumCells"][0]

    return np.linspace(lowerBound, upperBound, numCells + 1), lowerBound, upperBound

def history(config):
    basename = config["basename"]
    data_dir = config["data_dir"]

    file = h5py.File(f"{data_dir}/{basename}_History.h5")

    timeseries, lower_time, upper_time = createTimeseries(file["timeSeries"].attrs)

    datasets = list(file.keys())
    for dataset_name in datasets:
        dataset = file[dataset_name]

        if not isinstance(dataset, h5py.Dataset):
            continue

        print(dataset.name)
        if len(dataset.shape) == 1:
            y_values = dataset[:]
            print(plt.plot(timeseries, y_values, height=10, origin=False, X_label="Time",
                Y_label=dataset_name, x_min=lower_time, x_max=upper_time))




    file.close()
