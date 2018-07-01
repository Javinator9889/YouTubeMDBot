from database import InsertOperations, SelectOperations, UpdateOperations


class Handler:
    def __init__(self, handler_messages: dict):
        self.__messages = handler_messages
        self.__insert_operations: InsertOperations = InsertOperations()
        self.__update_operations: UpdateOperations = UpdateOperations()
        self.__select_operations: SelectOperations = SelectOperations()
