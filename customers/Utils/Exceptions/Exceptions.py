from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)


def AuthExceptionHandler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred"
        data = None

        if isinstance(response.data, dict):
            if "detail" in response.data:
                detail = response.data["detail"]

                if isinstance(detail, dict):
                    messages = detail.get("messages", [])
                    if isinstance(messages, list) and len(messages) > 0:
                        message = str(messages[0].get("message", "Token is invalid or has expired."))
                    else:
                        message = str(detail.get("string", "Token is invalid or has expired."))
                else:
                    message = str(detail)

            else:
                field_errors = {}
                for field, err in response.data.items():
                    field_errors[field] = [str(m) for m in err] if isinstance(err, list) else [str(err)]

                first_key = next(iter(field_errors), None)
                if first_key:
                    message = f"{first_key}: {field_errors[first_key][0]}"
                    if len(field_errors) > 1 or len(field_errors[first_key]) > 1:
                        data = {"errors": field_errors}

        elif isinstance(response.data, list) and len(response.data) > 0:
            message = str(response.data[0])

        response.data = {
            "status": "fail",
            "message": message,
            "data": data,
        }

    return response