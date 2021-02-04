import io
import os
import stat
import tarfile
import urllib.request


FFMPEG_URL = "https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-4.2.2-amd64-static.tar.xz"
FFMPEG_EXECUTABLE = "ffmpeg"
FFMPEG_ARCHIVE_PATH = "ffmpeg-4.2.2-amd64-static/ffmpeg"
FFMPEG_EXTRACTION_DIR = "../ffmpeg"


def download_ffmpeg_archive():
    request = urllib.request.urlopen(FFMPEG_URL)
    return io.BytesIO(request.read())


def extract_ffmpeg(raw_archive):
    archive = tarfile.open(fileobj=raw_archive)
    return archive.extractfile(FFMPEG_ARCHIVE_PATH)


def write_ffmpeg(executable):
    os.makedirs(FFMPEG_EXTRACTION_DIR, exist_ok=True)
    output_path = os.path.join(FFMPEG_EXTRACTION_DIR, FFMPEG_EXECUTABLE)
    output_file = open(output_path, "wb")
    output_file.write(executable.read())
    os.chmod(output_path, stat.S_IXUSR)


if __name__ == "__main__":
    write_ffmpeg(extract_ffmpeg(download_ffmpeg_archive()))
