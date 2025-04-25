**DCMS**

The Dental Clinic Management System (DCMS) is a web application built for Dr. Kareen’s dental clinic to replace manual Excel-based processes. 


-------------------------------------------------------------

**Features**

- User Management: Add, view, edit, and delete user accounts (Doctors, Staff), with restrictions preventing deletion of other Superusers.

- Patient Management: Add, view, update, and search patient records, including medical history and detailed tooth records.

- Appointment Management: Schedule, view, edit, and delete appointments, linked to patients and doctors, with treatment records and payment details. Includes calendar views (daily, weekly, monthly) and payment status filters.

- Transaction Management: Record, view, edit, and delete transactions, with categorization and filters by category or date.

- Reports and Statistics: View a dashboard with today’s appointments and follow-up reminders, generate PDF patient reports, and access  statistics with filters.

- User Interface: Features a collapsible sidebar, searchable tables, and Tailwind CSS styling for a clean, user-friendly experience.

---------------------------------------------

**Technologies**

- Backend: Django (Python) for server logic and data management.

- Frontend: HTML, Tailwind CSS, and JavaScript for responsive, simple interfaces.

- Database: PostgreSQL for storing user, patient, appointment, and transaction data.

------------------------------------------------

**Installation**
1. Clone the Repository:

        git clone https://github.com/Rakshita-Baidya/DCMS.git
        cd dcms

2. Set Up a Virtual Environment:
   
       python -m venv venv
       venv\Scripts\activate

3. Install Dependencies:

        pip install -r requirements.txt

4. Configure the Database:

    - Install PostgreSQL and create a database named dcms, update .env.

5. Run Migrations:

        python manage.py makemigrations
        python manage.py migrate

6. Create a Superuser:

        python manage.py createsuperuser
  
7. Run the system:
    
        python manage.py runserver


--------------------------------------------------------------------------

**Contact**

For issues or suggestions, contact the development team via GitHub Issues.
