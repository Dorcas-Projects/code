Overall, this project is a comprehensive implementation of our NittanyBusiness platform. The NittanyBusiness platform is a website that allows sellers to sell products to businesses. It is meant to create an intuitive and simple way for small and medium sized enterprises to purchase products via an online marketplace. This way, the supply chain is simplified and businesses are given an easy way to interact with and search for products they may need. To briefly explain the project functionaility, we start with a login page. You can either log in as a buyer or seller. There is also a help desk login meant for employees of NittanyBusiness. Buyers can surf the marketplace for items they need and can add products to their cart and checkout. They can also leave reviews and have the freedom to change their password or business name whenever they would like. Any other changes would need approval from a help desk staffer. Buyers can search the marketplace through a typical type and search or by category using our category hierarchy. Sellers can list products for sale and list what categories the product(s) belong in. They can change their password, business name, and bank details, but would need help desk approval for any other changes. If a seller wants to list a product under a category that does not yet exist within the website, they can submit a request to the help desk, highlighting a main feature and functionality of the help desk feature. As we can see, the NittanyBusiness platform is a basic and intutive way for businesses to buy products, similar to Amazon, but focused on meeting the needs of businesses.

MAIN FUNCTIONALITIES:
User login and registration
Product Listing and Order Management
Categorical Hierarchy and Search Functionality
Product/Seller Review
Updating User Information
Shopping Cart (extra functionality)
Helpdesk Support (extra functionality)

*A more detailed explanation of the functionalities and features will be under the app.py description*
 
There are 2 main files within this project, both of which I will give a short description of:

data_setup.py: This python script was used for us to populate the database for our test use. The function of this code is to go through the Users csv file and input each username and password combo into our database. So, let me quickly go through the logic. We define a simple function called sha256hash which sha256 hashes a password. This completes the hashing requirement to increase the security and privacy of our users' passwords. Then, the u_setup() function filters through the Users csv file and inputs each username/password into the database. First, it establishes a connection with the database, then creates the USERS table. Once the setup part is complete, it goes into the Users csv and reads through it. Each new row is a new username/password combo, and thus for each row, it inputs the username and hashed password into the database as a new USER entry. This repeats for all other data needed in the databse, and we go through a similar process the populate all other tables.

app.py: This file completes the overarching logic of the project. I will include a description of what all the functions in this file do and what functionalities they help implement. ALL DETAILS BELOW

Like I said before, this file implements all the follow features using Flask, Python, and HTML: User Authentication and Registration, Product Listings and Category Hierarchies, Order Management, Shopping Cart and Wishlist functionality, and a Helpdesk Support system. For out backend, we used SQLite, and there are 3 different account types, buyers, sellers, and helpdesk staff. Passwords are securely hashed using SHA-256.

When we were building the site, we started on the user login and registration system. We made sure buyers and sellers could sign up using separate forms (navigate_create_buyer() and navigate_create_seller()), and after logging in (login()), the app would figure out what type of user they were using is_buyer(), is_seller(), and is_helpdesk(). Then, they are sent to the right homepage with different features all as kjubkjbkbkjbkjbkjbbjkbkjbkbjkbkjbkbexplained above. We also used functions like is_valid_new_user() and insert_buyer()/insert_seller() to make sure emails were unique and that new users were properly saved into the database.

For organizing products, we built a full category browsing system. We made it so categories could have subcategories underneath them using functions like get_subcategories() and gather_subcategories(). To help people navigate easily, we created breadcrumbs with get_category_path(), showing users exactly where they were inside the category tree. Whenever someone clicks on a category, get_category_products() pulls all products from that category and its subcategories too, so buyers can see everything related without having to sift through a huge lineup of every category possible.

Next, let us talk about the product management features. Sellers can create new products with create_product_listing(), update them using update_product_listing(), and remove them (deactivating listings) with delete_product_listing(). We also built a function get_seller_products() so sellers could view everything theyâve listed in one place. Buyers, meanwhile, can view full product details through get_product_details() and see product reviews using get_product_reviews(). For anyone looking for something specific, the search_products() function lets them search by name, description, or even price.

