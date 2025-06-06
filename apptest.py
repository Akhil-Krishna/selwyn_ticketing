# All imports Required
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, datetime, timedelta
import MySQLdb
from MySQLdb.cursors import DictCursor
import connect

#Initialising the Web App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'selwynRandom'


def getCursor():
    global connection
    global cursor

    if connection is None:
        connection = MySQLdb.connect(
            user=connect.dbuser,
            password=connect.dbpass,
            host=connect.dbhost,
            database=connect.dbname,
            port=int(connect.dbport),
            autocommit=True
        )
    cursor = connection.cursor(DictCursor)
    return cursor

# Format date to New Zealand format (DD/MM/YYYY)
def format_date_nz(date_obj):
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    return date_obj.strftime('%d/%m/%Y')


# Task 2 : Home Page , Task 1 : Did it in base.html ,no routes
@app.route("/")
def home():
    return render_template("home.html")


# Events Selection Page 
@app.route("/events", methods=["GET"])
def events():
    cursor = getCursor()
    if request.method=="GET":
        # Lists the events        
        qstr = "SELECT event_id, event_name FROM events;" 
        cursor.execute(qstr)        
        events = cursor.fetchall()
        return render_template("events.html", events=events)


# Task 3 : Event : name,date, list of customers purchased ticket in family and yougest order
@app.route("/events/customerlist", methods=["POST"])
def eventcustomerlist():
    cursor = getCursor()
    event_id = request.form.get('event_id')
    
    #print(event_id)
    # Get event details
    cursor.execute("SELECT event_name, event_date FROM events WHERE event_id = %s", (event_id,))
    event = cursor.fetchone()
    
    # Get customers who purchased tickets for this event
    cursor.execute("""
        SELECT c.customer_id, c.first_name, c.family_name, c.date_of_birth, c.email, ts.tickets_purchased
        FROM customers c
        JOIN ticket_sales ts ON c.customer_id = ts.customer_id
        WHERE ts.event_id = %s
        ORDER BY c.family_name, c.date_of_birth DESC
    """, (event_id,))
    customerlist = cursor.fetchall()
    
    formatted_date = format_date_nz(event['event_date'])
    
    return render_template("eventcustomerlist.html", 
                          event_name=event['event_name'],
                          event_date=formatted_date,
                          customerlist=customerlist)


# Customer Listing Page 
@app.route("/customers")
def customers():
    cursor = getCursor()
    cursor.execute("""
        SELECT customer_id, first_name, family_name, date_of_birth, email
        FROM customers
        ORDER BY family_name, first_name
    """)
    customers_list = cursor.fetchall()
    
    return render_template("customers.html", customers=customers_list)


# Task 9 : Customer Ticket Summary
@app.route("/customer/details/<int:customer_id>")
def customer_details(customer_id):
    cursor = getCursor()
    
    # Get customer details
    cursor.execute("""
        SELECT customer_id, first_name, family_name, date_of_birth, email
        FROM customers
        WHERE customer_id = %s
    """, (customer_id,))
    customer = cursor.fetchone()
    
    if not customer:
        flash("Customer not found")
        return redirect(url_for('customers'))
    
    # Get all tickets purchased by this customer
    cursor.execute("""
        SELECT e.event_name, e.event_date, ts.tickets_purchased
        FROM ticket_sales ts
        JOIN events e ON ts.event_id = e.event_id
        WHERE ts.customer_id = %s
    """, (customer_id,))
    tickets = cursor.fetchall()
    
    # Calculate total tickets purchased
    total_tickets = sum(ticket['tickets_purchased'] for ticket in tickets)
    
    # Format dates for display
    formatted_tickets = []
    for ticket in tickets:
        formatted_ticket = ticket.copy()
        formatted_ticket['event_date'] = format_date_nz(ticket['event_date'])
        formatted_tickets.append(formatted_ticket)
    
    return render_template("customerdetails.html", 
                          customer=customer, 
                          tickets=formatted_tickets, 
                          total_tickets=total_tickets)


# Task 8 : Future Events with Tickects Remaining 
@app.route("/futureevents")
def futureevents():
    cursor = getCursor()
    today = date.today()
    
    # Get future events with available tickets
    cursor.execute("""
        SELECT e.event_id, e.event_name, e.event_date, e.capacity, 
               COALESCE(SUM(ts.tickets_purchased), 0) as tickets_sold,
               e.capacity - COALESCE(SUM(ts.tickets_purchased), 0) as tickets_remaining
        FROM events e
        LEFT JOIN ticket_sales ts ON e.event_id = ts.event_id
        WHERE e.event_date > %s
        GROUP BY e.event_id
        HAVING tickets_remaining > 0
        ORDER BY e.event_date
    """, (today,))
    
    events = cursor.fetchall()
    #print(events)
    
    # Format dates for display
    for event in events:
        event['event_date_formatted'] = format_date_nz(event['event_date'])
    
    return render_template("futureevents.html", events=events)

