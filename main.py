# Import Tkinter (for GUI) and 're' (regular expressions for validation)
import tkinter as tk
import re

# Import init_db() from your database file to create/connect the DB
from DataBase import init_db

# Run init_db() → Step 2: Database Setup (creates 'flights.db' and table if missing)
init_db()


# ----------------------------- APPLICATION (Main Window) -----------------------------
class ReservationApp(tk.Tk):
    """
    Main application class.  Inherits from tk.Tk and contains all the pages.
    This is Step 1 – Creates the base window and loads the different pages.
    """
    def __init__(self):
        super().__init__()

        # Basic window config
        self.title("Flight Reservation System")
        self.geometry("700x520")
        self.resizable(False, False)

        # 'container' is a big frame that will hold all pages (Home, Booking, List, Edit)
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Create one instance of each page class and store in self.frames
        self.frames = {}
        for PageClass in (HomePage, BookingPage, ReservationListPage, EditReservationPage):
            page = PageClass(container, self)   # parent = container, controller = main app
            self.frames[PageClass] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Show the home page first
        self.show_frame(HomePage)

    def show_frame(self, page_class):
        """
        Displays the selected page.
        Also clears success/error messages if the page is EditReservationPage (so it opens clean).
        """
        frame = self.frames[page_class]

        # ----- reset messages when opening Edit page -----
        if page_class == EditReservationPage:
            frame.status_label.config(text="")
            frame.name_error.config(text="")
            frame.date_error.config(text="")

        # Bring this frame to the top
        frame.tkraise()


# ----------------------------- HOME PAGE -----------------------------
class HomePage(tk.Frame):
    """
    Page shown at the beginning. Lets the user navigate to:
    - BookingPage (to create a reservation)
    - ReservationListPage (to view all reservations)
    """
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Page Title
        tk.Label(self, text="Home Page", font=("Arial", 20, "bold")).pack(pady=30)

        # Button to go to Booking Page
        tk.Button(
            self, text="Book Flight",
            command=lambda: controller.show_frame(BookingPage),
            width=20
        ).pack(pady=10)

        # Button to go to Reservation List Page AND load reservations
        tk.Button(
            self, text="View Reservations",
            command=lambda: [controller.show_frame(ReservationListPage),
                             controller.frames[ReservationListPage].load_reservations()],
            width=20
        ).pack(pady=10)


# ----------------------------- BOOKING PAGE (Create) -----------------------------
class BookingPage(tk.Frame):
    """
    Page for creating a new reservation.
    Step 3.1 (C = Create): user enters flight info and clicks 'Save'.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Booking Page", font=("Arial", 20, "bold")).pack(pady=20)

        # Entry fields for each reservation detail
        self.name_entry = tk.Entry(self, width=40)
        self.date_entry = tk.Entry(self, width=40)
        self.flight_entry = tk.Entry(self, width=40)
        self.departure_entry = tk.Entry(self, width=40)
        self.destination_entry = tk.Entry(self, width=40)
        self.seat_entry = tk.Entry(self, width=40)

        # Error labels (will show validation problems under the fields)
        self.name_error = tk.Label(self, text="", fg="red")
        self.date_error = tk.Label(self, text="", fg="red")

        # Labels + input boxes
        tk.Label(self, text="Name").pack()
        self.name_entry.pack()
        self.name_error.pack()

        tk.Label(self, text="Date (MM/DD/YYYY)").pack()
        self.date_entry.pack()
        self.date_error.pack()

        for label_text, entry in [
            ("Flight Number", self.flight_entry),
            ("Departure", self.departure_entry),
            ("Destination", self.destination_entry),
            ("Seat Number", self.seat_entry)
        ]:
            tk.Label(self, text=label_text).pack()
            entry.pack()

        # Success message (appears in green after saving)
        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack(pady=5)

        # Save and Back buttons
        tk.Button(self, text="Save Reservation", command=self.save_reservation, width=20).pack(pady=10)
        tk.Button(self, text="Back to Home",
                  command=lambda: controller.show_frame(HomePage),
                  width=20).pack()

        # Bind validation so it runs when field loses focus
        self.name_entry.bind("<FocusOut>", self.validate_name)
        self.date_entry.bind("<FocusOut>", self.validate_date)

    # -- Validation methods --
    def validate_name(self, e=None):
        """
        Allow only letters + spaces in the Name field.
        If invalid => show red error. If valid => clear error.
        """
        value = self.name_entry.get()
        if value and not re.fullmatch(r"[A-Za-z\s]+", value):
            self.name_error.config(text="❌ Name must contain letters and spaces only")
        else:
            self.name_error.config(text="")

    def validate_date(self, e=None):
        """
        Validate date format MM/DD/YYYY.
        Shows a red error message when the format is wrong.
        """
        value = self.date_entry.get()
        if value and not re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
            self.date_error.config(text="❌ Date must be in MM/DD/YYYY format (ex: 08/25/2025)")
        else:
            self.date_error.config(text="")

    # -- Save reservation (CREATE) --
    def save_reservation(self):
        """
        Insert a new reservation into the database after validation.
        """
        import sqlite3

        # Re-check validation
        self.validate_name()
        self.validate_date()
        if self.name_error.cget("text") or self.date_error.cget("text"):
            return  # Stop if invalid

        # Collect values from fields
        values = (
            self.name_entry.get(), self.flight_entry.get(),
            self.departure_entry.get(), self.destination_entry.get(),
            self.date_entry.get(), self.seat_entry.get()
        )

        # Insert into database table
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO reservations
                          (name, flight_number, departure, destination, date, seat_number)
                          VALUES (?, ?, ?, ?, ?, ?)""", values)
        conn.commit()
        conn.close()

        # Show success message + clear boxes
        self.status_label.config(text="✅ Reservation saved!")
        for entry in (self.name_entry, self.flight_entry, self.departure_entry,
                      self.destination_entry, self.date_entry, self.seat_entry):
            entry.delete(0, tk.END)


