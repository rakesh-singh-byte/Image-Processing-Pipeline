# Image Processing Pipeline using AWS Chalice

This is an AWS Chalice-based application that provides an image upload, resize, and retrieval service using AWS S3. The application accepts JPEG, PNG, and WebP images, resizes them, and stores the processed images in a separate S3 bucket.

## Features

- Upload an image (JPEG, PNG, WebP).
- Resize the uploaded image to a specified resolution (800x600).
- Retrieve the processed image via an API endpoint.
- S3 integration for storing original and processed images.

## Prerequisites

- Python 3.7 or higher
- AWS Account
- AWS CLI configured with appropriate IAM permissions
- Chalice (`pip install chalice`)
- Boto3 (`pip install boto3`)
- Pillow for image processing (`pip install pillow`)

## AWS Setup

1. Create two S3 buckets:
    - One for storing the original images (`original-images-bucket-chalice`).
    - One for storing the processed images (`processed-images-bucket-chalice`).

2. Set up IAM roles and policies for Chalice to have access to S3 (see `policy.json` for details).

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/Image-Processing-Pipeline.git
   cd Image-Processing-Pipeline
   ```

2. Install the required Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Deploy the Chalice application:

   ```bash
   chalice deploy
   ```

## API Endpoints

- **Upload Image**: Upload an image to the S3 bucket.
  - Endpoint: `POST /upload`
  - Content-Type: `image/jpeg`, `image/png`, or `image/webp`
  - Body: Binary image data

- **Retrieve Processed Image**: Get the processed image by image key.
  - Endpoint: `GET /images/{image_key}`
  - Response: Returns the processed image in binary form (Content-Type: `image/jpeg`).

## Configuration

Update the `config.json` to include binary media types:

```json
{
  "version": "2.0",
  "app_name": "Image-Processing-Pipeline",
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "binary_media_types": ["image/jpeg", "image/png", "image/webp"]
    }
  }
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request.

## Contact

For more information, please reach out to [rakesh.s.shankala@gmail.com](mailto:rakesh.s.shankala@gmail.com).