# SmartPark – Smart Vehicle Parking App

**SmartPark** is a multi-user web application designed to streamline 4-wheeler parking management. It allows users and administrators to interact through dedicated dashboards to manage parking lots, monitor spot availability, and handle reservations efficiently. The platform is built with Flask, Jinja2, SQLite, and Bootstrap, and runs entirely on a local machine with a programmatically initialized database.

---

##  Features by User Role

###  Admin (Superuser)
> *No registration required – admin account is auto-generated when the database is created.*

- Create, edit, and delete parking lots (deletion allowed only if all spots are free).
- Automatically generates parking spots based on the defined capacity.
- Monitor parking lots with real-time spot status.
- View current parking activity across all lots.
- Access a list of all registered users.
- Interactive admin dashboard with charts showing:
  - Overall lot occupancy
  - Parking usage trends

---

### Users
> *Users must register and log in to access features.*

- Browse and book available spots in any parking lot.
- Smart automatic allocation of spots upon booking.
- Release reserved spot once the vehicle departs.
- Track timestamps for each parking session.
- Automatic charge calculation based on duration.
- View personal parking history with visual summaries and statistics.

---

##  Core Technologies

| Layer       | Stack                          |
|-------------|--------------------------------|
| **Backend** | Python, Flask                  |
| **Frontend**| HTML, CSS, Bootstrap, Jinja2   |
| **Database**| SQLite                         |

---

##  Project Highlights

-  **Smart Allocation**: Parking spots are allocated intelligently based on real-time availability.
-  **Dashboard Charts**: Visual insights into parking usage for both admin and users.
-  -  **Secure Login**: Session-based authentication for registered users.
-  **Local Deployment**: No need for external setup — runs locally with SQLite.
