import hashlib
import re
import sqlite3

class TicketOffice:
    def __init__(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

    def display_movies(self):
        self.cursor.execute("SELECT * FROM movie")
        movies = self.cursor.fetchall()
        print("Available movies:")
        for movie in movies:
            print(f"{movie[0]}. {movie[1]} ({movie[2]})")

    def display_showtimes(self, movie_id):
        self.cursor.execute("SELECT * FROM afisha WHERE movie_id = ?", (movie_id,))
        showtimes = self.cursor.fetchall()
        print("Available showtimes:")
        for showtime in showtimes:
            print(f"{showtime[0]}. {showtime[4]} {showtime[5]}")

    def select_seats(self, afisha_id):
        self.cursor.execute("SELECT * FROM place WHERE afisha_id = ?", (afisha_id,))
        seats = self.cursor.fetchall()
        print("Available seats:")
        for i, seat in enumerate(seats, 1):
            print(f"{i}. Row {seat[2]}, Seat {seat[3]}")
            selected_seat = input("Select seat: ")
            if selected_seat.isdigit() and 1 <= int(selected_seat) <= len(seats):
                return seats[int(selected_seat) - 1][0]
            print("Invalid input. Try again.")

    def validate_payment_info(self, payment_info):
        try:
            if not re.match("^[a-zA-Z ]+$", payment_info['name']):
                raise ValueError("Invalid name format.")
            if not re.match("^\d{4} \d{4} \d{4} \d{4}$", payment_info['card_number']):
                raise ValueError("Invalid card number format.")
            if not re.match("^\d{2}/\d{2}$", payment_info['expiry_date']):
                raise ValueError("Invalid expiry date format.")
            return True
        except ValueError:
            return False

    def book_ticket(self, showtime_id, seat_id):
        self.cursor.execute("INSERT INTO ticket(name, phone, place_id) VALUES(?, ?, ?)", ("", "", seat_id))
        self.connection.commit()

    def process_payment(self, ticket_id, payment_info):
        if self.validate_payment_info(payment_info):
            self.cursor.execute("UPDATE ticket SET name = ?, phone = ? WHERE id = ?", (payment_info['name'], payment_info['card_number'], ticket_id))
            self.connection.commit()
            print("Payment processed successfully.")
        else:
            print("Invalid payment information. Please enter valid payment details.")

    def cancel_booking(self, ticket_id):
        self.cursor.execute("DELETE FROM ticket WHERE id = ?", (ticket_id,))
        self.connection.commit()
        print("Booking canceled successfully.")

    def signup(self):
        email = input("Enter email address: ")
        pwd = input("Enter password: ")
        conf_pwd = input("Confirm password: ")
        if conf_pwd == pwd:
            enc = pwd.encode()
            hash1 = hashlib.md5(enc).hexdigest()
            with open("credentials.txt", "a") as f:
                f.write(email + "\n")
                f.write(hash1 + "\n")
            print("You have registered successfully!")
            return True
        else:
            print("Password is not the same as above!")
            return False

    def login(self):
        email = input("Enter email: ")
        pwd = input("Enter password: ")
        auth = pwd.encode()
        auth_hash = hashlib.md5(auth).hexdigest()
        with open("credentials.txt", "r") as f:
            lines = f.readlines()
            stored_credentials = [line.strip() for line in lines]
        for i in range(0, len(stored_credentials), 2):
            stored_email = stored_credentials[i]
            stored_pwd = stored_credentials[i + 1]
            if email == stored_email and auth_hash == stored_pwd:
                print("Logged in Successfully!")
                return True
        print("Login failed!")
        return False

if __name__ == '__main__':
    ticket_office = TicketOffice()
    logged_in = False
    while not logged_in:
        print("** Login System **")
        print("1. Signup")
        print("2.Login")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            logged_in = ticket_office.signup()
        elif choice == '2':
            logged_in = ticket_office.login()

    ticket_office.display_movies()
    movie_id = int(input("Select movie by number: "))
    ticket_office.display_showtimes(movie_id)
    showtime_id = int(input("Select showtime by number: "))
    ticket_office.select_seats(showtime_id)
