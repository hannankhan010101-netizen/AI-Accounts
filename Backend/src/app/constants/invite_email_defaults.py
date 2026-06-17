"""Default invite / welcome email copy — P30."""

from __future__ import annotations

INVITE_EMAIL_TEMPLATE_KEY = "inviteEmailTemplate"
WELCOME_EMAIL_TEMPLATE_KEY = "welcomeEmailTemplate"

DEFAULT_INVITE_EMAIL_TEMPLATE: dict[str, str] = {
    "subject": "You have been invited to {companyName}",
    "introText": (
        "You have been invited to join {companyName} on Fast Accounts.\n\n"
        "Set your password here:\n  {resetLink}\n\n"
        "Your verification code is:\n  {code}\n\n"
        "This code expires in {ttlMinutes} minutes.\n"
    ),
    "introHtml": (
        "<p>You have been invited to join <strong>{companyName}</strong> "
        "on Fast Accounts.</p>"
        '<p><a href="{resetLink}">Set your password</a></p>'
        '<p style="font-size:24px;font-weight:bold;letter-spacing:4px">{code}</p>'
        "<p>This code expires in {ttlMinutes} minutes.</p>"
    ),
}

DEFAULT_WELCOME_EMAIL_TEMPLATE: dict[str, str] = {
    "subject": "You now have access to {companyName}",
    "introText": (
        "You have been added to {companyName} on Fast Accounts.\n\n"
        "Sign in here:\n  {loginUrl}\n"
    ),
    "introHtml": (
        "<p>You have been added to <strong>{companyName}</strong> on Fast Accounts.</p>"
        '<p><a href="{loginUrl}">Sign in</a></p>'
    ),
}
