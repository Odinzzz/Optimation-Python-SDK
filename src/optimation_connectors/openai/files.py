# connector/openai/files.py

from typing import Optional

from openai import OpenAI
from openai.types import FileObject, FileDeleted
from openai.pagination import SyncCursorPage

class FilesApi:
    def __init__(self, client: OpenAI = None):
        self.client = client or OpenAI()

        
    
    def upload_file(self, file_path:str) -> FileObject:
        return self.client.files.create(
            file=open(file_path, 'rb'),
            purpose='user_data'
        )
    

    def delete_file(self, file_id)-> FileDeleted:
        return self.client.files.delete(file_id)
    

    def list_files(self) -> SyncCursorPage[FileObject]:
        return self.client.files.list()

    
    def delete_all_file(self) -> Optional[list[FileDeleted]]:
        """
            WARNING VERY DESTRUCTIVE
            delete all the file into the open ai file service
            use at your own risk
        """
        files = self.list_files()
        deleted_files = list()

        if not files:
            return None
        
        for file in files:
            deleted_file = self.delete_file(file.id)
            deleted_files.append(deleted_file)
        
        return deleted_files

