class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class AuthenticationError(ApiError):
    def __init__(self, message: str = "未登录"):
        super().__init__(message, status_code=401, code=401)


class AuthorizationError(ApiError):
    def __init__(self, message: str = "无权限"):
        super().__init__(message, status_code=403, code=403)


class ConflictError(ApiError):
    def __init__(self, message: str):
        super().__init__(message, status_code=409, code=409)


class NotFoundError(ApiError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status_code=404, code=404)
