from collections import deque
from datetime import datetime, timedelta
from typing import List, Optional, Dict

class Queue:
    """Custom Queue implementation for managing reservations."""
    def __init__(self):
        """Initialize an empty queue."""
        self._items = deque()
    
    def enqueue(self, item):
        """
        Add an item to the end of the queue.
        
        :param item: Item to be added to the queue
        """
        self._items.append(item)
    
    def dequeue(self):
        """
        Remove and return the first item from the queue.
        
        :return: First item in the queue
        :raises IndexError: If the queue is empty
        """
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self._items.popleft()
    
    def peek(self):
        """
        View the first item in the queue without removing it.
        
        :return: First item in the queue
        :raises IndexError: If the queue is empty
        """
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self._items[0]
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        :return: True if queue is empty, False otherwise
        """
        return len(self._items) == 0
    
    def size(self) -> int:
        """
        Get the number of items in the queue.
        
        :return: Number of items in the queue
        """
        return len(self._items)

class Customer:
    """Represents a restaurant customer."""
    def __init__(self, name: str, phone: str, email: str):
        """
        Initialize a customer with contact information.
        
        :param name: Customer's full name
        :param phone: Customer's phone number
        :param email: Customer's email address
        """
        self.name = name
        self.phone = phone
        self.email = email

class Table:
    """Represents a restaurant table."""
    def __init__(self, table_id: int, capacity: int):
        """
        Initialize a table with an ID and seating capacity.
        
        :param table_id: Unique identifier for the table
        :param capacity: Maximum number of people the table can seat
        """
        self.table_id = table_id
        self.capacity = capacity
        self.is_available = True

class Reservation:
    """Represents a table reservation."""
    def __init__(self, 
                 customer: Customer, 
                 table: Table, 
                 date: datetime, 
                 party_size: int):
        """
        Create a reservation for a customer.
        
        :param customer: Customer making the reservation
        :param table: Table reserved
        :param date: Date and time of reservation
        :param party_size: Number of people in the party
        """
        self.customer = customer
        self.table = table
        self.date = date
        self.party_size = party_size
        self.reservation_id = self._generate_reservation_id()

    def _generate_reservation_id(self) -> str:
        """
        Generate a unique reservation ID.
        
        :return: Unique reservation identifier
        """
        return f"RES-{self.customer.name[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

class RestaurantBookingSystem:
    """Manages restaurant table bookings using Queue and other data structures."""
    def __init__(self):
        """
        Initialize the booking system with empty collections.
        """
        # Queue to manage waiting list
        self.waiting_queue = Queue()
        
        # List to store all tables
        self.tables: List[Table] = []
        
        # List to store all active reservations
        self.active_reservations: List[Reservation] = []
        
        # Dictionary to track reservations by date
        self.reservations_by_date: Dict[datetime, List[Reservation]] = {}

    def add_table(self, table_id: int, capacity: int):
        """
        Add a new table to the restaurant.
        
        :param table_id: Unique identifier for the table
        :param capacity: Maximum number of people the table can seat
        """
        table = Table(table_id, capacity)
        self.tables.append(table)

    def find_available_table(self, party_size: int) -> Optional[Table]:
        """
        Find an available table that can accommodate the party.
        
        :param party_size: Number of people in the party
        :return: An available table or None if no suitable table is found
        """
        for table in self.tables:
            # Check if table is available and can accommodate party
            if table.is_available and table.capacity >= party_size:
                table.is_available = False
                return table
        return None

    def make_reservation(self, 
                         customer: Customer, 
                         party_size: int, 
                         reservation_date: datetime) -> Optional[Reservation]:
        """
        Attempt to make a reservation for a customer.
        
        :param customer: Customer making the reservation
        :param party_size: Number of people in the party
        :param reservation_date: Date and time of reservation
        :return: Created reservation or None if no table available
        """
        # Try to find an available table
        available_table = self.find_available_table(party_size)
        
        if available_table:
            # Create and store reservation
            reservation = Reservation(customer, available_table, reservation_date, party_size)
            self.active_reservations.append(reservation)
            
            # Track reservations by date
            if reservation_date not in self.reservations_by_date:
                self.reservations_by_date[reservation_date] = []
            self.reservations_by_date[reservation_date].append(reservation)
            
            return reservation
        else:
            # If no table is available, add to waiting queue
            waiting_reservation = {
                'customer': customer,
                'party_size': party_size,
                'reservation_date': reservation_date
            }
            self.waiting_queue.enqueue(waiting_reservation)
            print(f"No table available. {customer.name} added to waiting queue.")
            return None

    def process_waiting_queue(self):
        """
        Process the waiting queue and try to accommodate waiting customers.
        """
        while not self.waiting_queue.is_empty():
            # Peek at the first waiting reservation
            waiting_reservation = self.waiting_queue.peek()
            
            # Try to find a table for the waiting reservation
            available_table = self.find_available_table(waiting_reservation['party_size'])
            
            if available_table:
                # Remove from waiting queue
                waiting_reservation = self.waiting_queue.dequeue()
                
                # Create reservation for the waiting customer
                reservation = Reservation(
                    waiting_reservation['customer'], 
                    available_table, 
                    waiting_reservation['reservation_date'], 
                    waiting_reservation['party_size']
                )
                
                self.active_reservations.append(reservation)
                print(f"Reservation created for {reservation.customer.name} from waiting queue.")
            else:
                # No tables available, keep waiting
                break

    def cancel_reservation(self, reservation: Reservation):
        """
        Cancel a specific reservation and free up the table.
        
        :param reservation: Reservation to cancel
        """
        # Mark table as available
        reservation.table.is_available = True
        
        # Remove from active reservations
        if reservation in self.active_reservations:
            self.active_reservations.remove(reservation)
        
        # Remove from date-based tracking
        if reservation.date in self.reservations_by_date:
            self.reservations_by_date[reservation.date].remove(reservation)
        
        # Try to process waiting queue
        self.process_waiting_queue()

# Example Usage
def main():
    # Create booking system
    booking_system = RestaurantBookingSystem()

    # Add tables to the restaurant
    booking_system.add_table(1, 2)  # Table 1: 2 seats
    booking_system.add_table(2, 4)  # Table 2: 4 seats
    booking_system.add_table(3, 6)  # Table 3: 6 seats

    # Create customers
    john = Customer("John Doe", "123-456-7890", "john@example.com")
    jane = Customer("Jane Smith", "987-654-3210", "jane@example.com")
    mike = Customer("Mike Johnson", "456-789-0123", "mike@example.com")

    # Demonstrate reservation and waiting queue
    reservation_time = datetime.now() + timedelta(days=7)
    
    # Make multiple reservations
    booking_system.make_reservation(john, 2, reservation_time)
    booking_system.make_reservation(jane, 4, reservation_time)
    booking_system.make_reservation(mike, 6, reservation_time)

    # Process waiting queue
    booking_system.process_waiting_queue()

if __name__ == "__main__":
    main()