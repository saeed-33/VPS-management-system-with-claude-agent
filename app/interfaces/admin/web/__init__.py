"""
واجهة صفحات الويب الإدارية.

تجمع مسارات HTML العامة والمحمية التي تعرض لوحات الإدارة، وتفصل تقديم القوالب
عن خدمات API والمجال.
"""
from app.interfaces.admin.web.routes import router
from app.interfaces.admin.web.auth_routes import router as auth_router

__all__ = ["router", "auth_router"]

__all__ = ["router"]
