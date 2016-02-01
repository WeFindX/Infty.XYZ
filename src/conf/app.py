LOCAL_APPS = (
    'users',
    'core',
    'payments',
    'invitation',
    'hours',
)

CONVERSATION_EMAIL_TEMPLATE = """
Hi [{{invited_user}}],

Your friend [{{existing_user}}] has posted a milestone [{{object.name}}] to solve a problem [{{object.plan.idea.goal.name}}], and invites you to help.

Use this unique link to see the milestone:
{{ invitation_link }}

Your password for future logins: {{user_password}}

The Infinity Project, Inc.

>> {{ invitation_text }}
"""

CONSTANCE_CONFIG = {
    'PAYPAL_MODE': ('sandbox', 'sandbox or live'),
    'PAYPAL_APPLICATION_ID': ('APP-80W284485P519543T', 'PayPal application ID'),
    'PAYPAL_SECURITY_USERID': ('shamkir-facilitator_api1.gmail.com', 'PayPal security user id'),
    'PAYPAL_SECURITY_PASSWORD': ('HATJ3CEGRHZVQTZV', 'PayPal security password'),
    'PAYPAL_SECURITY_SIGNATURE': ('AFcWxV21C7fd0v3bYYYRCpSSRl31AU7eDuvOQwePEQhUEjtkBesDYrC.', 'PayPal security signature'),
    'PAYPAL_CANCEL_URL': ('http://localhost:3000/', 'PayPal cancel URL'),
    'MAX_MENTIONS_PER_COMMENT': (10, '_comment_post_save email notifications per comment'),
    'CONVERSATION_EMAIL_TEMPLATE': ('Hello, your conversation url: {{conversation_url}}, Your password: {{user_password}}', ''),
    'DEFINITION_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'NEED_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'GOAL_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'IDEA_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'PLAN_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'STEP_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'TASK_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'WORK_CONVERSATION_EMAIL_TEMPLATE': (CONVERSATION_EMAIL_TEMPLATE, 'available tags: {{ conversation_url }}, {{ user_password }}, {{ invited_user }}, {{ existing_user }}, {{ object }}'),
    'CONVERSATION_SUBJECT': ('Invitation to conversation', ''),
    'CONVERSATION_FROM_EMAIL': ('noreply@infty.xyz', ''),
    'MAX_COMMENTS_IN_USER_PROFILE': (100, 'number of comments to display on user profiles')
}

AUTH_USER_MODELS = [
    "users.User",
]

"""
    Set default auth user model from models list
    if AUTH_USER_MODELS is empty, set django user model by default
"""

AUTH_USER_MODEL = "users.User"

LOGIN_URL = '/user/login/'

INVITATIONS_INVITATION_ONLY = True

# Some autoslag handler that we need to create for make tests runnable


def auto_slag_handler():
    return 'auto_slug'


def auto_markdown_field_gen():
    return 'auto_markdown'

MOMMY_CUSTOM_FIELDS_GEN = {
    'django_extensions.db.fields.AutoSlugField': auto_slag_handler,
    'django_markdown.models.MarkdownField': auto_markdown_field_gen
}
