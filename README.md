# Getting Started

## Install Dependencies
```bash
pip install -r requirements.txt
```

# Running the Application
Once the necessary dependencies have been installed, you can run the application

## Optional Arguments
The following optional arguments that determine how the system will run. 
- `--threads` <num_threads>: Use this flag to specify the amount of threads to use. The Default is **4**. The system supports 1-10 Threads.
The following flags are mutually exclusive and cannot be used together.
- `--test`: Use this flag to run a test suite to debug the program.
- `--distr` <addr_1>,<addr_2>, <addr_3>...: Use this flag to distribute workload among local machines.  
  Machines that run without this flag will wait to receive data to process from a machine that uses this flag.
```bash
python main.py --test | --distr <addr_1>,<addr_2>, <addr_3>
```

## Selecting a Channel to Search
Currently, there two ways to search through a channel  
- Playlist: https://www.youtube.com/watch?v=XmtiNajqbnI&list=PL84eKQ-fIQCkQUiQLa-jqU7Pu4MYSiwS0
- Channel Homepage: https://www.youtube.com/@BeastPhilanthropy/videos
Notice for the Channel Homepage that the url ends in **videos**. You can alternatively search through livestreams by changing the end to **streams**.

## Finding Youtube videos matching a given phrase
Upon running the system without the `--test` flag, you will be prompted to enter a Youtube channel name.
While the name is not case sensitive, spaces must be included. For an example channel like `Beast Philanthropy`:  

**(GOOD)** `beast philanthropy`  
**(BAD)** `beastphilanthropy`

The next step is to enter a phrase to search for within the channel. Like the channel name this is not case sensitive but requires 
appropriate spacing.
```bash
Enter a phrase: oh my god
```

Next if you selected the channel without changing any code you will be prompted to enter the channel URL:
```bash
Enter a url: https://www.youtube.com/@BeastPhilanthropy/videos
```

Finally, the system will scrape through all videos on the channel and record all matches, including timestamps, in a file located at `nodes\matches_beast philanthropy.txt`.

## Logging Runtime Errors
Due to the asynchronous nature of the internet, videos may be slow to load, transcripts could be slow to load, relevant HTML elements may be slow, etc. This may lead to a timeout error that will be logged at `nodes\error_log.txt`.


# Citations
- Stack Overflow Posts: [https://stackoverflow.com/questions/11154946/require-either-of-two-arguments-using-argparse](https://stackoverflow.com/questions/11154946/require-either-of-two-arguments-using-argparse)  
This post helped implement the command line arguments that control the behavior of the system.


