"""
Image Processing Pipeline with AWS S3 and Chalice.

This module implements a simple image processing pipeline using the AWS Chalice framework.
It provides an API to upload images to an S3 bucket, processes the images (resizing and conversion),
and stores the processed images in another S3 bucket. The module also includes a route to retrieve
processed images by their key.

The pipeline includes the following steps:
1. Upload an image via the `/upload` endpoint, where the image is uploaded to the 'original-images-bucket-chalice'.
2. Automatically trigger image resizing and processing via an S3 event when an image is uploaded.
3. Store the processed image in the 'processed-images-bucket-chalice' bucket.
4. Retrieve the processed image using its key via the `/images/{image_key}` endpoint.

Libraries used:
- `chalice` for creating the serverless application.
- `boto3` for AWS S3 interactions.
- `Pillow` (PIL) for image processing.

"""

import logging
import uuid
from io import BytesIO

import boto3
from chalice import Chalice, Response
from PIL import Image

app = Chalice(app_name='Image-Processing-Pipeline')
s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
log = logging.getLogger()
log.setLevel(logging.INFO)


@app.route('/upload', methods=['POST'], content_types=['image/jpeg', 'image/png'])
def upload_image():
    """
    Uploads an image to the S3 bucket after validating the content type.

    This function accepts an image via a POST request and uploads it to
    the 'original-images-bucket-chalice' S3 bucket. Supported image formats are
    JPEG, PNG, and WebP. The image is uploaded with a unique key.

    :return: JSON response with the image key and success message or an error message.
    """
    try:
        request = app.current_request
        image_data = request.raw_body
        content_type = request.headers.get('Content-Type', '')

        # Validate content type
        if content_type not in ['image/jpeg', 'image/png', 'image/webp']:
            log.error(f"Unsupported file type: {content_type}")
            return Response(body='Unsupported file type', status_code=400)

        # Generate a unique key for the image
        image_extension = content_type.split('/')[1]
        image_key = f"{uuid.uuid4()}.{image_extension}"

        # Upload the image to S3
        s3.upload_fileobj(BytesIO(image_data), 'original-images-bucket-chalice', image_key)
        log.info(f"Image uploaded successfully: {image_key}")

        return {'image_key': image_key, 'message': 'Image uploaded successfully'}
    except Exception as e:
        log.error(f"Error uploading image: {str(e)}")
        return Response(body=f"Error: {str(e)}", status_code=500)


@app.on_s3_event(bucket='original-images-bucket-chalice')
def resize_image(event):
    """
    Resizes the image from the S3 bucket and saves it to the processed images bucket.

    This function is triggered automatically when an image is uploaded to the 'original-images-bucket-chalice'.
    It retrieves the original image, processes it by resizing to 800x600 pixels, and stores the
    processed image in the 'processed-images-bucket-chalice'.

    :param event: S3 event triggering the function.
    :return: Message indicating success or failure.
    """
    try:
        original_bucket = s3_resource.Bucket('original-images-bucket-chalice')
        processed_bucket = s3_resource.Bucket('processed-images-bucket-chalice')

        image_obj = original_bucket.Object(event.key)
        image_data = image_obj.get()['Body'].read()

        # Process and resize the image
        processed_image = process_image(image_data)

        # Save the processed image to the processed images bucket
        processed_bucket.put_object(Key=event.key, Body=processed_image)
        log.info(f"Image processed and saved: {event.key}")

        return {'message': 'Image processed and saved'}
    except Exception as e:
        log.error(f"Error processing image: {str(e)}")
        return {'message': 'Error processing image'}, 500


def process_image(image_data):
    """
    Processes and resizes the image.

    This function resizes the given image to 800x600 pixels. If the image is in WebP format, 
    it is first converted to RGB before resizing.

    :param image_data: Raw image data from S3.
    :return: Resized and optimized image as bytes.
    """
    try:
        img = Image.open(BytesIO(image_data))

        # Convert WebP images to RGB if necessary
        if img.format == 'WEBP':
            img = img.convert("RGB")

        # Resize the image (800x600)
        img = img.resize((800, 600))

        # Save the processed image to a buffer
        buffer = BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=85)
        log.info("Image processed successfully.")

        return buffer.getvalue()
    except Exception as e:
        log.error(f"Error processing image: {str(e)}")
        raise


@app.route('/images/{image_key}', methods=['GET'])
def get_processed_image(image_key):
    """
    Fetches the processed image from the S3 bucket and returns it as binary data.
    
    This function retrieves a processed image from the 'processed-images-bucket-chalice' bucket
    by its key and returns it as a binary response with the correct Content-Type for images.
    
    :param image_key: Key of the image to retrieve.
    :return: Binary response with image data or an error message.
    """
    log.info(f"Fetching image with key: {image_key}")
    try:
        # Fetch the processed image from S3
        processed_image = s3.get_object(Bucket='processed-images-bucket-chalice', Key=image_key)
        image_data = processed_image['Body'].read()

        # Return the binary image data with the correct content type
        return Response(body=image_data,
                        status_code=200,
                        headers={'Content-Type': 'image/jpeg'},
                        is_base64_encoded=True)
    except s3.exceptions.NoSuchKey as e:
        log.error(f"Image not found for key: {image_key}. Error: {str(e)}")
        return Response(body='Image not found', status_code=404)
    except Exception as e:
        log.error(f"Error fetching image: {str(e)}")
        return Response(body=f"Error: {str(e)}", status_code=500)
        return Response(body=f"Error: {str(e)}", status_code=500)
