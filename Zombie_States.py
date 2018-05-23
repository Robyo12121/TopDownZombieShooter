import AI
class ZombieGlobalState(State):
    def __init__(self, mob):
        super().__init__(mob)

    def enter(self):
        pass
    
    def execute(self):
        #Conditional things in if statements#

        #Things to happen every update
        pass
            
    def exit(self):
        pass


class Idle(State):
    def __init__(self, mob):
        self.mob = mob

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass


class Aggro(State):
    def __init__(self, mob):
        self.mob = mob

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass


class Suspicious(State):
    def __init__(self, mob):
        self.mob = mob

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass
