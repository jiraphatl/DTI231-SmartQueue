# reservation_system.py
from collections import deque
from typing import Dict, List, Optional
import uuid

class ReservationSystem:
    def __init__(self):
        # Queue to manage booking order (FIFO)
        self.booking_queue = deque()
        
        # Hash table to store user reservations
        self.user_reservations = {}
        
        # Hash table to store reservation details
        self.reservation_details = {}

    def add_reservation(self, user_info: Dict[str, str]) -> str:
        """
        Add a new reservation to the system
        
        :param user_info: Dictionary containing user reservation details
        :return: Reservation ID
        """
        # Generate unique reservation ID
        reservation_id = str(uuid.uuid4())
        
        # Add reservation to queue
        self.booking_queue.append(reservation_id)
        
        # Store user information and reservation details
        self.user_reservations[reservation_id] = user_info
        self.reservation_details[reservation_id] = {
            'status': 'Pending',
            'timestamp': len(self.booking_queue)
        }
        
        return reservation_id

    def get_next_reservation(self) -> Optional[Dict[str, str]]:
        """
        Process next reservation in the queue
        
        :return: Next reservation details or None if queue is empty
        """
        if not self.booking_queue:
            return None
        
        # Get next reservation ID
        reservation_id = self.booking_queue.popleft()
        
        # Retrieve user information
        user_info = self.user_reservations.get(reservation_id)
        
        # Update reservation status
        if reservation_id in self.reservation_details:
            self.reservation_details[reservation_id]['status'] = 'Processed'
        
        return {
            'reservation_id': reservation_id,
            **user_info
        }

    def cancel_reservation(self, reservation_id: str) -> bool:
        """
        Cancel a specific reservation
        
        :param reservation_id: ID of the reservation to cancel
        :return: True if successfully cancelled, False otherwise
        """
        if reservation_id not in self.user_reservations:
            return False
        
        # Remove from user reservations
        del self.user_reservations[reservation_id]
        
        # Remove from reservation details
        del self.reservation_details[reservation_id]
        
        return True

    def get_reservation_status(self, reservation_id: str) -> Optional[Dict[str, str]]:
        """
        Get status of a specific reservation
        
        :param reservation_id: ID of the reservation
        :return: Reservation status details or None if not found
        """
        if reservation_id not in self.reservation_details:
            return None
        
        return {
            'user_info': self.user_reservations.get(reservation_id, {}),
            'status': self.reservation_details[reservation_id]['status'],
            'queue_position': list(self.booking_queue).index(reservation_id) + 1 if reservation_id in self.booking_queue else 'Processed'
        }

    def get_current_queue(self) -> List[str]:
        """
        Get current booking queue
        
        :return: List of reservation IDs in queue
        """
        return list(self.booking_queue)