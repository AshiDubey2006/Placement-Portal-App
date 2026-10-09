from app.tasks.celery_config import celery_app
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='app.tasks.report_tasks.send_monthly_report')
def send_monthly_report():
    """
    Scheduled on the 1st of every month at 07:00 UTC.
    Generates an HTML monthly placement report and emails it to the admin.
    """
    from app import create_app
    flask_app = create_app()

    with flask_app.app_context():
        from app.models.drive import Drive
        from app.models.application import Application
        from app.models.student import Student
        from app.models.company import Company
        from app.models.user import User
        from sqlalchemy import func

        now = datetime.utcnow()
        first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_prev_month = first_day_this_month - timedelta(seconds=1)
        first_day_prev_month = last_day_prev_month.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        period_label = last_day_prev_month.strftime('%B %Y')

        drives_last_month = Drive.query.filter(
            Drive.created_at >= first_day_prev_month,
            Drive.created_at < first_day_this_month
        ).all()

        all_applications = Application.query.filter(
            Application.created_at >= first_day_prev_month,
            Application.created_at < first_day_this_month
        ).all()

        unique_students = len(set(a.student_id for a in all_applications))
        total_selected = sum(1 for a in all_applications if a.status == 'Selected')
        total_shortlisted = sum(1 for a in all_applications if a.status == 'Shortlisted')

        total_students_ever = Student.query.count()
        total_companies_ever = Company.query.filter_by(approval_status='Approved').count()

        drive_rows = ''
        for drive in drives_last_month:
            drive_apps = [a for a in all_applications if a.drive_id == drive.id]
            selected = sum(1 for a in drive_apps if a.status == 'Selected')
            shortlisted = sum(1 for a in drive_apps if a.status == 'Shortlisted')
            company_name = drive.company.company_name if drive.company else 'N/A'
            deadline = drive.application_deadline.strftime('%d %b %Y') if drive.application_deadline else 'N/A'
            drive_rows += f"""
            <tr>
                <td>{company_name}</td><td>{drive.job_title}</td>
                <td>{len(drive_apps)}</td><td>{shortlisted}</td>
                <td>{selected}</td><td>{deadline}</td>
            </tr>"""

        if not drive_rows:
            drive_rows = '<tr><td colspan="6" style="text-align:center">No drives this period</td></tr>'

        branch_stats = (
            Student.query
            .join(Application, Application.student_id == Student.id)
            .filter(
                Application.created_at >= first_day_prev_month,
                Application.created_at < first_day_this_month
            )
            .with_entities(Student.branch, func.count(Application.id).label('cnt'))
            .group_by(Student.branch).all()
        )
        branch_rows = ''.join(
            f'<tr><td>{b.branch}</td><td>{b.cnt}</td></tr>' for b in branch_stats
        ) or '<tr><td colspan="2">No data</td></tr>'

        html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Monthly Placement Report – {period_label}</title>
  <style>
    body{{font-family:Arial,sans-serif;margin:30px;color:#333;line-height:1.7}}
    h1{{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px}}
    h2{{color:#283593;margin-top:30px}}
    .stat-grid{{display:flex;flex-wrap:wrap;gap:16px;margin:20px 0}}
    .stat-box{{background:#e8eaf6;border-left:5px solid #3f51b5;padding:16px 24px;border-radius:6px;min-width:140px}}
    .stat-box .value{{font-size:2rem;font-weight:bold;color:#1a237e}}
    .stat-box .label{{font-size:0.85rem;color:#555}}
    table{{border-collapse:collapse;width:100%;margin-top:12px}}
    th{{background:#3f51b5;color:#fff;padding:10px 14px;text-align:left}}
    td{{padding:9px 14px;border-bottom:1px solid #ddd}}
    tr:nth-child(even) td{{background:#f5f5f5}}
    .footer{{margin-top:40px;font-size:0.8rem;color:#aaa;border-top:1px solid #ddd;padding-top:12px}}
  </style>
</head>
<body>
  <h1>Monthly Placement Activity Report</h1>
  <p><strong>Period:</strong> {period_label} &nbsp;|&nbsp;
     <strong>Generated:</strong> {now.strftime('%d %b %Y, %H:%M UTC')}</p>
  <div class="stat-grid">
    <div class="stat-box"><div class="value">{len(drives_last_month)}</div><div class="label">Drives This Month</div></div>
    <div class="stat-box"><div class="value">{len(all_applications)}</div><div class="label">Total Applications</div></div>
    <div class="stat-box"><div class="value">{unique_students}</div><div class="label">Students Applied</div></div>
    <div class="stat-box"><div class="value">{total_shortlisted}</div><div class="label">Shortlisted</div></div>
    <div class="stat-box"><div class="value">{total_selected}</div><div class="label">Selected</div></div>
    <div class="stat-box"><div class="value">{total_students_ever}</div><div class="label">Registered Students</div></div>
    <div class="stat-box"><div class="value">{total_companies_ever}</div><div class="label">Approved Companies</div></div>
  </div>
  <h2>Drive-wise Breakdown</h2>
  <table>
    <thead><tr><th>Company</th><th>Job Title</th><th>Applications</th><th>Shortlisted</th><th>Selected</th><th>Deadline</th></tr></thead>
    <tbody>{drive_rows}</tbody>
  </table>
  <h2>Branch-wise Applications</h2>
  <table>
    <thead><tr><th>Branch</th><th>Applications</th></tr></thead>
    <tbody>{branch_rows}</tbody>
  </table>
  <div class="footer">Auto-generated by Placement Portal on {now.strftime('%d %b %Y at %H:%M UTC')}.</div>
</body>
</html>"""

        report_filename = f"monthly_report_{last_day_prev_month.strftime('%Y_%m')}.html"
        report_path = os.path.join(flask_app.config['UPLOAD_FOLDER'], report_filename)
        with open(report_path, 'w', encoding='utf-8') as fh:
            fh.write(html_report)

        # Email to admin if mail is configured
        admin_email = flask_app.config.get('ADMIN_EMAIL', 'admin@placementportal.com')
        sent = False
        if flask_app.config.get('MAIL_USERNAME'):
            try:
                from flask_mail import Mail, Message
                mail = Mail(flask_app)
                msg = Message(
                    subject=f"Placement Portal – Monthly Report ({period_label})",
                    recipients=[admin_email],
                    html=html_report
                )
                with flask_app.app_context():
                    mail.send(msg)
                sent = True
            except Exception as exc:
                logger.warning("Monthly report email failed: %s", exc)

        result_msg = f"Monthly report for {period_label} saved as {report_filename}. Email sent: {sent}"
        logger.info(result_msg)
        return result_msg
