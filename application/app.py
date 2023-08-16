
import os
import shutil
from random import randint
from datetime import datetime, timedelta, date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from export import exporting_task
from models import *
from charts import *

from sqlalchemy import func
from flask import Flask, render_template, send_file, send_from_directory, request, redirect, flash, get_flashed_messages
from flask_restful import Api
from flask_security import SQLAlchemySessionUserDatastore, Security, login_user, logout_user
from flask_security import current_user, login_required, roles_accepted, hash_password, verify_password, roles_required
from flask_caching import Cache

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///../database/testdb.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# sKey, pSalt, adPerm = input("SECRET_KEY:\t"),input("SECURITY_PASSWORD_SALT:\t"),input("ADMIN_PERMISSION:\t")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hbivnfdisbvljobfgjoihfhrugubdfsbery89w34yt5898he") #sKey if sKey else "hbivnfdisbvljobfgjoihfhrugubdfsbery89w34yt5898he"
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SECURITY_PASSWORD_SALT", "hbivnfdisbvljobfgjoihfhrugubdfsbery89w34yt5898he") #pSalt if pSalt else "hbivnfdisbvljobfgjoihfhrugubdfsbery89w34yt5898he"
# ADMIN_PERMISSION = os.environ.get("ADMIN_PERMISSION", "permission")
LAST_ACCESS = datetime.utcnow() + timedelta(minutes=-2)
OTP = str(randint(10000,999999))

db.init_app(app)
# app.app_context().push()


cache = Cache(config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 9736,
    'CACHE_REDIS_URL': 'redis://localhost:9736/0',
    "CACHE_DEFAULT_TIMEOUT": 300
})
cache.init_app(app)

api = Api(app)

user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
app.security = Security(app, user_datastore)



@app.route("/", methods=["GET"])
def index():
    return redirect('/signin')
  