# Task 4 : Buy Tickets , Providing A Form for Buying Tickets
@app.route("/tickets/buy", methods=["GET", "POST"])
def buytickets():
    cursor = getCursor()
    today = date.today()
    
    # Getting a Form with Dropdowns
    if request.method == "GET":
        # Get all customers
        cursor.execute("SELECT customer_id, first_name, family_name FROM customers ORDER BY family_name, first_name")
        customers = cursor.fetchall()
        
        # Get future events with available tickets
        cursor.execute("""
            SELECT e.event_id, e.event_name, e.event_date, e.age_restriction,
                   e.capacity - COALESCE(SUM(ts.tickets_purchased), 0) as tickets_remaining
            FROM events e
            LEFT JOIN ticket_sales ts ON e.event_id = ts.event_id
            WHERE e.event_date > %s
            GROUP BY e.event_id
            HAVING tickets_remaining > 0
            ORDER BY e.event_date
        """, (today,))
        events = cursor.fetchall()
        
        # Format dates for display
        for event in events:
            event['event_date_formatted'] = format_date_nz(event['event_date'])
        
        return render_template("buytickets.html", customers=customers, events=events)
    
    #Submitting Form
    elif request.method == "POST":
        customer_id = request.form.get('customer_id')
        event_id = request.form.get('event_id')
        tickets = request.form.get('tickets')
        
        if not customer_id or not event_id or not tickets:
            flash("Please fill out all fields")
            return redirect(url_for('buytickets'))
        
        try:
            tickets = int(tickets)
            if tickets <= 0:
                flash("Number of tickets must be positive")
                return redirect(url_for('buytickets'))
        except ValueError:
            flash("Invalid number of tickets")
            return redirect(url_for('buytickets'))
        
        # Check customer age against event restrictions
        cursor.execute("""
            SELECT c.date_of_birth, e.age_restriction, e.event_date, e.capacity,
                   COALESCE(SUM(ts.tickets_purchased), 0) as tickets_sold
            FROM customers c, events e
            LEFT JOIN ticket_sales ts ON e.event_id = ts.event_id
            WHERE c.customer_id = %s AND e.event_id = %s
            GROUP BY e.event_id
        """, (customer_id, event_id))
        result = cursor.fetchone()
        
        if not result:
            flash("Invalid customer or event")
            return redirect(url_for('buytickets'))
        
        dob = result['date_of_birth']
        event_date = result['event_date']
        age_restriction = result['age_restriction']
        tickets_sold = result['tickets_sold']
        capacity = result['capacity']
        
        # Calculate age at event date
        age_at_event = event_date.year - dob.year
        if (event_date.month, event_date.day) < (dob.month, dob.day):
            age_at_event -= 1
        
        # Check age restriction
        if age_at_event < age_restriction:
            flash(f"Customer does not meet the age restriction for this event (must be {age_restriction} or older)")
            return redirect(url_for('buytickets'))
        
        # Check available tickets
        tickets_remaining = capacity - tickets_sold
        if tickets > tickets_remaining:
            flash(f"Not enough tickets available. Only {tickets_remaining} tickets remaining.")
            return redirect(url_for('buytickets'))
        
        # Check if customer already has tickets for this event
        cursor.execute("""
            SELECT ticket_sales_id, tickets_purchased
            FROM ticket_sales
            WHERE customer_id = %s AND event_id = %s
        """, (customer_id, event_id))
        existing_purchase = cursor.fetchone()
        
        if existing_purchase:
            # Update existing ticket purchase
            new_total = existing_purchase['tickets_purchased'] + tickets
            cursor.execute("""
                UPDATE ticket_sales
                SET tickets_purchased = %s
                WHERE ticket_sales_id = %s
            """, (new_total, existing_purchase['ticket_sales_id']))
            flash(f"Added {tickets} more tickets to existing purchase. New total: {new_total} tickets.")
        else:
            # Create new ticket purchase
            cursor.execute("""
                INSERT INTO ticket_sales (customer_id, event_id, tickets_purchased)
                VALUES (%s, %s, %s)
            """, (customer_id, event_id, tickets))
            flash(f"Successfully purchased {tickets} tickets.")
        
        return redirect(url_for('customer_details', customer_id=customer_id))

# Task 5 : Customer Search 
@app.route("/search/customer", methods=["GET", "POST"])
def searchcustomer():
    if request.method == "GET":
        return render_template("searchcustomer.html")
    
    elif request.method == "POST":
        cursor = getCursor()
        first_name = request.form.get('first_name', '')
        family_name = request.form.get('family_name', '')
        
        # Build search query based on provided inputs
        query = "SELECT customer_id, first_name, family_name, email FROM customers WHERE 1=1"
        params = []
        
        if first_name:
            query += " AND first_name LIKE %s"
            params.append(f"%{first_name}%")
        
        if family_name:
            query += " AND family_name LIKE %s"
            params.append(f"%{family_name}%")
        
        query += " ORDER BY family_name, first_name"
        
        cursor.execute(query, tuple(params))
        search_results = cursor.fetchall()
        
        return render_template("searchcustomer.html", 
                              results=search_results, 
                              first_name=first_name, 
                              family_name=family_name)


