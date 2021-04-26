from flask import render_template, request, session, Response
from flask import flash, redirect, url_for
from app import lbms_app
from app.models import Member, Book
from app.forms import RegisterForm, LoginForm
import numpy
import io
import csv
from app.api import register_library, login_user
from app.api import is_logged_in, get_allbooks, search_books
from app.api import get_members, add_member_db, update_member_db
from app.api import add_book_db, updata_book_db, delete_book_db
from app.api import add_transaction, update_transaction
from app.api import fetch_frappe, delete_member_db


@lbms_app.route('/')
@lbms_app.route('/index')
def index():
    """View function for index page"""
    return render_template('index.html')


@lbms_app.route('/about')
def about():
    """View function for About Us page"""
    return render_template('about.html')


@lbms_app.route('/register', methods=['GET', 'POST'])
def register():
    """View function for Registration page"""
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        register_library(
            form.name.data,
            form.email.data,
            form.password.data)
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@lbms_app.route('/login', methods=['GET', 'POST'])
def login():
    """View function for login page"""
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user(form.email.data)
        flash('You have been logged in!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@lbms_app.route('/logout')
@is_logged_in
def logout():
    """view function for logout tab"""
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@lbms_app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    """view function for dashboard page of each library"""
    books = get_allbooks()

    page = request.args.get('page', 1, type=int)
    books_paginated = books.order_by(
        Book.registered_date.desc()).paginate(
            page=page,
            per_page=lbms_app.config['PER_PAGE_COUNT'])

    if request.method == "POST":
        search_string = request.form["search"]
        search_by = request.form.get("searchby")

        books_paginated = search_books(search_by, search_string, books)

    return render_template('dashboard.html', books=books_paginated)


@lbms_app.route('/guest', methods=['GET', 'POST'])
def guest():
    """view function for dashboard page of each library"""
    books = get_allbooks()

    page = request.args.get('page', 1, type=int)
    books_paginated = books.order_by(
        Book.registered_date.desc()).paginate(
            page=page,
            per_page=lbms_app.config['PER_PAGE_COUNT'])

    if request.method == "POST":
        search_string = request.form["search"]
        search_by = request.form.get("searchby")

        books_paginated = search_books(search_by, search_string, books)

    return render_template('guest_view.html', books=books_paginated)


@lbms_app.route('/members')
@is_logged_in
def members():
    """View function for Member management page"""
    all_members = get_members()
    return render_template('members.html', members=all_members)


@lbms_app.route('/add_member', methods=['GET', 'POST'])
@is_logged_in
def add_member():
    """View function to add Member into database"""
    if request.method == 'POST':
        add_member_db(
            request.form['name'],
            request.form['email'],
            request.form['phone'])
        flash("New Member is added", "success")
        return redirect(url_for('members'))


@lbms_app.route('/update_member', methods=['GET', 'POST'])
@is_logged_in
def update_member():
    """View function for updating Member info"""
    if request.method == 'POST':
        update_member_db(
            request.form.get('id'),
            request.form["name"],
            request.form["email"],
            request.form["phone"])

        flash("Member Information Updated Successfully", "success")

        return redirect(url_for('members'))


@lbms_app.route('/delete_member/<id>/', methods=['GET', 'POST'])
def delete_member(id):
    """View function to remove entries from Member table"""
    delete_member_db(id)
    flash("Member Deleted Successfully")
    return redirect(url_for('members'))


@lbms_app.route('/add_book', methods=['GET', 'POST'])
@is_logged_in
def add_book():
    """View function to add Member into database"""
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        total = request.form['total']
        authors = request.form.getlist("author[]")

        add_book_db(title, isbn, total, authors)

        flash("New book is added", "success")
        return redirect(url_for('dashboard'))


@lbms_app.route('/update_book', methods=['GET', 'POST'])
@is_logged_in
def update_book():
    """View function for updating Member info"""
    if request.method == 'POST':

        book_id = request.form.get('id')
        title = request.form['title']
        isbn = request.form['isbn']
        total = request.form['total']
        authors = request.form.getlist('author[]')
        updata_book_db(book_id, title, isbn, total, authors)

        flash("Book Information Updated Successfully", "success")
        return redirect(url_for('dashboard'))


@lbms_app.route('/delete_book/<id>/', methods=['GET', 'POST'])
def delete_book(id):
    """View function to remove entries from Member table"""
    delete_book_db(id)

    flash("Book info Deleted Successfully", 'danger')
    return redirect(url_for('dashboard'))


@lbms_app.route('/issue_book', methods=['GET', 'POST'])
@is_logged_in
def issue_book():
    """View function to issue a book"""
    if request.method == 'POST':
        member_name = request.form['member']
        book_id = request.form.get('book_id')
        add_transaction(book_id, member_name)
        return redirect(url_for('dashboard'))


@lbms_app.route('/return_book', methods=['GET', 'POST'])
@is_logged_in
def return_book():
    """View function to return a book"""
    if request.method == 'POST':
        member_name = request.form['member']
        book_id = request.form.get('book_id')
        update_transaction(book_id, member_name)

        return redirect(url_for('dashboard'))


@lbms_app.route('/import_books', methods=['GET', 'POST'])
@is_logged_in
def import_books():
    url = "https://frappe.io/api/method/frappe-library"
    if request.method == 'POST':
        params = request.form.to_dict()
        required = int(params['total'])
        params.popitem()
        params = {
            key: val for key, val in params.items() if val != ''}

        fetch_frappe(url, params, required)

        return redirect(url_for('dashboard'))


@lbms_app.route('/download_report/<rp>')
@lbms_app.route('/report', methods=['GET', 'POST'])
@is_logged_in
def report(rp=None):
    books = Book.query.filter_by(
        library_id=session["library_id"])
    counts = [book.transactions.count() for book in books]
    counts = numpy.array(counts)
    index_1 = numpy.argsort(counts)[-10:]
    counts = counts[index_1].tolist()
    isbn = [books[i].isbn for i in index_1]
    available = [books[i].available for i in index_1]
    total = [books[i].total for i in index_1]

    members = Member.query.filter_by(
        library_id=session["library_id"])
    amount = [
        member.transactions.filter_by(
            if_returned=True).count() for member in members]
    amount = [lbms_app.config['RENT_FEE']*i for i in amount]
    amount = numpy.array(amount)
    index_2 = numpy.argsort(amount)[-10:]
    amount = amount[index_2].tolist()
    names = [members[i].name for i in index_2]

    if rp == '01':
        output = io.StringIO()
        writer = csv.writer(output)

        line = [
            'Title', 'ISBN',
            'Total Transactions',
            'Available', 'Total']
        writer.writerow(line)

        for i, j in enumerate(index_1):
            line = [
                books[j].title, books[j].isbn,
                counts[i], books[j].available,
                books[j].total]
            writer.writerow(line)
        output.seek(0)
        return Response(
            output, mimetype="text/csv",
            headers={
                "Content-Disposition":
                "attachment;filename=book_report.csv"})
    elif rp == '02':
        output = io.StringIO()
        writer = csv.writer(output)

        line = ['Name', 'Amount']
        writer.writerow(line)

        for i, j in enumerate(index_2):
            line = [
                members[j].name,
                amount[i]
                ]
            writer.writerow(line)
        output.seek(0)
        return Response(
            output, mimetype="text/csv",
            headers={
                "Content-Disposition":
                "attachment;filename=payment_report.csv"})
    return render_template(
        'report.html', labels=isbn,
        data=counts, available=available,
        total=total, names=names, amount=amount)
