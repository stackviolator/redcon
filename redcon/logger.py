import csv
import datetime
import os
import sys

class Logger:
    def __init__(self):
        self.log_file = "logs/agent_logs.csv"
        self.fieldnames = [
            'action',
            'input',
            'result',
            'model',
            'time'
        ]

    def _log(self, data):
        file_exists = os.path.isfile(self.log_file)
        mode = "a" if file_exists else "w"
        try:
            with open(self.log_file, mode, newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                # Write header if the file was just created
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)  # Use writer.writerow for a single row
        except IOError:
            print(f"[-] Could not open {self.log_file} for logging")
            sys.exit(1)

    def log(self, action, input, result, model):
        data = {
            "action": action,
            "input": input,
            "result": result,
            "model": model,
            "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self._log(data)