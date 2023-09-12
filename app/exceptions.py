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
    
class HotelNotFound(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail='Отель не найден'
    
class NoRightsToDelete(BaseException):
    status_code=status.HTTP_403_FORBIDDEN
    detail='Вы не имеете права удалять это бронирование.'
    
class DateError(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail='Дата заезда >= Дата выезда'
    
class TooManyDays(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail='Бронь не может быть больше 30 дней'




