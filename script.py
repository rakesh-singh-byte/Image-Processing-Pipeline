import boto3

s3 = boto3.client('s3')

def fetch_image(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as e:
        print(f"Error: {str(e)}")

# Test the fetch manually
image_data = fetch_image('processed-images-bucket-chalice', '7af7be8b-c10a-4a23-8257-0225827eb06a.jpeg')
if image_data:
    with open('downloaded_image.jpeg', 'wb') as f:
        f.write(image_data)
