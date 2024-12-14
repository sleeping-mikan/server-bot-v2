"""
loggerで用いるフォーマッタの定義
"""
#!ignore
from ..imports import *
from ..constant import *
from ..colors import *
#!end-ignore

class Formatter():
    levelname_size = 8
    name_size = 10
    class ColoredFormatter(logging.Formatter):
        # ANSI escape codes for colors
        COLORS = {
            'DEBUG': Color.BOLD + Color.WHITE,   # White
            'INFO': Color.BOLD + Color.BLUE,    # Blue
            'WARNING': Color.BOLD + Color.YELLOW, # Yellow
            'ERROR': Color.BOLD + Color.RED,   # Red
            'CRITICAL': Color.BOLD + Color.MAGENTA # Red background
        }
        RESET = '\033[0m'  # Reset color
        BOLD_BLACK = Color.BOLD + Color.BLACK  # Bold Black

        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            bold_black_asctime = f"{self.BOLD_BLACK}{record.asctime}{self.RESET}"
            
            # Adjust level name to be 8 characters long
            original_levelname = record.levelname
            padded_levelname = original_levelname.ljust(Formatter.levelname_size)
            original_name = record.name
            padded_name = original_name.ljust(Formatter.name_size)
            
            # Apply color to the level name only
            color = self.COLORS.get(original_levelname, self.RESET)
            colored_levelname = f"{color}{padded_levelname}{self.RESET}"
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{bold_black_asctime} {colored_levelname} {padded_name}: {message}"
            
            return formatted_message

    class MinecraftFormatter(logging.Formatter):
        
        # ANSI escape codes for colors
        COLORS = {
            'SERVER': Color.BOLD + Color.GREEN,   # Green
        }
        RESET = '\033[0m'  # Reset color
        BOLD_BLACK = Color.BOLD + Color.BLACK  # Bold Black

        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            bold_black_asctime = f"{self.BOLD_BLACK}{record.asctime}{self.RESET}"
            
            # Apply color to the level name only
            color = self.COLORS["SERVER"]
            colored_levelname = f"{color}SERVER  {self.RESET}"
            
            # Get the formatted message
            message = record.getMessage()
            # msg_type = message.split()
            # if len(msg_type) > 2:
            #     msg_type = msg_type[2][:-1]
            # if msg_type == "INFO":
            #     msg_color = Color.CYAN
            # elif msg_type == "ERROR":
            #     msg_color = Color.RED
            # else:
            #     msg_color = Color.RESET
            what_type = message.upper()
            if "INFO" in what_type:
                msg_color = Color.CYAN
            elif "ERROR" in what_type:
                msg_color = Color.RED
            elif "WARN" in what_type:
                msg_color = Color.YELLOW
            else:
                msg_color = Color.RESET

            message = msg_color + message + Color.RESET
            
            # Create the final formatted message
            formatted_message = f"{bold_black_asctime} {colored_levelname} {message}"
            
            return formatted_message
    class FlaskFormatter(logging.Formatter):
        COLORS = {
            'FLASK': Color.BOLD + Color.CYAN,   # Green
        }
        RESET = '\033[0m'  # Reset color
        BOLD_BLACK = Color.BOLD + Color.BLACK  # Bold Black

        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            bold_black_asctime = f"{self.BOLD_BLACK}{record.asctime}{self.RESET}"
            
            # Apply color to the level name only
            color = self.COLORS["FLASK"]
            colored_levelname = f"{color}FLASK   {self.RESET}"
            
            # Get the formatted message
            message = record.getMessage()

            message = message + Color.RESET
            
            # Create the final formatted message
            formatted_message = f"{bold_black_asctime} {colored_levelname} {message}"
            
            return formatted_message

    class DefaultConsoleFormatter(logging.Formatter):
        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            
            # Adjust level name to be 8 characters long
            original_levelname = record.levelname
            padded_levelname = original_levelname.ljust(Formatter.levelname_size)
            original_name = record.name
            padded_name = original_name.ljust(Formatter.name_size)
            
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{record.asctime} {padded_levelname} {padded_name}: {message}"
            
            return formatted_message
        
    class MinecraftConsoleFormatter(logging.Formatter):
        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            
            padded_levelname = "SERVER".ljust(Formatter.levelname_size)
            
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{record.asctime} {padded_levelname} {message}"
            
            return formatted_message
    class FlaskConsoleFormatter(logging.Formatter):
        def format(self, record):
            # Format the asctime
            record.asctime = self.formatTime(record, self.datefmt)
            
            padded_levelname = "FLASK".ljust(Formatter.levelname_size)
            
            
            # Get the formatted message
            message = record.getMessage()
            
            # Create the final formatted message
            formatted_message = f"{record.asctime} {padded_levelname} {message}"
            
            return formatted_message


#logger
dt_fmt = '%Y-%m-%d %H:%M:%S'
console_formatter = Formatter.ColoredFormatter(f'{Color.BOLD + Color.BG_BLACK}%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt)
file_formatter = Formatter.DefaultConsoleFormatter('%(asctime)s %(levelname)s %(name)s: %(message)s', dt_fmt)
