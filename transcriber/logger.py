import threading

class Logger:
    def __init__(self, filepath, error_filepath, dir=None):
        self.write_lock = threading.Lock()
        self.err_lock = threading.Lock()
        self.file = filepath
        self.error_file = error_filepath

        if dir is not None:
            self.file = f"{dir}/{filepath}"
            self.error_file = f"{dir}/{error_filepath}"

    def log(self, content):
        """write to main file"""
        with self.write_lock:
            # write matches to file
            with open(self.file, "a") as f:
                f.write(content)

    def log_err(self, content):
        """write to error file"""
        with self.err_lock:
            with open(self.error_file, "a") as err:
                err.write(content)

        