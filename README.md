This project is a Password Manager application built using Python and Tkinter for the GUI. It securely stores, manages, and retrieves user passwords, leveraging Fernet encryption from the cryptography library. MySQL is used for database management, storing user credentials and encrypted passwords.

Features
Secure Login: Users authenticate securely using their credentials.
Password Encryption with Salt: Passwords are encrypted using Fernet encryption and a salt for added security. This ensures each password is uniquely encrypted.
Password Generation: Users can generate strong, random passwords.
Account Management: Add, store, and retrieve account details securely.
Password Retrieval: Decrypt stored passwords with the correct authentication key.
Database Management: Uses MySQL for storing and managing account information.
Admin Settings: Includes functionalities such as database reset.
Requirements
Python 3.x
Tkinter
cryptography library
MySQL server
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/password-manager.git
cd password-manager
Install the required Python packages:

bash
Copy code
pip install -r requirements.txt
Setup MySQL Database:

Create a new MySQL database.
Create tables using the provided SQL script (setup.sql).
Configure Database Connection:

Update the database connection details in the config.py file with your MySQL credentials.
Usage
Run the application:

bash
Copy code
python main.py
Login/Register:

Use the application to register a new user or login with existing credentials.
Manage Passwords:

Add new account details with passwords.
Retrieve and manage stored passwords.
Admin Settings:

Use admin functionalities to manage the database.
Encryption Details
Passwords are encrypted using Fernet encryption from the cryptography library.
A salt is used during the encryption process to ensure that each password is uniquely encrypted even if the plaintext passwords are the same.
The salt is stored securely and used during decryption to retrieve the original password.
