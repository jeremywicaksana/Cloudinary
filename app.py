from cloudinary.uploader import upload, destroy, add_tag, remove_tag, remove_all_tag
from cloudinary.utils import cloudinary_url

from flask import Flask, render_template, request, jsonify, url_for, redirect
import json
import sqlite3
import cloudinary
import requests

app = Flask(__name__)

cloudinary.config( 
  cloud_name = "dyvsb2mny", 
  api_key = "926684277493228", 
  api_secret = "_tJ-hTJfu34vcbX-wvom5x5gRGY" 
)

@app.route('/')
def index():
	return render_template("login.html")

@app.route('/login', methods=['GET','POST'])
def log_as():
  if request.method == 'POST':
    uname = request.form['username']
    uid = None

    #check existance
    exist = sqlExc("SELECT user_id FROM user WHERE uname = ?", [uname])
    if exist == [] and len(uname) > 0:
      sqlExc("INSERT INTO user(uname) VALUES (?)", [uname])
      uid = sqlExc("SELECT user_id FROM user WHERE uname = ?", [uname])
      requests.post('http://localhost:3000/user', json={"name": uname, "uid": uid[0]})    
      return redirect(url_for('home', user=uname, ident=uid[0]))
    elif len(uname) == 0:
      return render_template("login.html", error="name length needs to be > 0")
    
    uid = sqlExc("SELECT user_id FROM user WHERE uname = ?", [uname])
    # return render_template("upload_form.html", user = uname)
    return redirect(url_for('home', user=uname, ident=uid[0]))
    
@app.route('/mainpage/<user>/<ident>', methods=['POST','GET'])
def home(user, ident):
  return render_template("upload_form.html", user=user, ident=ident)
   

# https://cloudinary.com/documentation/image_upload_api_reference
@app.route('/upload', methods=['POST','GET'])
def upload_file():
  cur_id = request.form['ident']
  cur_name = request.form['user']
  upload_result = None
  thumbnail_url1 = None
  thumbnail_url2 = None
  public_ids = None
  if request.method == 'POST':
    file_to_upload = request.files['file'] 
    if file_to_upload:
      upload_result = upload(file_to_upload) #signed file upload function from cloudinary
      print("upload_result", upload_result)
      public_id = upload_result['public_id']
      sqlExc("INSERT INTO files(type, user_id, public_id) VALUES (?,?,?)", ["img", cur_id, public_id])
      public_ids = sqlExc("SELECT public_id FROM files WHERE user_id = ?", [cur_id])
      # transform images
      thumbnail_url1, options = cloudinary_url(public_id, format="jpg", crop="fill", width=100,
                                                height=100)
      thumbnail_url2, options = cloudinary_url(public_id, format="jpg", crop="fill", width=200,
                                                height=100, radius=20, effect="sepia")
  return render_template('upload_form.html', user=cur_name, ident=cur_id, upload_result=upload_result, thumbnail_url1=thumbnail_url1,
                          thumbnail_url2=thumbnail_url2, public_ids=public_ids) 


@app.route('/unameRecv', methods=['POST'])
def get_uname():
  resp = None
  if request.method == 'POST':
    rf = request.form #get immutable dict
    for key in rf.keys(): #transform to json
      data=key 
    data_dict = json.loads(data)#load json to dict
    uname = data_dict['uname']
    uid = sqlExc("SELECT user_id FROM user WHERE uname = ?", [uname])
    # uid = sqlExc("SELECT * FROM user")
    if len(uid) == 0:
      resp = jsonify("empty")
    else:
      resp_dic = {'id':uid[0]}
      resp = jsonify(resp_dic)

    publicID = 1

  return resp

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

#Cloudinary API -- 
def delete_Photo(public_id):
  destroy(public_id)
  return 0

def add_tag(tagname, public_id):
  add_tag(tagname, public_id)
  return 0

def remove_tag(tagname, public_id):
  remove_all_tag(tagname, public_id)
  return 0

def remove_all_tag(public_id):
  remove_tag(public_id)
  return 0



def sqlExc(statement, args=None):
  conn = sqlite3.connect('file.db')
  conn.row_factory = lambda cursor, row: row[0] #convert tuple to list
  cur = conn.cursor()
  if args != None:
    cur.execute(statement, tuple(args))
    result = cur.fetchall()
    conn.commit()

  else:
    cur.execute(statement)
    result = cur.fetchall()
    conn.commit()

  conn.close()
  return result

if __name__ == "__main__":
  app.debug = True
  app.run()