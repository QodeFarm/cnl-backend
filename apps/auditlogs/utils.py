from .models import AuditLog

def log_user_action(db, user_id, action_type, module_name, record_id, description=None):
    try:
        AuditLog.objects.using(db).create(
            user_id=user_id,
            action_type=action_type,
            module_name=module_name,
            record_id=record_id,
            description=description
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log user activity for {module_name}: {str(e)}")
