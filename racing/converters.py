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