# Task 6 : Add Customers
@app.route("/customer/add", methods=["GET", "POST"])
def addcustomer():
    if request.method == "GET":
        return render_template("addcustomer.html")
    
    elif request.method == "POST":
        cursor = getCursor()
        
        # Get form data
        first_name = request.form.get('first_name')
        family_name = request.form.get('family_name')
        date_of_birth = request.form.get('date_of_birth')
        email = request.form.get('email')
        
        # Validate form data
        if not first_name or not family_name or not date_of_birth or not email:
            flash("All fields are required")
            return render_template("addcustomer.html", 
                                  first_name=first_name, 
                                  family_name=family_name, 
                                  date_of_birth=date_of_birth, 
                                  email=email)
        
        try:
            # Validate date format
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            
            # Check if date is not in the future
            if dob > date.today():
                flash("Date of birth cannot be in the future")
                return render_template("addcustomer.html", 
                                      first_name=first_name, 
                                      family_name=family_name, 
                                      date_of_birth=date_of_birth, 
                                      email=email)
            if dob < date.today().replace(year=date.today().year - 110):
                flash("Age cannot be greater than 110 years")
                return render_template("addcustomer.html", 
                                        first_name=first_name, 
                                        family_name=family_name, 
                                        date_of_birth=date_of_birth, 
                                        email=email)
            
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD")
            return render_template("addcustomer.html", 
                                  first_name=first_name, 
                                  family_name=family_name, 
                                  date_of_birth=date_of_birth, 
                                  email=email)
        
        # Check if email is unique
        cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already exists")
            return render_template("addcustomer.html", 
                                  first_name=first_name, 
                                  family_name=family_name, 
                                  date_of_birth=date_of_birth, 
                                  email=email)
        
        # Get the next available customer ID
        cursor.execute("SELECT MAX(customer_id) as max_id FROM customers")
        result = cursor.fetchone()
        next_id = 1 if result['max_id'] is None else result['max_id'] + 1
        
        # Insert new customer
        cursor.execute("""
            INSERT INTO customers (customer_id, first_name, family_name, date_of_birth, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (next_id, first_name, family_name, date_of_birth, email))
        
        flash("Customer added successfully")
        return redirect(url_for('customer_details', customer_id=next_id))


# Task 7 : Edit customer Details
@app.route("/customer/edit/<int:customer_id>", methods=["GET", "POST"])
def editcustomer(customer_id):
    cursor = getCursor()
    
    if request.method == "GET":
        # Get customer details
        cursor.execute("""
            SELECT customer_id, first_name, family_name, date_of_birth, email
            FROM customers
            WHERE customer_id = %s
        """, (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            flash("Customer not found")
            return redirect(url_for('customers'))
        
        return render_template("editcustomer.html", customer=customer)
    
    elif request.method == "POST":
        # Get form data
        first_name = request.form.get('first_name')
        family_name = request.form.get('family_name')
        date_of_birth = request.form.get('date_of_birth')
        email = request.form.get('email')
        
        # Validate form data
        if not first_name or not family_name or not date_of_birth or not email:
            flash("All fields are required")
            return redirect(url_for('editcustomer', customer_id=customer_id))
        
        try:
            # Validate date format
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            
            # Check if date is not in the future
            if dob > date.today():
                flash("Date of birth cannot be in the future")
                return redirect(url_for('editcustomer', customer_id=customer_id))
            
            if dob < date.today().replace(year=date.today().year - 110):
                flash("Age cannot be greater than 110 years")
                return redirect(url_for('editcustomer', customer_id=customer_id))
            
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD")
            return redirect(url_for('editcustomer', customer_id=customer_id))
        
        # Check if email is unique (excluding current customer)
        cursor.execute("""
            SELECT customer_id FROM customers 
            WHERE email = %s AND customer_id != %s
        """, (email, customer_id))
        if cursor.fetchone():
            flash("Email already in use by another customer")
            return redirect(url_for('editcustomer', customer_id=customer_id))
        
        # Update customer
        cursor.execute("""
            UPDATE customers
            SET first_name = %s, family_name = %s, date_of_birth = %s, email = %s
            WHERE customer_id = %s
        """, (first_name, family_name, date_of_birth, email, customer_id))
        
        flash("Customer updated successfully")
        return redirect(url_for('customer_details', customer_id=customer_id))



# For locally running , just for development placed debug to true
if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    
