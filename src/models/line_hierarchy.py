from enum import Enum

class Hierarchy(Enum):
    PARENT = 1
    CHILD1 = 2
    CHILD2 = 3


completed_request_body = {
    'PARENT': Hierarchy.PARENT,
    'CHILD1': Hierarchy.CHILD1,
    'CHILD2': Hierarchy.CHILD2
}