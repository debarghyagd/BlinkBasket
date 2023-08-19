# BlinkBasket-2.0
>This repo is of a Flask-based full-stack online grocery shopping website (PWA) that caters to both customers and management. It implements role-based access, providing separate logins and views for shoppers and staff. Shoppers can browse, search, add to cart, and purchase products from various categories. Meanwhile, staff can manage inventory, create, update, delete items, and export summaries for analysis and inventory control.

## Overall System Description
#### Designed with distinct user groups in mind, the system comprises the following main components:
1. **Shopping Area**: Displays Category (e.g., produce, dairy) cards. Clicking on a category
expands to show the corresponding Products that can be added to the cart.
2. **User Cart**: Allows shoppers to view and modify items in their cart.
3. **Search Icon**: Enables shoppers to search for specific products.
4. **Inventory Area**: Shows Category cards for staff to manage items. This includes adding
new products.
5. **Summary Section**: Provides managers/admins with inventory status, business metrics
(stocks, revenue), order trends, and traffic insights.
6. **Data Export**: Enables storing inventory data locally on staff systems.
7. **User Profile & Logout**: Displays account information and purchase history.

## Backend
#### A combination of MVC & MVVC architecture was employed. The backend was built using Flask and associated Flask frameworks for DB, API, Security, and Caching. Product attributes were stored in the database, while static files (images, export.csv) were hosted locally. The backend communicates with front-end HTML files using Flask's render_template. The admin manages user access privileges, roles, and creation via secret routes. The first signup becomes the Admin.

## Frontend
#### The Vue2 JS framework (CDN) and Bootstrap5 were used for client-side rendering. Vue components were used for products and cart items, using custom delimiters to distinguish them from Jinja placeholders. Vue fetches data from the backend using fetch API calls. Validation errors were handled using Jinja2, flash messages, and Bootstrap.

## Database & API 
#### **Database**: Flask_SQLAlchemy Framework (sqlite3)
> - User(*id,username,first_name,last_name,email,address,contact_no, orders*),
> - Role(*id,name), Category(category_id,category_name, products*),
> - Product(*product_id,product_name, category_id, stock,price,mfd,expd, last_updated*),
> - Transaction(*order_id,order,timestamp,total), user_role(user_id, role_id*)
> - Cart (*localStorage*): [*<Product>(+qty), <Product>(+qty), <Product>(+qty)...*]

#### **API**: Flask_RESTful
> - *SectionAPI*: Fetches and displays views.
> - *ProductAPI*: Handles item creation, manipulation, and search.

## Security & Validation
#### Flask Security Too was used for user session management, custom login/registration views, role-based access, and form validation using inline JavaScript and Bootstrap. OTPs were emailed to the Admin for Manager's permits to modify inventory. Vue directives were employed to conditionally restrict access to components/routes, ensuring data integrity. 

## Caching & Batch Jobs for Notification, Reporting & Exporting
#### Flask Caching with Redis and Celery was used for caching routes and executing batch jobs. Batch jobs include email notifications, monthly reports, and user-triggered exports. Additional jobs include cleaning unused files and daily de-stocking of expired items. 

## Summary & Analytics
#### The summary page showcases the current month's inventory data and comparative analysis through charts:
 - **Section-wise Revenue Percentage**: *Pie Chart*
 - **Individual Product Stock**: *Bar Chart*
 - **Revenue per Product**: *Bar Chart*
 - **Order Traffic per Weekday**: *Line Chart*
I used *matplotlib.plt* to generate chart images(.png) to render through *img*-tags.
