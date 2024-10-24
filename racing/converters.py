class ConferenceConverter:
    regex = "AUS|RSEQ|OUA|CW"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
