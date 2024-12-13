# reservation_system.py
from collections import deque
import uuid

class ReservationSystem:
    def __init__(self):
        # Queue to manage booking order
        self.booking_queue = deque()
        
        # Hash table (dictionary) to store user information
        self.user_bookings = {}
    
    def enqueue_booking(self, booking_details):
        """
        Add a new booking to the queue and store user details
        
        Args:
            booking_details (dict): Contains user booking information
        
        Returns:
            str: Unique booking ID
        """
        # Generate a unique booking ID
        booking_id = str(uuid.uuid4())[:8]
        
        # Add booking to queue
        self.booking_queue.append(booking_id)
        
        # Store user details with booking ID
        booking_details['booking_id'] = booking_id
        self.user_bookings[booking_id] = booking_details
        
        return booking_id
    
    def dequeue_booking(self):
        """
        Remove and return the next booking in queue
        
        Returns:
            dict: Details of the next booking, or None if queue is empty
        """
        if not self.booking_queue:
            return None
        
        # Get and remove the first booking ID from queue
        booking_id = self.booking_queue.popleft()
        
        # Retrieve and return booking details
        return self.user_bookings.pop(booking_id, None)
    
    def peek_next_booking(self):
        """
        View the next booking without removing it
        
        Returns:
            dict: Details of the next booking, or None if queue is empty
        """
        if not self.booking_queue:
            return None
        
        # Get the first booking ID without removing
        next_booking_id = self.booking_queue[0]
        return self.user_bookings.get(next_booking_id)
    
    def get_all_bookings(self):
        """
        Get all current bookings
        
        Returns:
            list: List of all current bookings
        """
        return list(self.user_bookings.values())
    
    def cancel_booking(self, booking_id):
        """
        Cancel a specific booking
        
        Args:
            booking_id (str): Unique ID of the booking to cancel
        
        Returns:
            bool: True if booking was cancelled, False otherwise
        """
        if booking_id in self.user_bookings:
            # Remove from queue
            self.booking_queue.remove(booking_id)
            
            # Remove from user bookings
            del self.user_bookings[booking_id]
            
            return True
        return False