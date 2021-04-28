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

### Screenshots:

- Home page:
<p align="middle">
<img src="https://user-images.githubusercontent.com/39316548/116450020-6d67e780-a878-11eb-9968-5fb26e790a42.png" width=699 height=393>
</p>

- Login & Register:
<p align="middle">
<img src="https://user-images.githubusercontent.com/39316548/116450371-d8b1b980-a878-11eb-96d2-2d2066584718.png" width=425 height=269>
<img src="https://user-images.githubusercontent.com/39316548/116450391-e0715e00-a878-11eb-8668-e98764d96b93.png" width=425 height=269>
</p>

- Dashboard:
<p align="middle">
<img src="https://user-images.githubusercontent.com/39316548/116450105-88d2f280-a878-11eb-9c5e-238e48ede77f.png" width=699 height=393>
</p>

- Members:
<p align="middle">
<img src="https://user-images.githubusercontent.com/39316548/116454624-d2720c00-a87d-11eb-85b6-184ecb216e40.png" width=699 height=393>
</p>

- Popular Books:
<p align="middle">
<img src="https://user-images.githubusercontent.com/39316548/116455108-50ceae00-a87e-11eb-8e01-edf93a5e34ba.png" width=699 height=393>
</p>

- Highest paying members:
<p align="middle">
<img src="https://user-images.githubusercontent.com/39316548/116455720-0a2d8380-a87f-11eb-9412-e4ed1a987e06.png" width=699 height=393>
</p>

- Guest view:
<p align="middle">
<img src="https://user-images.githubusercontent.com/39316548/116455302-85426a00-a87e-11eb-8b23-f3e88cc8d73f.png" width=699 height=393>
</p>
