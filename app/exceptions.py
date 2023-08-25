from fastapi import HTTPException, status


class BookingException(HTTPException):  # <-- наследуемся от HTTPException,который наследован от Exception
    status_code = 500  # <-- задаем значения по умолчанию
    detail = ""
    
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

    

class UserAlreadyExistException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='Пользователь уже существует'


class IncorrectEmailOrPasswordException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Неверная почта или пароль'


class TokenExpiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Токен истек'


class TokenAbsentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Токен отсутсвует'


class IncorrectTokenFormatException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Неверный формат токена'


class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    
class RoomCannotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='Нет свободных номеров для бронирования'
    
class BookingNotFound(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail='Бронирование не найдено'



