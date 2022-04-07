class MusicException(Exception):
    pass

class YTDLException(MusicException):
    pass

class TopTracksException(MusicException):
    pass

class CreateTrackEventException(MusicException):
    pass

class MessageException(Exception):
    pass

class MessageCreateException(Exception):
    pass

class UserException(MessageException):
    pass

class MessageSelectionException(MessageException):
    pass

class RequestException(Exception):
    pass

class SentimentCreateException(Exception):
    pass