# --------------------------  RESERVATION LIST PAGE (Read + Delete) --------------------------
class ReservationListPage(tk.Frame):
    """
    Displays all saved reservations in a listbox.
    Also provides a field to delete a reservation by ID.
    Step 3.2 – Read + Delete.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Reservation List Page",
                 font=("Arial", 20, "bold")).pack(pady=20)

        # Listbox widget used to show all records
        self.listbox = tk.Listbox(self, width=95)
        self.listbox.pack(pady=10)

        # Navigation buttons
        tk.Button(self, text="Back to Home",
                  command=lambda: controller.show_frame(HomePage), width=20).pack(pady=5)
        tk.Button(self, text="Edit Reservation",
                  command=lambda: controller.show_frame(EditReservationPage), width=20).pack(pady=5)

        # Delete field (ID) + delete button
        tk.Label(self, text="ID to delete").pack()
        self.delete_id_entry = tk.Entry(self, width=20)
        self.delete_id_entry.pack()
        tk.Button(self, text="Delete Reservation",
                  command=self.delete_reservation, width=20).pack(pady=5)

        self.load_reservations()

    def load_reservations(self):
        """
        Read all rows from the reservations table and display them in the listbox.
        """
        import sqlite3
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations")
        rows = cursor.fetchall()
        self.listbox.delete(0, tk.END)
        for row in rows:
            display_text = f"ID:{row[0]} | Name:{row[1]} | Flight:{row[2]} | From:{row[3]} | To:{row[4]} | Date:{row[5]} | Seat:{row[6]}"
            self.listbox.insert(tk.END, display_text)
        conn.close()

    def delete_reservation(self):
        """
        Delete a record by its ID and refresh the list afterwards.
        Also clears the delete ID entry box so it's ready for the next input.
        """
        import sqlite3
        reservation_id = self.delete_id_entry.get()
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservations WHERE id=?", (reservation_id,))
        conn.commit()
        conn.close()
        self.load_reservations()
        self.delete_id_entry.delete(0, tk.END)   # Clear after deleting


# ----------------------------- EDIT PAGE (Update) -----------------------------
class EditReservationPage(tk.Frame):
    """
    Step 3.3 – Update
    Allows the user to edit an existing reservation.
    The user types an ID → current values are loaded into the form.
    User then changes the field(s) and clicks Save.
    Only the changed fields are updated.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Edit Reservation Page", font=("Arial", 20, "bold")).pack(pady=20)

        # ID (which record the user wants to edit)
        tk.Label(self, text="Reservation ID").pack()
        self.id_entry = tk.Entry(self, width=20)
        self.id_entry.pack()

        # Entry boxes for the editable fields
        self.name_entry = tk.Entry(self, width=40)
        self.date_entry = tk.Entry(self, width=40)
        self.flight_entry = tk.Entry(self, width=40)
        self.departure_entry = tk.Entry(self, width=40)
        self.destination_entry = tk.Entry(self, width=40)
        self.seat_entry = tk.Entry(self, width=40)

        self.name_error = tk.Label(self, text="", fg="red")
        self.date_error = tk.Label(self, text="", fg="red")
        self.status_label = tk.Label(self, text="", fg="green")

        # Labels and field packing
        for label_text, entry in [
            ("Name", self.name_entry),
            ("Date (MM/DD/YYYY)", self.date_entry),
            ("Flight Number", self.flight_entry),
            ("Departure", self.departure_entry),
            ("Destination", self.destination_entry),
            ("Seat Number", self.seat_entry)
        ]:
            tk.Label(self, text=label_text).pack()
            entry.pack()
            if label_text.startswith("Name"):
                self.name_error.pack()
            if label_text.startswith("Date"):
                self.date_error.pack()

        # Buttons: Save and Back
        tk.Button(self, text="Save Changes",
                  command=self.update_reservation, width=20).pack(pady=8)
        tk.Button(self, text="Back to Reservations",
                  command=lambda: controller.show_frame(ReservationListPage),
                  width=20).pack()

        self.status_label.pack(pady=4)

        # Bind actions
        # (When user types an ID and leaves the field, load the record's values)
        self.id_entry.bind("<FocusOut>", self.load_reservation)
        # Validation binds for the two fields
        self.name_entry.bind("<FocusOut>", self.validate_name)
        self.date_entry.bind("<FocusOut>", self.validate_date)

    # Validation same logic as BookingPage
    def validate_name(self, e=None):
        value = self.name_entry.get()
        if value and not re.fullmatch(r"[A-Za-z\s]+", value):
            self.name_error.config(text="❌ Name must contain letters and spaces only")
        else:
            self.name_error.config(text="")

    def validate_date(self, e=None):
        value = self.date_entry.get()
        if value and not re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
            self.date_error.config(text="❌ Date must be in MM/DD/YYYY format (ex: 08/25/2025)")
        else:
            self.date_error.config(text="")

    def load_reservation(self, e=None):
        """
        Automatically loads the values of the reservation with given ID.
        This runs when the user finishes typing the ID and clicks outside the box.
        """
        import sqlite3
        # Clear any old messages
        self.status_label.config(text="")

        reservation_id = self.id_entry.get().strip()
        if not reservation_id:
            return  # empty → do nothing

        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id=?", (reservation_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # Fill all fields with current values
            self.name_entry.delete(0, tk.END);        self.name_entry.insert(0, row[1])
            self.date_entry.delete(0, tk.END);        self.date_entry.insert(0, row[5])
            self.flight_entry.delete(0, tk.END);      self.flight_entry.insert(0, row[2])
            self.departure_entry.delete(0, tk.END);   self.departure_entry.insert(0, row[3])
            self.destination_entry.delete(0, tk.END); self.destination_entry.insert(0, row[4])
            self.seat_entry.delete(0, tk.END);        self.seat_entry.insert(0, row[6])

    def update_reservation(self):
        """
        Updates the reservation.  Only fields that the user changed will be updated,
        and others stay the same.
        """
        import sqlite3

        # Clear confirmation
        self.status_label.config(text="")

        # Validate Name / Date
        self.validate_name()
        self.validate_date()
        # Stop if validation error is displayed
        if self.name_error.cget("text") or self.date_error.cget("text"):
            return

        # Check if ID exists
        reservation_id = self.id_entry.get()
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id=?", (reservation_id,))
        row = cursor.fetchone()

        if not row:
            self.status_label.config(text="❌ ID not found", fg="red")
            return

        # Choose new value if user changed it, otherwise keep the original database value
        updated_values = {
            'name':   self.name_entry.get()   if self.name_entry.get()   else row[1],
            'date':   self.date_entry.get()   if self.date_entry.get()   else row[5],
            'flight': self.flight_entry.get() if self.flight_entry.get() else row[2],
            'dep':    self.departure_entry.get() if self.departure_entry.get() else row[3],
            'dest':   self.destination_entry.get() if self.destination_entry.get() else row[4],
            'seat':   self.seat_entry.get() if self.seat_entry.get() else row[6],
        }

        # UPDATE query
        cursor.execute("""
            UPDATE reservations SET
                name = ?,
                flight_number = ?,
                departure = ?,
                destination = ?,
                date = ?,
                seat_number = ?
            WHERE id = ?
        """, (updated_values['name'], updated_values['flight'], updated_values['dep'],
              updated_values['dest'], updated_values['date'], updated_values['seat'], reservation_id))
        conn.commit()
        conn.close()

        # Confirmation + refresh list
        self.status_label.config(text="✅ Changes saved!", fg="green")
        self.controller.frames[ReservationListPage].load_reservations()

        # Clear fields
        for entry in (self.id_entry, self.name_entry, self.date_entry, self.flight_entry,
                      self.departure_entry, self.destination_entry, self.seat_entry):
            entry.delete(0, tk.END)


# -------------------------- RUN APPLICATION --------------------------
if __name__ == "__main__":
    # Launch the application (keeps running until window is closed)
    app = ReservationApp()
    app.mainloop()


