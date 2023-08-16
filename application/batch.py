from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import pdfkit
# from sqlalchemy import in_

import os
# import datetime
from datetime import datetime, date, time, timedelta


from models import *
from app import app
from charts import bar_chart, pie_chart

from celery import Celery
from celery.schedules import crontab

celery = Celery("tasks", 
                backend='redis://localhost:9736/1', 
                broker="redis://localhost:9736/1",
                # broker_connection_retry_on_startup=True
                )

celery.conf.timezone = 'Asia/Kolkata'  

@celery.task
def testing_task():
    print('hi')
          
@celery.task
def reporting_task():
    startDate = datetime(date.today().year, date.today().month - 1, 1) if date.today().month > 1 else date(date.today().year - 1, 12, 1)
    # startDate = datetime(date.today().year, date.today().month, 1)
    endDate = datetime(date.today().year, date.today().month, 1)
    with app.app_context():
        users = User.query.all()
        for user in users:
            user_total = 0
            orders = [order for order in user.orders if (order.timestamp >= startDate and order.timestamp < endDate)]
            # orders = [order for order in user.orders if order.timestamp >= startDate]
            categories = {section.category_name : 0 for section in Category.query.all()}
            products = {product.product_name : 0 for product in Product.query.all()}
            htmlString= '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monthly Report</title>
    <style>
        .header {
            padding: 20px;
            padding-left: 45%;
            background-color: green;
            color: white;
        }
        .details {
            font-size: large;
            padding-left: 1%;
            width: 50%;
        }
        .details tr:nth-child(odd) {
            background-color: #f2f2f2;
        }
        .orders {
            width: 100%;
            text-align: left;
            padding-left: 1%;
        }
        .orders tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .orders th{
            background-color: rgba(64, 131, 64, 0.507);
            padding: 10px;
            
        }
        .orders td {
            padding: 10px;
        }
        .orders li {
            list-style-type: none
        }
    </style>
</head>'''
            htmlString += f'''
