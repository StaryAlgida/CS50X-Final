# Your Finances
#### Video Demo:  <https://www.youtube.com/watch?v=BZ8mVqf-mAE>
#### Description:

## About the project.
My project is a simple finances app where you can split your money into smaller budgets and track the history of your income and expenditure.

## login
The login page allows the user to input login and password.
When login or password are incorrect login page return apology wyth message "Invalid username and/or password."
When the login and password are correct the user is logged into his account.

## register
On register page user can create new account passing an user name and password.
if user name is already in use side return apology with message "User already exists".

## home page
When user is logged in on the home page they can see how much money he has and two tables first with budgets and second with budgets goals.
If user has not created any budget yet, he will see the message "You don't have any budgets yet."

## budgets page
On this page user can choose if he want to create a new budget clicking add button or remove budget clicking remove button.

## budget_add page
On this page user can add new budget to his account.
The application will check if all fields have been filled in correctly.
If user select checkbox "Enable goal" that will enable goal for this budget.

## budget_remove page
This page allows the user to delete budgets.
Application will delete budget goal too.
If you wont to delete budget select your budget name from drop down list and click remove button.

## edit page
There are three buttons on the edit page:
- **Add money** user can add mone to account. The application will check if the amount of money given is correct. This function is designed to simulate revenue.
- **Remove money** user can remove money from account. The application will check if the amount of money given is correct. This function simulates expenses.
- **Edit budget** user can edit budgets by adding or removing money from it or adding goal. To edit the budget, the user must first select the name of the budget. Then select whether he wants to add money or subtract it. Finally, he can edit the limit and the target. If the budget does not have a target it will be added.

## history page
- **Budgets history** user can see the history of their budgets
- **Account history** user can see the history of their account

# data.db
The database contains 5 tables:
- **users** this table contains information on user accounts. It contains information such as username, hash password, cash
- **goals** this table contains information about budgets goals. It contains information such as budget_id, cash_goal, date_start, date_end
- **budgets** this table contains information about budgets. It contains information such as user_id, budget_name, budget_cash, cash_limit
- **budgets_history** this table contains information about history of all budgets.
- **account_history** this table contains information about the account and budgets when the budget was created and deleted.