
class Prov2BigchainDBException(Exception):
    pass


class InvalidOptionsException(Prov2BigchainDBException):
    pass


class CreateRecordException(Prov2BigchainDBException):
    pass

class NoDocumentException(Prov2BigchainDBException):
    pass

class ParseException(Prov2BigchainDBException):
    pass