When it came to handling orders, we built a system that automatically updates everything when a buyer makes a purchase. The create_order() function takes care of inserting the order, lowering the productâs quantity, and adjusting the sellerâs balance. Buyers can look back at their order history with get_buyer_orders(), and sellers can view all their received orders through get_seller_orders(). We also added a way for buyers to leave reviews for items theyâve purchased using create_product_review(), so other users could read honest feedback.

We added the extra shopping cart feature as well. Buyers can add items to their cart using add_to_cart(), change quantities with update_cart_quantity(), and remove items with remove_from_cart(). If they want to clear their cart completely, we use clear_cart(). When they decide to checkout, the checkout_cart() function handles turning the cart into real orders, checking the available stock, updating the database, and wiping the cart clean afterward. It really helps the site feel like a real online store.

Finally, we built a helpdesk support system to help users who have issues or suggestions. Buyers and sellers can send support requests through submit_helpdesk_request(), and helpdesk staff can manage these requests by claiming them (claim_helpdesk_request()) and marking them completed (complete_helpdesk_request()). If someone requests a new product category, we use extract_category_info() to pull the needed details out of the message, and add_category_from_request() lets the helpdesk team add the new category straight into the system without needing to mess with the database manually.

Throughout the project, we used get_db_connection() to make sure database connections were easy to manage, and we handled user sessions securely so everyone stayed logged in and only had access to the parts of the site meant for them. Each type of user (buyer, seller, and helpdesk) gets their own home page and different available options/features. Overall, the project came together into a full online marketplace for businesses (just like Mr. Gilbert Dude wanted!), with login security, product browsing, cart checkout, product reviews, wishlists, and even a customer support system. If we had more time, we would definitely split the code into multiple smaller files for simplicity and add more security features like email verification. Also, we might add a subcription feature and make the design a little cleaner.


After those main files, there is a plethora of html files that sets up the design of each individual page. I will not go into detail on those as it is literally just designing the layout of the pages and outlining which buttons call which functions.


INSTRUCTIONS:
1. Make sure you have the required languages and software tools downloaded (Python, Flask, HTML, SQLite, JavaScript, PyCharm Professional)
2. Download the files given in the zip file and place them into a project folder
3. Open the project folder into PyCharm Professional
4. First, run the data_setup.py file to populate the database with all data provided in the CSV files
5. Then, Open the app.py file and run the app by pressing the Run button in the upper-right side of your screen
6. In the terminal, it will give you a link to "http://127.0.0.1:5000/", click on that
7. Clicking on that link will have brought you to the login page, with 2 boxes, one for you to enter your username(email), and one for your password
8. To start, let's enter a username and password provided in the Users csv, since we know it is correct and will be in our database. Just for the sake of these instructions, let's enter o5mrsfw0@nittybiz.com as the username and TbIF16hoUqGl as the password.
9. Then, click the Login button
10. Since that was a valid username/password combination, you are directed to the homepage of NittanyBusiness
11. However, if you had entered an incorrect username/password combination, then a simple red text would show up informing you of as much, saying, "Login attempt failed. Invalid email or password"
12. Or, you can create a new account, for either a buyer or seller by clicking the 'Create new buyer' or 'Create new seller' buttons
13. Once you are logged in to a buyer account, you will see buttons to go to your profile, search for products, ckeck what is in your shopping cart, and your orders
14. Also, in the top right, there is a way to request support from a Help Desk personnel and a place to logout
15. If you click your profile, you can update your password and business name
16. In the search products page, you can either search by category, which utilizes the category hierarchy, or you can search by name by just typing it in
17. The shopping cart will have all products you have clicked add to cart, and you can remove items from your cart if you wish
18. The orders page will display all orders you have placed
19. You can also review any sellers or products for which you have purchased. This includes a rating out of 5 as well as any words you may have to describe your rating
20. If you login to a seller profile, you will have a similar profile button to update your passowrd, business name, or bank details
21. There is also a products page where you can view and edit any product you have listed for sale
22. For both sellers and buyers, you can request help desk support for any updates you may need that you cannot do on your own or need permission to do
22. The last account type is a help desk account, logging in here is meant only for our staff and allows the help desk staffer to view any requests users have made for them and make any necessary changes. This account is similar to an admin account, where they have permission to make changes that users cannot do on their own

CONGRATS! You have successfully learned how to use our Nittany Business platform!
