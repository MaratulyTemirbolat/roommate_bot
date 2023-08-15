# Python
from typing import (
    Tuple,
    Dict,
    Any,
)

# Third party
from aiohttp import ClientSession
from aiohttp.client_exceptions import (
    ServerDisconnectedError,
    ClientConnectorError,
)

# Project
from core.api.http_statuses import HTTP_503_SEERVICE_UNAVAILABLE


UNAVAILABLE_SERVER_RESPONSE = {
    "status": HTTP_503_SEERVICE_UNAVAILABLE,
    "response": "Извините, не удается установить соединение с сервером"
}

SERVER_DISCTONNECTED_RESPONSE = {
    "status": HTTP_503_SEERVICE_UNAVAILABLE,
    "response": "Извините, но сервер сейчас недоступен"
}


async def handle_get(
    url: str,
    headers: Dict[str, Any] = {},
    params: Dict[str, Any] = {},
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> Dict[str, Any]:
    result_response: Dict[str, Any] = {}
    try:
        async with ClientSession(headers=headers) as session:
            async with session.get(
                url=url,
                ssl=False,
                params=params
            ) as response:
                result_response.setdefault("status", response.status)
                result_response.setdefault("response", await response.json())
        return result_response
    except ServerDisconnectedError:
        return SERVER_DISCTONNECTED_RESPONSE
    except ClientConnectorError:
        return UNAVAILABLE_SERVER_RESPONSE


async def handle_post(
    url: str,
    headers: Dict[str, Any] = {},
    data: Dict[Any, Any] = {},
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> Dict[str, Any]:
    result_response: Dict[str, Any] = {}
    try:
        async with ClientSession(headers=headers) as session:
            async with session.post(
                url=url,
                data=data
            ) as response:
                result_response.setdefault("status", response.status)
                result_response.setdefault("response", await response.json())
            return result_response
    except ServerDisconnectedError:
        return SERVER_DISCTONNECTED_RESPONSE
    except ClientConnectorError:
        return UNAVAILABLE_SERVER_RESPONSE


# res = run(
#     main=handle_get(
#         url="http://localhost:8000/api/v1/auths/users",
#         headers={
#             "Temirbolat": "hello"
#         },
#         params={
#             "gender": "M",
#             "districts": [1, 2,],
#             "city": 1,
#         },
#     )
# )

# res = run(
#     main=handle_post(
#         url="http://localhost:8000/api/v1/auths/users/register_user",
#         headers={
#             "Temirbolat": "hello"
#         },
#         data={
#             "password": "12345",
#         },
#     )
# )

# print(res)
