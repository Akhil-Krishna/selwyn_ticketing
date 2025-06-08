# Selwyn Event Ticketing (SET)

This is a web application I built using Flask, aimed at handling the core operations of the Selwyn Event Ticketing platform. It manages customer records, event data, and ticket purchases — all integrated with a MySQL database.

---

## Design Choices

### 1. How I Handled Database Connections

Instead of reusing one connection across the app (which can cause problems), I made a function that sets up a fresh connection and cursor every time a query is needed. It seemed cleaner and helps avoid timeout issues — especially when hosted online.

### 2. Getting Dates to Look Right

I wrote a simple function to show dates in DD/MM/YYYY format — the usual NZ style. This way, all pages show consistent date formatting, and if we ever need to switch formats, we can just tweak one place.

### 3. Handling Forms: GET vs POST

I used GET requests for showing forms and POST for when data is submitted. It’s a clear pattern and helped me keep the logic tidy. You’ll see this in most of the form-based features like adding or editing customers, or buying tickets.

### 4. How Customer IDs Are Assigned

Since the original setup didn’t use auto-increment for customer IDs, I wrote logic to find the highest ID and add one when a new customer is created. This fits with the existing data model and avoids messing with the table schema.

### 5. Age Checks Based on Event Date

When a customer tries to buy a ticket, I check how old they'll be on the date of the event — not just how old they are now. That felt fairer, since someone might qualify by the time the event actually happens.

### 6. Avoiding Duplicate Ticket Records

If a customer already bought tickets for an event, the app just updates the quantity instead of creating another row. That keeps things tidy in the database.

### 7. Search Logic for Customers

I used flexible search logic so users can search by first name, last name, or both. It uses SQL `LIKE` to support partial matches — which is nice when you only remember part of someone’s name.

### 8. Keeping the Look Consistent

All the pages extend a single `base.html` file. It has the site header and nav bar, so everything looks consistent and I don’t have to repeat code.

### 9. Showing Feedback with Flash

Whenever a form succeeds or fails, the user sees a flash message — whether it’s “Customer added” or “Please fill out all fields.” It’s a quick way to improve usability without needing complex UI work.

### 10. Showing Only Upcoming Events

On the “Future Events” page, I used the server date to filter out past events. Only events in the future with available tickets are shown. That keeps things relevant.

### 11. Sorting Data Clearly

Customers are sorted by last name and then first name, and the customer list for each event shows youngest people first (if surnames match). Events are sorted by date. It just makes everything easier to browse.

### 12. Validating User Input

Every form checks that required fields are filled, that emails aren’t duplicated, that ticket counts are valid, and that dates make sense. It’s not fancy, but it stops a lot of bugs before they happen.

---

## Image Attribution

* **Homepage Illustration**:
  “Flat design online ticket illustration”
  by Freepik – [View Source](https://www.freepik.com/free-vector/flat-design-online-ticket-illustration_144642196.htm)

---

## 🗃️ SQL + Database Integration

### 1. How the `events` table is defined:

```sql
CREATE TABLE events (
    event_id INT,
    event_name VARCHAR(100),
    age_restriction INT,
    capacity INT,
    event_date DATE,
    PRIMARY KEY (event_id)
);
```

### 2. How customers and events are linked via ticket purchases:

```sql
CREATE TABLE ticket_sales (
    ticket_sales_id INT NOT NULL AUTO_INCREMENT,
    customer_id INT,
    event_id INT,
    tickets_purchased INT,
    PRIMARY KEY (ticket_sales_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
```

### 3. SQL to create `event_categories`:

```sql
CREATE TABLE event_categories (
    category_id INT NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    PRIMARY KEY (category_id)
);
```

### 4. SQL to insert a new category:

```sql
INSERT INTO event_categories (category_name, description)
VALUES ('Music Festivals', 'Large-scale outdoor music events featuring multiple artists and stages');
```

### 5. If I wanted to link categories to events:

* I’d add a `category_id` column to the `events` table.
* Then set it as a foreign key pointing to `event_categories`.
* I’d update existing records to assign them a category.
* The UI and routes would need updates to show categories and let users filter or assign them.
* Admin tools could be added to manage categories too.

---

## Tech Stack Used

* **Python**: Flask for the backend logic and routes
* **MySQL**: Database engine with `MySQLdb` connector
* **HTML/CSS**: Bootstrap for layout and styling
* **Hosting**: PythonAnywhere
* **Templates**: Jinja2 with template inheritance

---

##  Features at a Glance

* Add, edit, and search for customers
* View customer ticket history
* Buy tickets with age and capacity checks
* Filter and view future events with available seats
* Friendly and consistent interface using Bootstrap
* Secure form submissions with clear error handling
* Fully functional on local and PythonAnywhere

