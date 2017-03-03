class Prov2BigchainDBException(Exception):
    pass


class CreateRecordException(Prov2BigchainDBException):
    pass


class ParseException(Prov2BigchainDBException):
    pass


class NoAccountException(Prov2BigchainDBException):
    pass


class TransactionIdNotFound(Prov2BigchainDBException):
    pass

class BlockIdNotFound(Prov2BigchainDBException):
    pass