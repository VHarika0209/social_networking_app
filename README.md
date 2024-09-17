Markdown

# Social Connect

Social Connect is a Django application that allows users to interact by searching for other users, sending, accepting, and rejecting friend requests. This README file provides instructions for setting up and running the project.


## Features
1. **User Signup**:  
   - Users can sign up with their email (case insensitive) and password.
   - No OTP verification is required; a valid email format is sufficient.
   Example:
   POST {{base_url}}/signup/
   request_body
   {
      "email": "amarendra@gmail.com",
      "password": "123",
      "first_name": "amar",
      "last_name": "v"
   }

2. **User Login**:  
   - Users can log in with their email and password.
   - Authentication is required for all API interactions except login and signup.

   Example:
   POST {{base_url}}/login/
   request_body
   {
      "email": "amarendra@gmail.com",
      "password": "123"
   }

3. **User Search**:
   - Search other users by email or name with pagination (up to 10 results per page).
   - The search keyword can match the exact email or a substring in the name.
   
   Example:
   {{base_url}}/users/search/?keyword=amarendra@gmail.com
   {{base_url}}/users/search/?keyword=ama


4. **Friend Requests**:
   - Users can send friend requests to other users.
   - Limit: Users cannot send more than 3 friend requests per minute (rate-limited).

   Example:
   POST {{base_url}}/friend-request/send/


5. **Accept/Reject Friend Requests**:
   - Users can accept or reject pending friend requests they have received.
   - Only the receiver of the request can accept or reject it.

   Example:
   {{base_url}}/friend-request/action/4/


6. **Friend List**:
   - View a list of all accepted friends.

      Example: {{base_url}}/friend-request/list/?status=accepted

   - View a list of pending friend requests that a user has received.

      Example: {{base_url}}/friend-request/list/?status=pending


## Security
   - Authentication is required for all APIs except login and signup.
   - A rate limit is applied: users can only send 3 friend requests within one minute.

## API Endpoints
Below is a summary of the key API endpoints:

| Endpoint                                      | Method | Description                                   |
|-----------------------------------------------|--------|-----------------------------------------------|
| `/signup`                                     | POST   | Register a new user                           |
| `/login`                                      | POST   | Log in an existing user                       |
| `/users/search`                               | GET    | Search users by email or name                 |
| `/friend-request/send/`                       | POST   | Send a friend request                         |
| `/friend-request/action/{id}`                 | PATCH  | Accept/Reject a friend request                |
| `/friend-request/list/?status=accepted`       | GET    | Get a list of accepted friends                |
| `/friend-request/list/?status=pending`        | GET    | Get a list of pending friend requests         |

## Getting Started
### Prerequisites
   - Python 3.8 or higher
   - MySQL
   - Django 5.1.1
   - Django REST framework 3.15.2

### Installation
1. **Clone the repository**:


2. **Install dependencies**:
   pip install -r requirements.txt


3. **Configure MySQL Database**:
   - Set up your MySQL database and update the `DATABASES` setting in `settings.py` with your database credentials.

4. **Run Migrations**:

   python manage.py migrate


5. **Run the Development Server**:
   python manage.py runserver