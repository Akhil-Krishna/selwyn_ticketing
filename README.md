# Selwyn Event Ticketing (SET)

A Flask-based web application for managing event ticketing, customers, and ticket sales for Selwyn Event Ticketing company.

## Design Decisions

### 1. Database Connection Management
I implemented a global connection pattern with the `getCursor()` function to manage database connections efficiently. This approach ensures a single connection is maintained throughout the application's lifecycle while providing fresh cursors for each query. This decision was made to avoid connection overhead while maintaining thread safety for the single-user development environment.

### 2. Date Formatting Strategy
I created a dedicated `format_date_nz()` function to consistently format dates in New Zealand format (DD/MM/YYYY) throughout the application. This centralized approach ensures consistency across all templates and makes it easy to modify date formatting if requirements change. The function handles both string and date object inputs for flexibility.

### 3. Form Handling with GET/POST Pattern
For all forms, I consistently used GET requests to display empty forms and POST requests to process form submissions. This RESTful approach provides clear separation of concerns - GET for data retrieval and display, POST for data modification. This pattern is repeated across add customer, edit customer, buy tickets, and search functionality.

### 4. Customer ID Management
I chose to auto-generate customer IDs by finding the maximum existing ID and incrementing it, rather than relying on database auto-increment. This gives more control over ID assignment and ensures consistency with the existing data structure where customer_id is not set to auto-increment.

### 5. Age Validation Logic
For ticket purchases, I implemented age validation that calculates the customer's age at the event date rather than their current age. This ensures customers who will meet the age requirement by the event date can purchase tickets, providing a better user experience while maintaining event restrictions.

### 6. Ticket Purchase Update vs Insert
I implemented logic to check if a customer already has tickets for an event. If they do, the system updates their existing purchase by adding more tickets rather than creating a duplicate entry. This prevents data duplication and provides a cleaner ticket sales record.

### 7. Search Functionality Implementation
For customer search, I built dynamic SQL queries based on which fields are provided (first name, family name, or both). This flexible approach allows partial matching using LIKE operators and handles empty search fields gracefully, providing a user-friendly search experience.

### 8. Template Structure and Inheritance
I utilized Flask's template inheritance system with a base template for consistent navigation and styling across all pages. Each specific page extends the base template, ensuring consistent branding and navigation while avoiding code duplication.

### 9. Error Handling with Flash Messages
I consistently used Flask's flash messaging system for user feedback throughout the application. This provides immediate feedback for validation errors, successful operations, and system messages without requiring additional page redirects or complex state management.

### 10. Future Events Filtering
For the future events display, I used SQL date comparison with Python's `date.today()` to filter events. This server-side filtering ensures accuracy and reduces data transfer. The query also includes ticket availability calculations to only show events with remaining tickets.

### 11. Sorting and Ordering Strategy
I implemented consistent sorting throughout the application - customers by family name then first name, events by date, and customer lists by family name with youngest first for same family names. This provides predictable and logical ordering for users.

### 12. Form Validation Approach
I implemented comprehensive server-side validation for all forms, including data type validation, date range checking, email uniqueness verification, and required field validation. This ensures data integrity and provides clear error messages to users.

## Image Sources

- **Home page illustration**: "Flat design online ticket illustration" by Freepik
  - Source: https://www.freepik.com/free-vector/flat-design-online-ticket-illustration_144642196.htm
  - Search term: "Ticketing System"
  - Used under Freepik license

## Database Questions

### 1. SQL statement that creates the events table:

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

### 2. SQL lines that set up the relationship between customers and events through ticket purchases:

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

### 3. SQL script to create event_categories table:

```sql
CREATE TABLE event_categories (
    category_id INT NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    PRIMARY KEY (category_id)
);
```

### 4. SQL statement to add a new category:

```sql
INSERT INTO event_categories (category_name, description)
VALUES ('Music Festivals', 'Large-scale outdoor music events featuring multiple artists and stages');
```

### 5. Changes needed to integrate event_categories table:

To fully integrate the event_categories table into the data model, the following changes would be needed:

- **Add foreign key to events table**: Add a `category_id` column to the `events` table as a FOREIGN KEY referencing `event_categories(category_id)`. This would establish the relationship between events and their categories.

- **Update existing events**: Assign appropriate category IDs to all existing events in the database to maintain data consistency.

- **Modify application queries**: Update all queries that retrieve event information to include category details through JOIN operations where category information is needed.

- **Update user interface**: Modify forms and display pages to show category information and allow category selection when creating or editing events.

- **Add category management**: Create additional routes and templates for managing event categories (add, edit, delete categories) for administrative purposes.

## Technologies Used

- **Backend**: Python Flask
- **Database**: MySQL with MySQLdb connector
- **Frontend**: HTML5, Bootstrap CSS
- **Template Engine**: Jinja2
- **Development Environment**: PythonAnywhere hosting

## Key Features

- Customer management (add, edit, search, view details)
- Event listing and management
- Ticket purchasing with age and availability validation
- Future events display with remaining ticket counts
- Customer ticket purchase history
- Professional Bootstrap-styled interface
- Comprehensive form validation and error handling