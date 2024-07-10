# Getting Started

## Install Dependencies
```bash
pip install -r requirements.txt
```

# Running the Application
Once the necessary dependenceis have been installed, run `main.py`

## Arguments
The following optional arguments that determine how the system will run. Additionally, these flags are mutually exclusive
and cannot be used together.
- `--test`: Use this flag to run a test suite to debug the program.
- `--distr` <addr_1>,<addr_2>, <addr_3>...: Use this flag to distribute workload among local machines.  
  Machines that run without this flag will wait to receive data to process from a machine that uses this flag.
```bash
python main.py --test | --distr <addr_1>,<addr_2>, <addr_3>
```

## Finding Youtube videos matching a given phrase
Upon running the system without the `--test` flag, you will be prompted to enter a Youtube channel name.
While the name is not case sensitive, spaces must be included. For example a channel like `Beast Philanthropy`:
(GOOD) `beast philanthropy`
(BAD) `beastphilanthropy`

The next step is to enter a phrase to search for within the channel. Like the channel name this is not case sensitive but requires 
appropriate spacing.
```Bash
Enter a phrase: oh my god
```


