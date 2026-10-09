from app.tasks.celery_config import celery_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='app.tasks.reminder_tasks.send_daily_reminders')
def send_daily_reminders():
    """
    Scheduled daily at 08:00 UTC.
    Sends reminders to eligible students who haven't applied to drives
    whose deadline is within the next 3 days.
    """
    from app import create_app
    flask_app = create_app()

    with flask_app.app_context():
        from app.models.drive import Drive
        from app.models.student import Student
        from app.models.application import Application
        from app.models.user import User

        three_days_from_now = datetime.utcnow() + timedelta(days=3)
        upcoming_drives = Drive.query.filter(
            Drive.status == 'Approved',
            Drive.application_deadline <= three_days_from_now,
            Drive.application_deadline > datetime.utcnow()
        ).all()

        reminders_sent = 0

        for drive in upcoming_drives:
            days_left = (drive.application_deadline - datetime.utcnow()).days
            deadline_str = drive.application_deadline.strftime('%d %b %Y %H:%M UTC')

            active_students = Student.query.join(User).filter(
                User.is_active == True,
                User.is_blacklisted == False
            ).all()

            for student in active_students:
                if not drive.is_eligible(student):
                    continue
                already_applied = Application.query.filter_by(
                    student_id=student.id, drive_id=drive.id
                ).first()
                if already_applied:
                    continue

                subject = f"Reminder: Apply for {drive.job_title} at {drive.company.company_name}"
                html_body = f"""
                <html><body>
                <p>Dear {student.full_name},</p>
                <p>This is a reminder that the placement drive
                <strong>{drive.job_title}</strong> by
                <strong>{drive.company.company_name}</strong>
                closes on <strong>{deadline_str}</strong>
                ({days_left} day(s) remaining).</p>
                <p>Log in to the Placement Portal and apply before the deadline.</p>
                <p>Regards,<br>Placement Cell</p>
                </body></html>
                """
                gchat_text = (
                    f"📢 Reminder for {student.full_name}: "
                    f"Apply to *{drive.job_title}* at *{drive.company.company_name}* "
                    f"by {deadline_str}. ({days_left} day(s) left)"
                )

                sent = False
                student_email = student.user.email if student.user else None

                # Try email
                if student_email and flask_app.config.get('MAIL_USERNAME'):
                    try:
                        from flask_mail import Mail, Message
                        mail = Mail(flask_app)
                        msg = Message(subject=subject, recipients=[student_email], html=html_body)
                        with flask_app.app_context():
                            mail.send(msg)
                        sent = True
                    except Exception as exc:
                        logger.warning("Email failed: %s", exc)

                # Try Google Chat webhook
                if not sent:
                    webhook_url = flask_app.config.get('GOOGLE_CHAT_WEBHOOK_URL')
                    if webhook_url:
                        try:
                            import requests
                            r = requests.post(webhook_url, json={'text': gchat_text}, timeout=10)
                            r.raise_for_status()
                            sent = True
                        except Exception as exc:
                            logger.warning("GChat webhook failed: %s", exc)

                # Fallback to log
                if not sent:
                    logger.info("REMINDER | %s | %s | deadline %s",
                                student.full_name, drive.job_title, deadline_str)

                reminders_sent += 1

        result_msg = f"Daily reminders: {reminders_sent} notifications dispatched."
        logger.info(result_msg)
        return result_msg
