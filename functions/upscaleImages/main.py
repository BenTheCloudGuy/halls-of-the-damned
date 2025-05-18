import requests

# Upscale Images Extracted from PDF - Not Free and should be moved to dedicated Function in another script 
# that is executed ONLY when needed.. 
def upscale_images(output_dir,image_output_path):
 
    # Uri and API Key
    url = "https://api.claid.ai/v1-beta1/image/edit/upload"
    apiKey = "YOUR_API_KEY"
    upscaledImageName = image_output_path.split('/')[-1]

    # Create folder for upscaled images
    if not os.path.exists(f'{output_dir}/upscaled_images'):
        os.makedirs(f'{output_dir}/upscaled_images')

    # Set resize percentage
    resize_percentage = '200%'

    headers = {
        "Host": url,
        "Authorization": f'Bearer {apiKey}',
        "Content-Type": "multipart/form-data"
    }

    files = {
        'file': (upscaledImageName, open(image_output_path, 'rb')),
        'data': (None, '{"operations":{"resizing":{"width":200%},"background":{"remove":false}}}', 'application/json')
    }