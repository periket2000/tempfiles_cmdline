from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    UPLOAD_URL: str = 'https://tempfil.es/fileupload/'
    FINISH_URL: str = 'https://tempfil.es/finish/'
    VERSION: str = '2.0.0'

    NO_MODE: str = 'No mode selected!'
    NO_FILE_GIVEN: str = 'No file to upload given!'
    UPLOADING: str = 'Uploading {} to https://tempfil.es'
    FILE_NOT_FOUND: str = 'File {} not found!'
    NO_DOWNLOAD_LINK: str = 'No link to download given!'
    INVALID_DESTINATION: str = 'Invalid destination path given!'
    CONNECTION_CLOSED: str = 'Server closed the connection, maybe the file is too large or the network speed too slow'
    OVERWRITE: str = 'File {} exists, overwrite? (y/n): '
    COMPLETE: str = 'Download of {} complete!'
    NOT_FOUND: str = 'File not found!'
    BAD_URL: str = 'Bad url provided!'
    SERVER_KO: str = 'Failed to establish a connection with the server!'
    ALIEN: str = 'Unexpected error:'


def log(msg: str, *args: Optional[str]) -> None:
    if args:
        print(msg.format(*args))
    else:
        print(msg)
