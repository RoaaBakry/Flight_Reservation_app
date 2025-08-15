from DataBase import init_db
init_db() # to connect to the database 
import tkinter as tk
class ReservationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # window setup 
        self.title("Flight Reservation System")
        self.geometry("400x500")
        self.resizable(False, False)

        #creating a frame to take all diff pages
        container = tk.Frame(self)
        container.pack(fill="both", expand= True)

        # creating a dictionary to hold all frames
        self.frame={}
        
        # create a loop to create each page
        for PageClass in (HomePage, BookingPage, ReservationListPage, EditReservationPage):
            page= PageClass(container,self) 
            self.frame[PageClass]= page
            page.grid(row=0, column=0, sticky="nsew")
            # show the home page first
        self.show_frame(HomePage)
    def show_frame(self, page_class):
         frame = self.frame[page_class]
        
         frame.tkraise()  # Display the page
       
        
        

# Home Page
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Home Page", font=("Arial", 18)).pack(pady=20)

        # Navigation Buttons
        tk.Button(self, text="Book Flight",
                  command=lambda: controller.show_frame(BookingPage)).pack(pady=5)

        tk.Button(self, text="View Reservations",
                  command=lambda: controller.show_frame(ReservationListPage)).pack(pady=5)

                             
# Booking Page
class BookingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Booking Page", font=("Arial", 18)).pack(pady=20)

        #  create textbox start and varibles
        self.name_entry = tk.Entry(self)
        self.flight_entry = tk.Entry(self)
        self.departure_entry = tk.Entry(self)
        self.destination_entry = tk.Entry(self)
        self.date_entry = tk.Entry(self)
        self.seat_entry = tk.Entry(self)

        tk.Label(self, text="Name").pack() #create label of each box
        self.name_entry.pack() #show the box

        tk.Label(self, text="Flight Number").pack()
        self.flight_entry.pack()

        tk.Label(self, text="Departure").pack()
        self.departure_entry.pack()

        tk.Label(self, text="Destination").pack()
        self.destination_entry.pack()

        tk.Label(self, text="Date").pack()
        self.date_entry.pack()

        tk.Label(self, text="Seat Number").pack()
        self.seat_entry.pack()

        #Buttons
        tk.Button(self, text="Save Reservation",
                  command=self.save_reservation).pack(pady=10)

        tk.Button(self, text="Back to Home",
                  command=lambda: controller.show_frame(HomePage)).pack()

    def save_reservation(self): # to send data to database
        import sqlite3

        # get data from entry fields
        name = self.name_entry.get()
        flight = self.flight_entry.get()
        departure = self.departure_entry.get()
        destination = self.destination_entry.get()
        date = self.date_entry.get()
        seat = self.seat_entry.get()

        # Connect to DB and insert the data
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reservations (name, flight_number, departure, destination, date, seat_number) VALUES (?, ?, ?, ?, ?, ?)",
            (name, flight, departure, destination, date, seat)
        )
        conn.commit()
        conn.close()


# Reservation List Page
class ReservationListPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Reservation List Page", font=("Arial", 18)).pack(pady=20)

        # Listbox to display reservations
        self.listbox = tk.Listbox(self, width=60)
        self.listbox.pack(pady=10)

        # Back Button
        tk.Button(self, text="Back to Home",
                  command=lambda: controller.show_frame(HomePage)).pack()

        # Edit Button Example (navigates to Edit Page)
        tk.Button(self, text="Edit Reservation",
                  command=lambda: controller.show_frame(EditReservationPage)).pack(pady=5)

        # Load data when the page is created
        self.load_reservations()

    def load_reservations(self):
        import sqlite3

        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations")
        rows = cursor.fetchall()

        self.listbox.delete(0, tk.END)  # clear old data

        for row in rows:
            display_text = f"ID:{row[0]} | Name:{row[1]} | Flight:{row[2]} | From:{row[3]} | To:{row[4]} | Date:{row[5]} | Seat:{row[6]}"
            self.listbox.insert(tk.END, display_text)

        conn.close()
        

# Edit Reservation Page
class EditReservationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Reservation List Page", font=("Arial", 18)).pack(pady=20)

        # Listbox to display reservations
        self.listbox = tk.Listbox(self, width=60)
        self.listbox.pack(pady=10)

        # Back Button
        tk.Button(self, text="Back to Home",
                  command=lambda: controller.show_frame(HomePage)).pack()

        # Edit Button (go to Edit page manually)
        tk.Button(self, text="Edit Reservation",
                  command=lambda: controller.show_frame(EditReservationPage)).pack(pady=5)

        # ----- Delete Section -----
        tk.Label(self, text="ID to delete").pack()
        self.delete_id_entry = tk.Entry(self)
        self.delete_id_entry.pack()

        tk.Button(self, text="Delete Reservation",
                  command=self.delete_reservation).pack(pady=5)

        # Load the data immediately when the page is created
        self.load_reservations()

    def load_reservations(self):
        import sqlite3

        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations")
        rows = cursor.fetchall()

        self.listbox.delete(0, tk.END)  # clear old data

        for row in rows:
            display_text = f"ID:{row[0]} | Name:{row[1]} | Flight:{row[2]} | From:{row[3]} | To:{row[4]} | Date:{row[5]} | Seat:{row[6]}"
            self.listbox.insert(tk.END, display_text)

        conn.close()

    def delete_reservation(self):
        import sqlite3

        reservation_id = self.delete_id_entry.get()

        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservations WHERE id=?", (reservation_id,))
        conn.commit()
        conn.close()

        # refresh listbox so the deleted item disappears
        self.load_reservations()
# Run the App
if __name__== "__main__":
    app = ReservationApp()
    app.mainloop()

