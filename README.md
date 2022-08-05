# Golem Collatz Conjecture App

This application calculates [Collatz conjecture](https://en.wikipedia.org/wiki/Collatz_conjecture) for a provided numbers range.
Given range start as A and end as B, this application will split the range into subgroups (6 by default) and execute
each batch on a separate Golem network provider.

## Demo

![demo](https://user-images.githubusercontent.com/5244214/183013704-4a2dca76-be4f-41dd-9caa-8225c2e34d0c.gif)


## Setup

Prerequisites:

- Python 3.6 or higher
- (optional) Fresh virtual environment
- Yagna daemon running ([docs](https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development))

Install packages

```
$ python3 -m pip install -r requirements.txt
```

## Run

To execute the whole example, run the following command

```
$ python3 main.py A B
```

Where **A** is range start and **B** is a range end.

The **main.py** file configures Golem network and deploys the task to the workers (stored in the **task.py**)

You can customize the batch size or enable batch calculations debug logs using the parameters listed below

```
$ python3 main.py --help
usage: main.py [-h] [-bs BATCH_SIZE] [--debug] range_start range_end

positional arguments:
  range_start           Specify search range start (inclusive)
  range_end             Specify search range end, (non-inclusive)

optional arguments:
  -h, --help            show this help message and exit
  -bs BATCH_SIZE, --batch-size BATCH_SIZE
                        Specify on how many batches should the calculations be split
  --debug               Enable debug logs
```

