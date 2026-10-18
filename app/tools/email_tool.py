EMAIL_TOOL = {
    "type": "function",
    "name": "email_service",
    "description": (
        "Send an email to a recipient when the user explicitly "
        "requests an email. Ask for the recipient's email address "
        "if it has not been provided."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "receiver_mail": {
                "type": "string",
                "description": "Recipient's email address",
            },
            "title": {
                "type": "string",
                "description": "Email subject, maximum 15 characters and minimum 5 characters",
            },
            "content": {
                "type": "string",
                "description": "Email body in HTML format, maximum 500 characters and minimum 100 characters ",
            },
        },
        "required": ["receiver_mail", "title", "content"],
        "additionalProperties": False,
    },
    "strict": True,
}