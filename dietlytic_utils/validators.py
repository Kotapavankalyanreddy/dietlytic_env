
def is_valid_mobile(mobile_number):
    """Check if the mobile number has exactly 10 digits."""
    return mobile_number.isdigit() and len(mobile_number) == 10
