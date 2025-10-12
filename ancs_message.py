

class ANCSMessage:

    def __init__(self, **kwargs):
        self.event_id = kwargs.get('event_id')
        self.action = kwargs.get('action')
        self.category = kwargs.get('category')
        self.count = kwargs.get('count')

    def __repr__(self):
        return "%s: %s (%s), id: %s" % (self.action, self.category, self.count, self.event_id)

    def to_json(self):
        return {
            "event_id": self.event_id,
            "action": self.action,
            "category": self.category,
            "count": self.count
        }

    def __eq__(self, other):
        return self.event_id == other.event_id and self.action == other.action and self.category == self.category

    def __ne__(self, other):
        return not (self == other)

    def get_unique_string(self):
        return "%s_%s" % (self.category, self.event_id)

    @staticmethod
    def set_from_message_string(message_string):
        category_id_lookup = {
            "0": "OTHER",
            "1": "INCOMING CALL",
            "2": "MISSED CALL",
            "3": "VOICE MAIL",
            "4": "SOCIAL",
            "5": "SCHEDULE",
            "6": "EMAIL",
            "7": "NEWS",
            "8": "HEALTH AND FITNESS",
            "9": "BUSINESS AND FINANCE",
            "A": "LOCATION",
            "B": "ENTERTAINMENT"
        }
        action_id_lookup = {
            "0": "ADDED",
            "1": "MODIFIED",
            "2": "DELETED"
        }
        message_string = message_string[1:]

        action_string = action_id_lookup[message_string[0]]
        category_string = category_id_lookup[message_string[1]]
        alert_count = int(message_string[3], 16)
        event_id = message_string[4:]

        return ANCSMessage(
            action=action_string,
            category=category_string,
            count=alert_count,
            event_id=event_id
        )
