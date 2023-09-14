import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        *[(4, "2030-05-01", "2030-05-15", 200)] * 8,
        (4, "2030-05-01", "2030-05-15", 409),
        (4, "2030-05-01", "2030-05-15", 409),
        (4, "2030-05-01", "2030-04-15", 400),
        (4, "2030-05-01", "2030-10-15", 400),
    ],
)
async def test_add_new_get_booking(
    room_id, date_from, date_to, status_code, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.post(
        "/bookings",
        params={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )

    assert response.status_code == status_code


async def test_get_and_delete_bookings(authenticated_ac: AsyncClient):
    # Получаем все бронирования текущего аутентифицированного пользователя
    response = await authenticated_ac.get("/bookings")
    assert response.status_code == 200

    # Проверяем, что полученные бронирования не пусты
    bookings = response.json()
    assert len(bookings) > 0

    for booking in bookings:
        await authenticated_ac.delete(f"/bookings/{booking['id']}")

    # Получаем все бронирования текущего аутентифицированного пользователя
    response = await authenticated_ac.get("/bookings")
    assert response.status_code == 200

    # Проверяем, что полученные бронирования не пусты
    bookings = response.json()
    assert len(bookings) == 0


async def test_crud_booking(authenticated_ac: AsyncClient):
    create_response = await authenticated_ac.post(
        "/bookings",
        params={
            "room_id": 1,
            "date_from": "2023-09-15",
            "date_to": "2023-09-25",
        },
    )
    assert create_response.status_code == 200
    created_booking_id = create_response.json()["id"]

    # Чтение бронирования по его id
    read_response = await authenticated_ac.get(f"/bookings/{created_booking_id}")
    assert read_response.status_code == 200
    read_booking_data = read_response.json()
    assert read_booking_data["id"] == created_booking_id

    # Удаление бронирования
    delete_response = await authenticated_ac.delete(f"/bookings/{created_booking_id}")
    assert delete_response.status_code == 204

    # Попытка прочитать удаленное бронирование (должно вернуть 404)
    read_deleted_response = await authenticated_ac.get(
        f"/bookings/{created_booking_id}"
    )
    assert read_deleted_response.status_code == 404
