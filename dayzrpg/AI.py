
# To hold generic AI & entity management classes
# Each entity type's states should exist in their own files.


class BaseGameEntity(object):
    """In the book this makes sure that all entities have an update function implemented
        but also ensures they have a unique identifier"""
    def __init__(self):
        pass

    def update(self):
        raise NotImplementedError


# class EntityManager(object):
#    """Keeps track of all entities with a unique identifier
#        Dead entities should be removed when they die.
#        In the book this is a singleton class"""
#    def __init__(self):
#        self.active_entities = {}
#        # Active entities stored as string name in dict - is there a better way?
#        # Entities don't have numerical id's - identified by their name currently
       
#    def add_entity(self, entity):
#        self.active_entities[entity.name] = entity

#    def remove_entity(self, str_entity_name):
#        del self.active_entities[str_entity_name]

#    def get_entity(self, str_entity_name):
#        return self.active_entities[str_entity_name]


class State_Machine():
    """In the book this is a singleton class"""
    def __init__(self, owner):
        self.owner = owner
        self.current_state = None
        self.previous_state = None
        self.global_state = None

    def set_current_state(self, state):
        self.owner.current_state = state

    def set_global_state(self, state):
        self.owner.global_state = state

    def set_previous_state(self, state):
        self.owner.previous_state = state

    def update(self):
        if isinstance(self.global_state, State):
            self.global_state.execute()
        if isinstance(self.current_state, State):
            self.current_state.execute()

    def change_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()

    def revert_to_previous_state(self):
        self.change_state(self.previous_state)


class State(object):
    """A base class to handle the state and state transitions of game entities"""
    def __init__(self, mob):
        self.mob = mob

    def enter(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def exit(self):
        raise NotImplementedError
