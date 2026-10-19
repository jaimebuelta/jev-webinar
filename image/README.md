Image classifier using Jev

Be sure to fill your Jev key from https://typesafe.ai in the .env file, and call the script with your image to find
if there's an animal in your image


  uv venv
  uv pip install -r requirements.txt
  
  uv run check_image.py YOUR_IMAGE


You can use the parameter --box to display the image with the animal in a bounding box

Alternatively, you can use the --scifi parameter to tell you if the image is related to Star Trek or Star Wars


Have fun!
