from marshmallow import Schema, fields


class DownloadUrlCreateRequest(Schema):
    url = fields.Str(description="URL", required=True)
    path = fields.Str(description="File Path", required=True)
    http_user_agent = fields.Str(description="User Agent")
    http_referer = fields.Str(description="Referer")
    auth_username = fields.Str(description="Authentication Username")
    auth_password = fields.Str(description="Authentication Password")
    cookie_jar = fields.Str(description="Cookie Jar")
    meta = fields.Str(description="Metadata")


class DownloadUrlDestroyRequest(Schema):
    id = fields.Int(description="Download Id", required=True)


class DownloadUrlUpdateRequest(Schema):
    id = fields.Int(description="Download Id", required=True)
    retries = fields.Int(description="Retry times", required=True)
    downloaded_at = fields.Str(description="Last Downloaded At", required=True)
