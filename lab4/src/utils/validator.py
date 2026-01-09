class Validator:
    def __init__(self, record_size, index_record_size):
        self.RECORD_SIZE = record_size
        self.INDEX_RECORD_SIZE = index_record_size

    def validate_key(self, key_value):
        if '.' in key_value or ',' in key_value:
            return False, ("Input Error", "Index must be an integer!")

        try:
            if int(key_value) <= 0 and int(key_value) != -1:
                return False, ("Input Error", "Index must be a positive integer!")
        except ValueError:
            return False, ("Input Error", "Index must be an integer!")
        
        if len(key_value) > self.INDEX_RECORD_SIZE:
            return False, ("Limit Exceeded", "Key is too long!")
        
        return True, None

    def validate_data(self, data_value):
        if not data_value.strip():
            return False, ("Input Error", "Data value cannot be empty!")

        if len(data_value) > self.RECORD_SIZE - 1:
            return False, ("Limit Exceeded", "Data is too long!")
        
        return True, None