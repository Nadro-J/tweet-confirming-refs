import os
import sys
import logging
import inspect
from datetime import datetime


class Logger:
    @staticmethod
    def configure(log_level, filename_prefix, output_dir="./logs"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Include a timestamp in the log file name
        timestamp = datetime.now().strftime("%Y-%m-%d")

        # Get the command line command used to execute the script
        command = " ".join(sys.argv)

        # Map numeric levels to logging levels
        level_mapping = {
            1: logging.ERROR,
            2: logging.WARNING,
            3: logging.INFO,
            4: logging.DEBUG,  # Enables all logging levels
        }

        level_names = {1: "ERROR", 2: "WARN", 3: "INFO", 4: "DEBUG"}

        # Default to DEBUG if the provided level is out of range
        numeric_level = level_mapping.get(log_level, logging.DEBUG)
        level_name = level_names.get(log_level, "DEBUG")
        log_file_path = f"{output_dir}/{filename_prefix}-{timestamp}-{level_name}.log"
        logging.basicConfig(
            filename=log_file_path,
            level=numeric_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Log the command at the top of the log file
        logging.info("Command executed:\n# %s\n", command)

    @staticmethod
    def get_caller_info():
        stack = inspect.stack()
        for frame_info in stack[2:]:
            frame = frame_info.frame
            code = frame.f_code
            if "self" in frame.f_locals:
                class_name = frame.f_locals["self"].__class__.__name__
                method_name = code.co_name
                return f"{class_name}.{method_name}"

            module_name = frame.f_globals["__name__"]
            function_name = code.co_name
            return f"{module_name}.{function_name}"
        return "Unknown"

    @staticmethod
    def log(log_func, caller_info, message):
        log_func("%s:\n%s\n", caller_info, message)

    @staticmethod
    def info(message):
        caller_info = Logger.get_caller_info()
        Logger.log(logging.info, caller_info, message)

    @staticmethod
    def warning(message):
        caller_info = Logger.get_caller_info()
        Logger.log(logging.warning, caller_info, message)

    @staticmethod
    def error(message):
        caller_info = Logger.get_caller_info()
        Logger.log(logging.error, caller_info, message)

    @staticmethod
    def debug(message):
        caller_info = Logger.get_caller_info()
        Logger.log(logging.debug, caller_info, message)
