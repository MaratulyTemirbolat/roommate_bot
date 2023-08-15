def get_valid_phone_number(mobile_phone: str) -> str:
    return "+7" + mobile_phone[1:] \
        if mobile_phone.startswith("8") else mobile_phone
