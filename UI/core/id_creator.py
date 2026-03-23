import hashlib
from datetime import datetime

class FileIDGenerator:
    def __init__(self, created_time: str):
        """
        Khởi tạo đối tượng với thời gian tạo file.
        :param created_time: Thời gian tạo file dạng chuỗi (ISO format).
        """
        self.created_time = created_time
        self.file_id = self.generate_id()

    def generate_id(self) -> str:
        """
        Tạo ID duy nhất cho file dựa trên thời gian tạo.
        :return: ID file dưới dạng chuỗi hexadecimal.
        """
        # Băm (hash) thời gian tạo file để tạo ra ID duy nhất.
        hashed = hashlib.sha256(self.created_time.encode('utf-8')).hexdigest()
        return hashed

    def get_file_id(self) -> str:
        """
        Lấy ID file.
        :return: ID file.
        """
        return self.file_id

