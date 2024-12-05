from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from models import SystemLog
from functools import wraps
import traceback

def handle_error(error):
    """通用错误处理函数"""
    if isinstance(error, HTTPException):
        response = {
            'error': {
                'code': error.code,
                'name': error.name,
                'description': error.description
            }
        }
        status_code = error.code
    else:
        response = {
            'error': {
                'code': 500,
                'name': 'Internal Server Error',
                'description': str(error)
            }
        }
        status_code = 500
    
    # 记录错误日志
    SystemLog.log(
        'ERROR',
        'System',
        'Error',
        None,
        request.remote_addr,
        f'{response["error"]["name"]}: {response["error"]["description"]}\n{traceback.format_exc()}'
    )
    
    # 根据请求类型返回不同格式的响应
    if request.is_json or request.path.startswith('/api/'):
        return jsonify(response), status_code
    else:
        return render_template('error.html', error=response['error']), status_code

def setup_error_handlers(app):
    """设置错误处理器"""
    # 处理 404 错误
    @app.errorhandler(404)
    def not_found_error(error):
        return handle_error(error)
    
    # 处理 500 错误
    @app.errorhandler(500)
    def internal_error(error):
        return handle_error(error)
    
    # 处理数据库错误
    @app.errorhandler(Exception)
    def unhandled_exception(error):
        return handle_error(error)

def handle_exceptions(f):
    """异常处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return handle_error(e)
    return decorated_function

class ValidationError(Exception):
    """验证错误"""
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field

def validate_required_fields(data, required_fields):
    """验证必填字段"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            missing_fields
        )

def validate_file_upload(file, allowed_extensions, max_size_mb=10):
    """验证文件上传"""
    if not file:
        raise ValidationError("No file uploaded")
    
    # 检查文件扩展名
    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        raise ValidationError(
            f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # 检查文件大小
    if len(file.read()) > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size exceeds {max_size_mb}MB limit")
    
    # 重置文件指针
    file.seek(0)
