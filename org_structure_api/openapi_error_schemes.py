from drf_spectacular.utils import OpenApiResponse

BAD_REQUEST_RESP_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'error_field': {
                'type': 'array',
                'items':
                    {
                        'type': 'string',
                        'default': 'список ошибок'
                    }
            },
        }
    },
    description='ошибка валидации'
)

NOT_FOUND_RESP_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'detail': {
                'type': 'string',
                'default': 'описание ошибки'
            },
        }
    },
    description='ошибка поиска объекта'
)