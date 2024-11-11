import re


class ConferenceConverter:
    regex = "AUS|RSEQ|OUA|CW"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)

class YearConverter:
    regex = "[0-9]{4}"
    
    def to_python(self, value):
        return int(value)
    
    def to_url(self, value):
        return "%04d" % value
    
class RaceConverter:
    regex = r"(\d)+(km|mi)-(male|female)"
    
    def to_python(self, value):
        # returns tuple of (distance, unit, sex)
        # i.e. (8, 'km', 'M')
        
        match = re.match(self.regex, value)
        if match:
            distance = int(match.group(1))
            unit = match.group(2)
            sex = 'M' if match.group(3) == 'male' else 'F'
            
            return (distance, unit, sex)
        
        raise ValueError("Invalid race format")
    
    def to_url(self, value):
        distance, unit, sex = value
        sex_str = 'male' if sex == 'M' else 'female'
        
        return f"{distance}{unit}-{sex_str}"
