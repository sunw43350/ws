# utils/csv_utils.py

import os
import csv
import asyncio

class CSVManager:
    def __init__(self, output_root: str):
        self.output_root = output_root
        self.writers = {}
        self.files = {}
        self._init_directories()

    def _init_directories(self):
        self.exchange_dir = os.path.join(self.output_root, "exchange")
        self.symbol_dir = os.path.join(self.output_root, "symbol")
        os.makedirs(self.exchange_dir, exist_ok=True)
        os.makedirs(self.symbol_dir, exist_ok=True)

    def _get_writer(self, category: str, key: str, headers: list):
        if category not in self.writers:
            self.writers[category] = {}
            self.files[category] = {}

        if key not in self.writers[category]:
            file_path = os.path.join(
                self.exchange_dir if category == "exchange" else self.symbol_dir,
                f"{key}.csv"
            )
            f = open(file_path, mode="a", newline="", encoding="utf-8")
            writer = csv.writer(f)
            if os.stat(file_path).st_size == 0:
                writer.writerow(headers)
            self.files[category][key] = f
            self.writers[category][key] = writer

        return self.writers[category][key]

    def write(self, category: str, key: str, row: list):
        headers = {
            "exchange": ["timestamp", "symbol", "bid", "ask", "bid_vol", "ask_vol"],
            "symbol": ["timestamp", "exchange", "bid", "ask", "bid_vol", "ask_vol"],
        }[category]
        writer = self._get_writer(category, key, headers)
        writer.writerow(row)

    def close_all(self):
        for category_files in self.files.values():
            for f in category_files.values():
                f.close()


class WriteTask:
    def __init__(self, category: str, key: str, row: list):
        self.category = category
        self.key = key
        self.row = row


async def writer_worker(write_queue: asyncio.Queue, csv_manager: CSVManager):
    while True:
        task = await write_queue.get()
        csv_manager.write(task.category, task.key, task.row)
        write_queue.task_done()
