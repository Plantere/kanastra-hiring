from app.interfaces.services.file_service_interface import IFileService

class FileService(IFileService):
    def save_file(self, file):
        filepath = f"/kanastra-file-processor/app/storage/uploads/{file.filename}"
        with open(filepath, "wb+") as f:
            f.write(file.file.read())

        return filepath

    def is_csv_file(self, filename): 
        return filename.endswith(".csv")

    @classmethod
    def get_instance(cls) -> IFileService:
        return cls()
