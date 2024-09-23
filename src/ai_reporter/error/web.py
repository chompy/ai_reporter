class ElementNotFoundException(Exception):
    """ Element was not found. """
    pass

class InvalidElementException(Exception):
    """ Tried to perform an invalid action on an element. """
    pass