<body>
    <h1 class="header">BlinkBasket</h1>
    <h2 style="padding-left: 1%; background-color: rgba(0, 128, 0, 0.5);">Detail</h2>
    <table class="details">
        <tr>
            <td><strong>Username:</strong></td>
            <td>{user.username}</td>
        </tr>
        <tr>
            <td><strong>First Name:</strong></td>
            <td>{user.first_name}</td>
        </tr>
        <tr>
            <td><strong>Last Name:</strong></td>
            <td>{user.last_name}</td>
        </tr>
        <tr>
            <td><strong>Email:</strong></td>
            <td>{user.email}</td>
        </tr>
        <tr>
            <td><strong>Phone Number:</strong></td>
            <td>{user.contact_number}</td>
        </tr>
        <tr>
            <td><strong>Address:</strong></td>
            <td>{user.address}</td>
        </tr>
    </table>
    <br>
    <h2 style="padding-left: 1%; background-color: rgba(0, 128, 0, 0.5);">Orders</h2>
    <table class="orders">
        <tr>
			<th>ID</th>
			<th>Date</th>
			<th>Products</th>
			<th>Total</th>
        </tr>'''
            for order in orders:
                htmlString += f'''
        <tr>
			<td>{order.order_id}</td>
			<td>{order.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</td>
			<td>'''

                for item in order.order.split('\n'):
                    prod = item.split(' x ')[1]
                    val = int(item.split(' x ')[0])
                    product = Product.query.filter_by(product_name = prod ).first()
                    category = Category.query.filter_by(category_id = product.category_id ).first()
                    products[product.product_name] += val*product.price
                    categories[category.category_name] += val*product.price
                    htmlString += f'''
                <li>{item}</li>'''
                htmlString += f'''
            </td>
			<td>Rs. {order.total_price}</td>
        </tr>'''
                user_total += order.total_price
            pie_chart([item[0] for item in categories.items()],[item[1] for item in categories.items()],'Section-wise Expenditure',str(user.id))
            bar_chart([item[0] for item in products.items()],[item[1] for item in products.items()],'Rs. ','Products','Expenditure (in Rs.)','Product-wise Expenditure',str(user.id))
            category_labels = [item[0] for item in categories.items()]
            category_values = [round(i*100/user_total, 2) for i in [item[1] for item in categories.items()]] if user_total != 0 else [item[1] for item in categories.items()]
            product_labels = [item[0] for item in products.items()]
            product_values = [item[1] for item in products.items()]
            htmlString += f'''
        <tr>
            <th colspan="3">Total:</th>
            <td style="background-color: rgba(0, 128, 0, 0.5);">Rs. {user_total}</td>
		</tr>
    </table>
    <br>
    <h2 style="padding-left: 1%; background-color: rgba(0, 128, 0, 0.5);">Stats</h2>
    <table class="orders">
        <tr>
            <th>Category</th>
            <th>Expense</th>
        </tr>'''
            for i in range(len(category_labels)):
                htmlString += f'''
        <tr>
            <td>{category_labels[i]}</td>
            <td>{category_values[i]} %</td>
        </tr>'''
            htmlString += '''
    </table>
    <br>
    <table class="orders">
        <tr>
            <th>Product</th>
            <th>Expense</th>
        </tr>'''
            for i in range(len(product_labels)):
                htmlString += f'''
        <tr>
			<td>{product_labels[i]}</td>
			<td>Rs. {product_values[i]}</td>
        </tr>'''
            htmlString += '''
    </table>
</body>
</html>'''
            # print(htmlString)
            with open(f'../collection/Reports/HTML/{user.id}.html','w') as f:
                f.write(htmlString)
            pdfkit.from_file(f'../collection/Reports/HTML/{user.id}.html', f'../collection/Reports/PDF/{user.id}.pdf')
            
            with smtplib.SMTP("localhost", 1025) as mail:
                sender = "team@blinkbasket.com"
                password = "1234"
                mail.login(sender, password)
            
                msg = MIMEMultipart()
                msg['From'] = sender
                msg['To'] = user.email
                msg['Subject'] = 'Monthly Report'
                
                html_filename = f'../collection/Reports/HTML/{user.id}.html'
                with open(html_filename) as f:
                    content = f.read()
                html_attachment = MIMEText(content, "html")
                html_attachment.add_header("content-disposition", f"attachment; filename={user.username}.html")
                msg.attach(html_attachment)
                
                pdf_filename = f'../collection/Reports/PDF/{user.id}.pdf'
                with open(pdf_filename, "rb") as f:
                    content = f.read()
                pdf_attachment = MIMEBase("application", "octet-stream")
                pdf_attachment.set_payload(content)
                encoders.encode_base64(pdf_attachment)
                pdf_attachment.add_header("content-disposition", f"attachment; filename={user.username}.pdf")
                msg.attach(pdf_attachment)
                
                image_filename = f'../static/images/charts/Pie_{user.id}.png'
                with open(image_filename, "rb") as f:
                    content = f.read()
                image_attachment = MIMEBase("application", "octet-stream")
                image_attachment.set_payload(content)
                encoders.encode_base64(image_attachment)
                image_attachment.add_header("content-disposition", f"attachment; filename=Pie_{user.username}.png")
                msg.attach(image_attachment)

                image_filename = f'../static/images/charts/Bar_{user.id}.png'
                with open(image_filename, "rb") as f:
                    content = f.read()
                image_attachment = MIMEBase("application", "octet-stream")
                image_attachment.set_payload(content)
                encoders.encode_base64(image_attachment)
                image_attachment.add_header("content-disposition", f"attachment; filename=Bar_{user.username}.png")
                msg.attach(image_attachment)

                mail.sendmail(sender, user.email, msg.as_string())
                print(f'Mail sent to {user.username}')
                


@celery.task
def expd_task():
    with app.app_context():
        products = Product.query.all()
        with open('../collection/expdLogs.txt','a') as f:
            for product in products:
                if product.expd <= datetime.utcnow():
                    product.stock = 0
                    db.session.commit()
                    f.write(f'{product.product_id} : {product.product_name} expired on {product.expd}\n')
                    print(f'{product.product_id} : {product.product_name} expired on {product.expd}')
            f.write('\n')
        with smtplib.SMTP("localhost", 1025) as mail:
            sender = "team@blinkbasket.com"
            password = "1234"
            mail.login(sender, password)   
            users=[{"username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email} for user in User.query.filter(User.roles.any(Role.name.in_(['Admin', 'Manager']))).all()]
            for user in users:
                msg = MIMEMultipart()
                msg['From'] = sender
                msg['To'] = user["email"]
                msg['Subject'] = 'Expiry Log'   
                with open('../collection/expdLogs.txt') as f:
                    content = f.read()
                text_attachment = MIMEText(content)
                text_attachment.add_header("content-disposition", f"attachment; filename=expdLogs")
                msg.attach(text_attachment)    
                
                mail.sendmail(sender, user["email"], msg.as_string())
                print(f'Mail sent to {user["username"]}')
            print('Expiry Check Complete')     
                    

@celery.task
def deleting_task():
    with app.app_context():
        products = [product.product_id for product in Product.query.all()]
        prod_img = os.listdir('../static/images/products')
        for img in prod_img:
            if int(img[:-4]) not in products:
                os.remove('../static/images/products/'+img)
                print(f'Deleted ../static/images/products/{img}')
        category = [category.category_id for category in Category.query.all()]
        cat_img = os.listdir('../static/images/sections')
        for img in cat_img:
            if int(img[:-4]) not in category:
                os.remove('../static/images/sections/'+img)
                print(f'Deleted ../static/images/sections/{img}')

@celery.task
def mailing_task():
    with smtplib.SMTP("localhost", 1025) as mail:
        sender = "team@blinkbasket.com"
        password = "1234"
        mail.login(sender, password)
        with app.app_context():
            today = datetime.utcnow().date()
            startDate = datetime(today.year,today.month,today.day)
            nUsers = User.query.join(User.orders).filter(User.orders,Transaction.timestamp >= startDate).all()
            users=[{"username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email} for user in User.query.all() if user not in nUsers]
            
            # users=[{"username": user.username,
            #         "first_name": user.first_name,
            #         "last_name": user.last_name,
            #         "email": user.email} for user in User.query.all()]
            
        for user in users:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = user["email"]
            msg['Subject'] = 'Long no see... 😢'

            # Attach a text file
            # text_filename = "text.txt"
            # with open(text_filename) as f:
            #     content = f.read()
            
            content = f"Hey there, {user['first_name']}!\n🛒 We noticed your cart's been napping today. Time to wake it up with delicious possibilities! \nFresh produce, pantry essentials - it's all just a click away. \nHappy shopping! 🥦🥖🛍️"
            text_attachment = MIMEText(content)
            text_attachment.add_header("content-disposition", f"attachment; filename=notification")
            msg.attach(text_attachment)


            # doc_filename = "document.doc"
            # with open(doc_filename, "rb") as f:
            #     content = f.read()
            # doc_attachment = MIMEBase("application", "octet-stream")
            # doc_attachment.set_payload(content)
            # encoders.encode_base64(doc_attachment)
            # doc_attachment.add_header("content-disposition", f"attachment; filename={doc_filename}")
            # msg.attach(doc_attachment)

            # csv_filename = "data.csv"
            # with open(csv_filename, "rb") as f:
            #     content = f.read()
            # csv_attachment = MIMEBase("application", "octet-stream")
            # csv_attachment.set_payload(content)
            # encoders.encode_base64(csv_attachment)
            # csv_attachment.add_header("content-disposition", f"attachment; filename={csv_filename}")
            # msg.attach(csv_attachment)
            
            mail.sendmail(sender, user["email"], msg.as_string())
            print(f'Mail sent to {user["username"]}')
        print('Mailing Job Complete')
            
celery.conf.beat_schedule = {
    # 'print-hi-every-10-seconds': {
    #     'task': 'batch.testing_task',
    #     'schedule': 10.0,  # Every 10 seconds
    # },
    'mail-every-day': {
        'task': 'batch.mailing_task',
        'schedule': crontab(),    #Every day at 6
        # 'schedule': crontab(minute=0, hour=18),    #Every day at 6
    },
    'delete-every-month': {
        'task': 'batch.deleting_task',
        # 'schedule': crontab(minute=0, hour=18, day_of_month=1),    #First day of every month at 6 PM
        'schedule': crontab(),    #First day of every month at 6 PM
    },
    'expdCheck-every-day': {
        'task': 'batch.expd_task',
        # 'schedule': crontab(minute=0, hour=0),    #Every day at 12 AM
        'schedule': crontab(),    #Every day at 6 PM
    },
    'report-every-month': {
        'task': 'batch.reporting_task',
        'schedule': crontab(minute=0, hour=0, day_of_month=1),    #First day of every month at 12 AM
        # 'schedule': crontab(),    
    },
}
