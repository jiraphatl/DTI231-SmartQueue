from collections import deque
import uuid

class ReservationSystem:
    def __init__(self):
        self.booking_queue = deque()
        self.user_bookings = {}
    
    # เพิ่มคิว
    def enqueue_booking(self, booking_details):
        # Generate a booking ID
        booking_id = str(uuid.uuid4())[:8]
        self.booking_queue.append(booking_id)
        booking_details['booking_id'] = booking_id
        self.user_bookings[booking_id] = booking_details
        return booking_id
    
    def dequeue_booking(self):
        if self.booking_queue:
            booking_id = self.booking_queue.popleft()
            return self.user_bookings.pop(booking_id, None) 
        return None

    # ดูคิว
    def peek_next_booking(self):
        if self.booking_queue:
            next_id = self.booking_queue[0]
            return self.user_bookings[next_id]
        return None
    
    # ดูคิวทั้งหมด
    def get_all_bookings(self):
        return [self.user_bookings[booking_id] for booking_id in self.booking_queue]
    
    # แอดมินยกเลิกคิว
    def cancel_booking(self, booking_id):
        if booking_id in self.user_bookings:
            self.booking_queue.remove(booking_id)
            del self.user_bookings[booking_id]
            return True
        return False