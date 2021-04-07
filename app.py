from cloudinary.uploader import upload, destroy
from cloudinary.utils import cloudinary_url
from flask import Flask, render_template, request
import json

app = Flask(__name__)

publicID = []

@app.route('/', methods=['POST'])
# upload
# https://cloudinary.com/documentation/image_upload_api_reference
def upload_file():
  upload_result = None
  thumbnail_url1 = None
  thumbnail_url2 = None
  if request.method == 'POST':
      file_to_upload = request.files['file'] 
      if file_to_upload:
          upload_result = upload(file_to_upload) #signed file
          publicID.append(upload_result.get('public_id'))
          print(publicID)
          # transform images
          # thumbnail_url1, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=100,
          #                                           height=100)
          # thumbnail_url2, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=200,
          #                                           height=100, radius=20, effect="sepia")
  return render_template('upload_form.html', upload_result=upload_result, thumbnail_url1=thumbnail_url1,
                          thumbnail_url2=thumbnail_url2, publicID=publicID)

@app.route('/delete', methods=['POST'])
def delete_file():
  condition = None
  if request.method == 'POST':
    if len(publicID) > 0:
      condition = publicID[0] + " has been deleted" 
      delete(publicID[0])
    else:
      condition = "file does not exist"
    
  return render_template('upload_form.html', condition=condition)


def delete(filename):
  destroy(filename)
  publicID.pop(0)
  return 0

def fetch_file(fileName):
  pass


if __name__ == "__main__":
  app.debug = True
  app.run()

