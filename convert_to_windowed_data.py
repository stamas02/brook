import numpy as np
import argparse
import signal_manager as sm

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, help="The folder in which the dataset is in")
    parser.add_argument("--destination", type=str, help="The folder where the converted data is daved")
    parser.add_argument("--currency", type=str, help="The curreny pair to convert")
    parser.add_argument("--nrof_bins", type=int, help="The number of bins the data is smoothed to")
    parser.add_argument("--look_forward", type=int, help="For how long the network is required to predict the feature in minutes")
    parser.add_argument("--look_backward", type=int, help="The size of the history available for the network to learn from")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    data = np.load(args.source)
    data = data[args.currency+'.npy']
    data = data[:,1]
    available_windows = np.array(range(0, len(data) - args.look_forward - args.look_backward))
    datax = [sm.exsax(sm.preprocess(data[window:window + args.look_backward]), args.nrof_bins) for window in
             available_windows]
    datay = [sm.future_description(
        data[window + args.look_backward:window + args.look_backward + args.look_forward] - data[
            window + args.look_backward - 1]) for window in available_windows]

    settings = {"nrof_bins": args.nrof_bins,
                "look_forward": args.look_forward,
                "look_backward": args.look_backward}
    np.savez(args.destination, datax=datax, datay=datay, original=data[args.look_backward:], settings = settings)