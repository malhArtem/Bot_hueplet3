class Battle:
    def __init__(self, attacker: int, defender: int):
        self.attacker = attacker
        self.defender = defender


class TopUser:
    def __init__(self, row_number: int, user_id: int, chat_id: int, name: str, chat_name: str, length: int):
        self.row_number = row_number
        self.user_id = user_id
        self.chat_id = chat_id
        self.name = name
        self.chat_name = chat_name
        self.length = length


class Huy:
    def __init__(self, adder=0, attack=0, defense=0, force=0, trys=0):
        self.adder = adder
        self.attack = attack
        self.defense = defense
        self.force = force
        self.trys = trys