@app.route('/manifest.json')
def manifest():
    return send_from_directory('../static', 'manifest.json')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    username = request.form["Username"]
    password = hash_password(request.form["Password"])
    first_name = request.form["fname"]
    last_name = request.form["lname"]
    contact_number = request.form["Contact"]
    email = request.form["email"]
    address = request.form["Address"]
    # Create and save the user
    error=False
    if User.query.filter_by(username=username).first():
      flash('Username already taken!','validation_error')
      error=True
    if '.' not in email or '@' not in email:
      flash('Invalid email address!','validation_error')
      error=True
    if error != True:
      app.security.datastore.create_user(username=username, password=password, first_name=first_name, last_name=last_name, contact_number=contact_number, email=email, address=address)
      db.session.commit()
      user = db.session.query(User).filter_by(username=username).first()
      # if username[-4:] == 'SU-A':
      #   role = db.session.query(Role).filter_by(name='Admin').first()
      # elif username[-4:] == 'SU-M':
      #   role = db.session.query(Role).filter_by(name='Manager').first()
      # else:
      #   role = db.session.query(Role).filter_by(name='Shopper').first()
      # role_user = RolesUsers(user_id=user.id, role_id=role.id)
      # db.session.add(role_user)
      # db.session.commit()
      if User.query.count() == 1:
        role = db.session.query(Role).filter_by(name='Admin').first()
        role_user = RolesUsers(user_id=user.id, role_id=role.id)
        db.session.add(role_user)
        db.session.commit()
        
    result = login_user(user)
    if result:
      return redirect('/shop')
    else:
      flash('Login Failed :(','unknown_error')
  return render_template('security/register_user.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
  if request.method == "POST":
    username = request.form["Username"]
    password = request.form["Password"]
    print(request.method,request.form)
    error=False
    user = User.query.filter_by(username=username).first()
    if user:
      if verify_password(password, user.password) == False:
        flash('Invalid Username or Password!','validation_error')
        error=True
    else:
      flash('Invalid Username or Password!','validation_error')
      error=True
    if error != True:
      result = login_user(user)
      if result:
        if 'Admin' in user.roles or 'Manager' in user.roles:
          return redirect('/inventory')
        return redirect('/shop')
      else:
        flash('Login Failed :(','unknown_error')
  return render_template('security/login_user.html')
  
@app.route('/logout')
def signout():
  result = logout_user()
  if result:
    return redirect('/login')
  else:
    return 'Logout Failed :('





@app.route("/shop", methods=["GET"])
@login_required
@cache.cached(timeout=30)
def shop():
  return render_template("shopperDash.html")

@app.route("/inventory", methods=["GET"])
@login_required
@roles_accepted('Manager','Admin')
@cache.cached(timeout=30)
def inventory():
  return render_template("managerDash.html")

@cache.cached(timeout=30)
@app.route("/summary", methods=["GET"])
@login_required
@roles_accepted('Manager','Admin')
def summary():
  # return "Hello!"
  return render_template("summary.html")

# @cache.cached(timeout=30)
@app.route("/search", methods=["GET","POST"])
@login_required
def search():
  # if request.method == "GET":
  #   return "Hi!"
  # if request.method == "GET":
  #   return "Yo!"
  return render_template("search.html")

@cache.cached(timeout=30)
@app.route("/profile", methods=["GET"])
@login_required
def profile():
  # return "Hi!"
  return render_template("userProfile.html") 





@app.route('/create-role/<string:role>')
@login_required
@roles_required('Admin')
def create_role(role):

    app.security.datastore.create_role(name=role)
    db.session.commit()

    return "Role Created Successfully"


@app.route("/get-roles")
@login_required
@roles_required('Admin')
def get_roles():
    return str([x.name for x in db.session.query(Role).all()])


@app.route("/grant-role/<string:username>/<string:role>")
@login_required
@roles_required('Admin')
def grant_roles(username,role):
  user = User.query.filter_by(username = username).first()
  role = Role.query.filter_by(name = role).first()
  role_user = RolesUsers(user_id=user.id, role_id=role.id)
  db.session.add(role_user)
  db.session.commit()
  return 'Access Granted'



@app.route("/get-users/<string:ID>")
def get_users(ID):
  if ID == 'all':
    return {user.id: {"username": user.username,
                      "first_name": user.first_name,
                      "last_name": user.last_name,
                      "email": user.email,
                      "address": user.address,
                      "contact_number": user.contact_number,
                      "roles": [role.name for role in user.roles],
                      "orders": [[order.order_id,order.timestamp,order.order, order.total_price] for order in user.orders]} for user in db.session.query(User).all()},200
  elif ID == 'this':
    startDate = datetime(date.today().year, date.today().month - 1, 1) if date.today().month > 1 else date(date.today().year - 1, 12, 1)
    try:
      return {"username": current_user.username,
          "first_name": current_user.first_name,
          "last_name": current_user.last_name,
          "email": current_user.email,
          "address": current_user.address,
          "contact_number": current_user.contact_number,
          "id": current_user.id,
          "roles": [role.name for role in current_user.roles],
          "orders": [{'order_id' : order.order_id, 'timestamp' : order.timestamp, 'order' : [item for item in order.order.split('\n')], 'total_price' : order.total_price} for order in current_user.orders if order.timestamp >= startDate]}, 200
    except Exception as e:
      return str(e)
  else:
    return 'Looking at the wrong place buddy...',404

# @app.route('/hashtest/')
# def hashtest():
#   return hash_password(ADMIN_PERMISSION)

@app.route('/OTP')
def otp():
  if LAST_ACCESS <= datetime.utcnow() + timedelta(minutes=-2):
    global OTP
    OTP = str(randint(10000,999999))
    with smtplib.SMTP("localhost", 1025) as mail:
        sender = "team@blinkbasket.com"
        password = "1234"
        mail.login(sender, password)
        
        admin = User.query.filter(User.roles.any(Role.name == 'Admin')).first()
    
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = admin.email
        msg['Subject'] = 'OTP'
        
        text_attachment = MIMEText(str(OTP))
        text_attachment.add_header("content-disposition", f"attachment; filename=notification")
        msg.attach(text_attachment)

        mail.sendmail(sender, admin.email , msg.as_string())
        print(f'Mail sent to {admin.username}')
  return {'response':'OK'}, 200

@app.route('/permit/<string:passkey>')
def permit(passkey):
  print(f'looking for OPT == {OTP} ()')
  print(f'got the OPT == {passkey}')
  if OTP == passkey:
  # if ADMIN_PERMISSION == passkey:
    global LAST_ACCESS
    LAST_ACCESS = datetime.utcnow()
    return {'data': ['GRANTED']}, 200
  return {'data': ['INVALID']}, 200

@app.route('/shopreset')
def esapeToShop():
  return redirect('/shop')

# @cache.cached(timeout=30)
@app.route("/summary/data", methods=["GET"])
def data():
  with app.app_context():
    startDate = datetime(date.today().year, date.today().month, 1)
    sectionData = {section.category_name: 0 for section in Category.query.all()}
    productData = {product.product_name: [0,product.stock] for product in Product.query.all()}
    trafficData = {day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
    
    for transaction in Transaction.query.filter(Transaction.timestamp >= startDate).all():
      trafficData[transaction.timestamp.strftime('%a')] += 1
      for item in transaction.order.split('\n'):
        product = Product.query.filter_by(product_name = item.split(' x ')[1]).first()
        section = db.session.query(Product, Category).join(Category, Product.category_id == Category.category_id).filter(Product.product_name ==  item.split(' x ')[1]).first()[1]
        productData[product.product_name][0] += (int(item.split(' x ')[0]) * product.price)
        sectionData[section.category_name] += (int(item.split(' x ')[0]) * product.price)
    
    sectionData_ = { 'labels' : [], 'values' : []}
    for item in sectionData.items():
      sectionData_['labels'].append(item[0])
      sectionData_['values'].append(item[1])
    
    productData_ = { 'labels' : [], 'values' : []} 
    for item in productData.items():
      productData_['labels'].append(item[0])
      productData_['values'].append(item[1])
    
    trafficData_ = { 'labels' : [], 'values' : []}
    for item in trafficData.items():
      trafficData_['labels'].append(item[0])
      trafficData_['values'].append(item[1])
      
    
    bar_chart(productData_['labels'],[item[0] for item in productData_['values']],'Rs. ','Products','Revenue (in Rs.)','Product-wise Revenue','0R')
    bar_chart(productData_['labels'],[item[1] for item in productData_['values']],'SKU ','Products','Stock (in SKU)','Product-wise Inventory','0S')
    pie_chart(sectionData_['labels'],sectionData_['values'],'Section-wise Revenue','0')
    line_chart(trafficData_['labels'], trafficData_['values'],'SKU ','Days of Week','Stock (in SKU)','Daily Traffic','0')
    
    return {
      'summary' :{
        'nUsers': User.query.count(),
        'nOrders': Transaction.query.count(),
        'tRevenue': db.session.query(func.sum(Transaction.total_price)).scalar(),
        'nSections': Category.query.count(),
        'nProducts': Product.query.count(),
        'tStock': db.session.query(func.sum(Product.stock)).scalar(),
        'month': date.today().strftime('%B'),
      }}, 200
      # 'sectionData' : sectionData_,
      # 'productData' : productData_,
      # 'trafficData' : trafficData_,
      





@app.route("/sectionImage", methods=["POST"])
def secImg():
  with app.app_context():
    import time
    time.sleep(3)
    if 'category_id' in request.form:
      section = Category.query.filter_by(category_id = request.form['category_id']).first()
    else:
      section = Category.query.filter_by(category_name = request.form['category_name']).first()
    if section:
      # return (str(request.files))
      if 'Image' in request.files and request.files['Image'].filename != '':
        request.files['Image'].save("../static/images/sections/"+str(section.category_id)+".png")
      else:
        if os.path.isfile("../static/images/sections/"+str(section.category_id)+".png") != True:
          shutil.copy('../static/images/default.png',"../static/images/sections/"+str(section.category_id)+".png")
      return redirect("/inventory")
    return "ERROR"

@app.route("/productImage", methods=["POST"])
def prodImg():
  import time
  time.sleep(3)
  with app.app_context():
    # return request.form [request.form, request.files]
    if 'product_id' in request.form:
      product = Product.query.filter_by(product_id = request.form['product_id']).first()
    else:
      product = Product.query.filter_by(product_name = request.form['product_name']).first()
    if product:
      # return (str(request.files))
      if 'Image' in request.files and request.files['Image'].filename != '':
        request.files['Image'].save("../static/images/products/"+str(product.product_id)+".png")
        return redirect("/inventory")
      else:
        if os.path.isfile("../static/images/products/"+str(product.product_id)+".png") != True:
          shutil.copy('../static/images/default.png',"../static/images/products/"+str(product.product_id)+".png")
      return redirect("/inventory")
    return "ERROR"

# @app.route("/delete/<entity>/<obj>")
# def delImg(entity,obj):
#   return ["Hi"]
#   os.remove('../static/images/'+ entity +'/'+ obj +'.png')

@app.route("/checkout/<string:order_details>")
def checkout(order_details):
    with app.app_context():
      order_details =  [i.split('_x_') for i in order_details.rstrip('+').split('+')]
      # print(order_details)
      # return [order_details]
      total = 0
      
      for i in range(len(order_details)):
        qty = order_details[i][0]
        item = order_details[i][1]
        product = Product.query.filter_by(product_name=item).first()
        # print(item,qty)
        product.stock = product.stock - int(qty)
        db.session.commit()
        total += (int(qty) * int(product.price))
      
      print(total)
      # return([total])
      # print(current_user.id)
      order = Transaction(user_id=current_user.id, order='\n'.join([' x '.join(i) for i in order_details]), total_price=total)
      db.session.add(order)
      db.session.commit()
      return {"data": "Order Placed :)"}, 200

@app.route("/async")
def async_export():
  with app.app_context():
    startDate = datetime(date.today().year, date.today().month, 1)
    sectionData = {section.category_name: 0 for section in Category.query.all()}
    productData = {product.product_name: 0 for product in Product.query.all()}
    
    for transaction in Transaction.query.filter(Transaction.timestamp >= startDate).all():
      for item in transaction.order.split('\n'):
        product = Product.query.filter_by(product_name = item.split(' x ')[1]).first()
        section = db.session.query(Product, Category).join(Category, Product.category_id == Category.category_id).filter(Product.product_name ==  item.split(' x ')[1]).first()[1]
        productData[product.product_name] += (int(item.split(' x ')[0]) * product.price)
        sectionData[section.category_name] += (int(item.split(' x ')[0]) * product.price)

    pTotal = max(sum(list(sectionData.values())),1)
    csv_list=[]
    for product in Product.query.order_by(Product.product_id).all():
      section = db.session.query(Product, Category).join(Category, Product.category_id == Category.category_id).filter(Product.product_name ==  product.product_name).first()[1]
      csv_list.append({'ID': product.product_id, 'Name': product.product_name, 'SectionID': section.category_id,
                       'Section_Name': section.category_name, 'Price': product.price, 'Unit': product.unit,
                       'Mfd': product.mfd.strftime('%d-%m-%Y'), 'Expd': product.expd.strftime('%d-%m-%Y'), 'Stock': product.stock,
                       'nOrders':  productData[product.product_name]//product.price, 'Revenue': productData[product.product_name],
                       'Pctg_Revenue_Overall': round(productData[product.product_name]/pTotal,2),
                       'Pctg_Revenue_Sectionally': round(productData[product.product_name]/max(sectionData[section.category_name],1),2)})
  try:      
    exporting_task.delay(csv_list)
    return {'resp': 'The export job is ready!'}, 200
  except Exception as e:
    return {'resp': str(e)}, 404

@app.route("/export")
@login_required
@roles_accepted('Admin','Manager')
def download_export():
  return send_file('../collection/export.csv', as_attachment=True)


@app.route("/test")
def test():
  # return 'Nothing to see here! :]'
  return render_template("test.html")

  
from api import SectionAPI, ProductAPI
api.add_resource(SectionAPI, "/api/section", "/api/section/<string:category_id>")
api.add_resource(ProductAPI, "/api/product", "/api/product/<string:product_id>")



if __name__ == "__main__":
  with app.app_context():
    db.create_all()
    # print([i.category_name for i in Category.query.all()])
  app.run(host="127.0.0.1", port="8080", debug=True)