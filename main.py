import cv2
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

VIDEO_DIRECTORY = os.getenv("VIDEO_DIRECTORY")
OUTPUT_IMAGE_PATH = os.getenv("OUTPUT_IMAGE_PATH")
ALLOWED_EXTENSIONS = [".mkv", ".mp4"]  # You can add more if needed
BUCKET_NAME = os.getenv("BUCKET_NAME")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
REGION = "us-east-1"
S3_FILE_NAME = "camera_image.jpg"


def get_most_recent_video(directory):
    video_files = [
        f
        for f in os.listdir(directory)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]
    if not video_files:
        return None
    video_files.sort(
        key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=False
    )
    return os.path.join(directory, video_files[0])


def capture_image(video):
    vidcap = cv2.VideoCapture(video)
    success, image = vidcap.read()
    cv2.imwrite(OUTPUT_IMAGE_PATH, image)  # save frame as JPEG file
    vidcap.release()
    cv2.destroyAllWindows()


def remove_file(file):
    os.remove(file)


def upload_to_s3():
    client = boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )
    client.upload_file(
        OUTPUT_IMAGE_PATH,
        BUCKET_NAME,
        S3_FILE_NAME,
        ExtraArgs={"ContentType": "image/jpeg"},
    )


if __name__ == "__main__":
    video_url = get_most_recent_video(VIDEO_DIRECTORY)
    if video_url:
        capture_image(video=video_url)
        remove_file(file=video_url)
        upload_to_s3()
        remove_file(OUTPUT_IMAGE_PATH)
