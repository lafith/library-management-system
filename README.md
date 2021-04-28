# LbMS- Library Management System

LbMS is a simple web application for library management.
It is developed using [Flask](https://flask.palletsprojects.com/en/1.1.x/) framework.

## Requirements:

```console
foo@bar:~$ pip install -r requirements.txt
```

## Initializing sqlite database:

```console
foo@bar:~$ flask db init
foo@bar:~$ flask db migrate
foo@bar:~$ flask db upgrade
```

## Run LbMS:

```console
foo@bar:~$ python3 lbms.py
```

## Implemented functionalities:

- A librarian can maintain Books, Members and Transactions
- CRUD operations on Books and Members
- Issuing a book to a member
- Returning a book; Rent fee & Debt limit is specified in config file
- Search for a book by name and author
- Importing books from [Frappe API](https://frappe.io/api/method/frappe-library)
- Downloadable reports of popular books and highest paying members
- Charts for visualizing reports
- Guest view for members to browse the catalogue
- Deployed on [PythonAnywhere](http://lafith.pythonanywhere.com/)
