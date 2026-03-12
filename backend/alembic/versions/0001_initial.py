"""Initial migration - create all tables

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

# Pre-declared enums with create_type=False — prevents SA from auto-creating them
# We create them manually below via conn.execute(DO $$ ... $$)
gender = postgresql.ENUM('male', 'female', 'other', name='gender', create_type=False)
userrole = postgresql.ENUM('user', 'admin', 'super_admin', name='userrole', create_type=False)
teststatus = postgresql.ENUM('in_progress', 'completed', 'abandoned', 'expired', name='teststatus', create_type=False)
resultstatus = postgresql.ENUM('normal', 'warning', 'concern', 'skipped', name='resultstatus', create_type=False)
testtype = postgresql.ENUM(
    'visual_acuity', 'color_blindness', 'amsler_grid', 'contrast', 'astigmatism',
    'duochrome', 'near_vision', 'red_desaturation', 'perimetry', 'dry_eye',
    'glaucoma', 'cataract', 'myopia', 'chorioretinitis', 'retinal_dystrophy',
    name='testtype', create_type=False
)
eyeside = postgresql.ENUM('right', 'left', 'both', name='eyeside', create_type=False)
appointmentstatus = postgresql.ENUM(
    'pending', 'confirmed', 'completed', 'cancelled', 'no_show',
    name='appointmentstatus', create_type=False
)
notificationtype = postgresql.ENUM(
    'reminder', 'result', 'appointment', 'promotion', 'system',
    name='notificationtype', create_type=False
)
notificationchannel = postgresql.ENUM(
    'push', 'telegram', 'sms', 'email',
    name='notificationchannel', create_type=False
)
notificationstatus = postgresql.ENUM(
    'pending', 'sent', 'delivered', 'failed', 'read',
    name='notificationstatus', create_type=False
)


def upgrade() -> None:
    conn = op.get_bind()

    # === ENUMS (idempotent — safe to rerun) ===
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE gender AS ENUM ('male', 'female', 'other');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE userrole AS ENUM ('user', 'admin', 'super_admin');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE teststatus AS ENUM ('in_progress', 'completed', 'abandoned', 'expired');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE resultstatus AS ENUM ('normal', 'warning', 'concern', 'skipped');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE testtype AS ENUM ("
        " 'visual_acuity', 'color_blindness', 'amsler_grid', 'contrast', 'astigmatism',"
        " 'duochrome', 'near_vision', 'red_desaturation', 'perimetry', 'dry_eye',"
        " 'glaucoma', 'cataract', 'myopia', 'chorioretinitis', 'retinal_dystrophy'"
        "); EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE eyeside AS ENUM ('right', 'left', 'both');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE appointmentstatus AS ENUM ('pending', 'confirmed', 'completed', 'cancelled', 'no_show');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE notificationtype AS ENUM ('reminder', 'result', 'appointment', 'promotion', 'system');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE notificationchannel AS ENUM ('push', 'telegram', 'sms', 'email');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))
    conn.execute(sa.text(
        "DO $$ BEGIN CREATE TYPE notificationstatus AS ENUM ('pending', 'sent', 'delivered', 'failed', 'read');"
        " EXCEPTION WHEN duplicate_object THEN null; END $$;"
    ))

    # === USERS ===
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('phone', sa.String(20), unique=True, nullable=True),
        sa.Column('email', sa.String(255), unique=True, nullable=True),
        sa.Column('telegram_id', sa.BigInteger(), unique=True, nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('birth_date', sa.DateTime(), nullable=True),
        sa.Column('gender', gender, nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('language', sa.String(5), server_default='uz'),
        sa.Column('timezone', sa.String(50), server_default='Asia/Tashkent'),
        sa.Column('notifications_enabled', sa.Boolean(), server_default='true'),
        sa.Column('reminder_days', sa.Integer(), server_default='180'),
        sa.Column('fcm_token', sa.String(500), nullable=True),
        sa.Column('device_id', sa.String(255), nullable=True),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('verification_code', sa.String(6), nullable=True),
        sa.Column('verification_expires_at', sa.DateTime(), nullable=True),
        sa.Column('role', userrole, server_default='user'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_blocked', sa.Boolean(), server_default='false'),
        sa.Column('blocked_reason', sa.Text(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('login_count', sa.Integer(), server_default='0'),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'])
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'])

    # === ADMINS ===
    op.create_table(
        'admins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), server_default='admin'),
        sa.Column('permissions', postgresql.JSONB(), server_default='{}'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('two_factor_enabled', sa.Boolean(), server_default='false'),
        sa.Column('two_factor_secret', sa.String(255), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0'),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )

    # === DOCTORS ===
    op.create_table(
        'doctors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('specialty', sa.String(100), server_default='Oftalmolog'),
        sa.Column('experience', sa.String(50), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('telegram', sa.String(50), nullable=True),
        sa.Column('clinic_name', sa.String(255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('district', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('work_hours', sa.String(100), nullable=True),
        sa.Column('work_days', sa.String(50), nullable=True),
        sa.Column('consultation_price', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(3), server_default='UZS'),
        sa.Column('rating', sa.Float(), server_default='0.0'),
        sa.Column('review_count', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('priority', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_doctors_city', 'doctors', ['city'])
    op.create_index('idx_doctors_is_active', 'doctors', ['is_active'])
    op.create_index('idx_doctors_rating', 'doctors', ['rating'])

    # === TEST SESSIONS ===
    op.create_table(
        'test_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('session_token', sa.String(64), unique=True, nullable=False),
        sa.Column('source', sa.String(20), server_default='web'),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('device_type', sa.String(20), nullable=True),
        sa.Column('browser', sa.String(50), nullable=True),
        sa.Column('os', sa.String(50), nullable=True),
        sa.Column('screen_width', sa.Integer(), nullable=True),
        sa.Column('screen_height', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('calibrated_distance_cm', sa.Integer(), nullable=True),
        sa.Column('ipd_mm', sa.Float(), nullable=True),
        sa.Column('status', teststatus, server_default='in_progress'),
        sa.Column('pdf_url', sa.Text(), nullable=True),
        sa.Column('pdf_generated_at', sa.DateTime(), nullable=True),
        sa.Column('overall_status', sa.String(20), nullable=True),
        sa.Column('concerns', postgresql.JSONB(), nullable=True),
        sa.Column('recommendations', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_test_sessions_status', 'test_sessions', ['status'])
    op.create_index('idx_test_sessions_created_at', 'test_sessions', ['created_at'])
    op.create_index('idx_test_sessions_source', 'test_sessions', ['source'])
    op.create_index(op.f('ix_test_sessions_user_id'), 'test_sessions', ['user_id'])
    op.create_index(op.f('ix_test_sessions_session_token'), 'test_sessions', ['session_token'])

    # === TEST RESULTS ===
    op.create_table(
        'test_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_type', testtype, nullable=False),
        sa.Column('test_order', sa.Integer(), nullable=False),
        sa.Column('eye_side', eyeside, server_default='both'),
        sa.Column('score', sa.String(50), nullable=True),
        sa.Column('status', resultstatus, server_default='normal'),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('distance_cm', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_test_results_test_type', 'test_results', ['test_type'])
    op.create_index('idx_test_results_status', 'test_results', ['status'])
    op.create_index(op.f('ix_test_results_session_id'), 'test_results', ['session_id'])

    # === BOT TEST SESSIONS ===
    op.create_table(
        'bot_test_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('has_eye_fatigue', sa.String(20), nullable=True),
        sa.Column('has_foggy_vision', sa.String(20), nullable=True),
        sa.Column('has_burning', sa.String(20), nullable=True),
        sa.Column('has_distant_blur', sa.String(20), nullable=True),
        sa.Column('has_peripheral_darkness', sa.String(20), nullable=True),
        sa.Column('has_floaters', sa.String(20), nullable=True),
        sa.Column('suspected_conditions', postgresql.JSONB(), nullable=True),
        sa.Column('test_results', postgresql.JSONB(), nullable=True),
        sa.Column('recommended_tests', postgresql.JSONB(), nullable=True),
        sa.Column('medications', postgresql.JSONB(), nullable=True),
        sa.Column('current_step', sa.String(50), server_default='start'),
        sa.Column('is_completed', sa.Boolean(), server_default='false'),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_bot_sessions_telegram_id', 'bot_test_sessions', ['telegram_id'])
    op.create_index('idx_bot_sessions_completed', 'bot_test_sessions', ['is_completed'])

    # === TELEGRAM SESSIONS ===
    op.create_table(
        'telegram_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), unique=True, nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('username', sa.String(50), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('language_code', sa.String(5), nullable=True),
        sa.Column('current_state', sa.String(50), server_default='idle'),
        sa.Column('state_data', postgresql.JSONB(), nullable=True),
        sa.Column('message_count', sa.Integer(), server_default='0'),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('language', sa.String(5), server_default='uz'),
        sa.Column('notifications_enabled', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index(op.f('ix_telegram_sessions_telegram_id'), 'telegram_sessions', ['telegram_id'])

    # === BOT MESSAGES ===
    op.create_table(
        'bot_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('direction', sa.String(10), nullable=False),
        sa.Column('content_type', sa.String(20), server_default='text'),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_bot_messages_created_at', 'bot_messages', ['created_at'])
    op.create_index(op.f('ix_bot_messages_telegram_id'), 'bot_messages', ['telegram_id'])

    # === DOCTOR REVIEWS ===
    op.create_table(
        'doctor_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), server_default='false'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('admins.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index(op.f('ix_doctor_reviews_doctor_id'), 'doctor_reviews', ['doctor_id'])

    # === APPOINTMENTS ===
    op.create_table(
        'appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_sessions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), server_default='30'),
        sa.Column('status', appointmentstatus, server_default='pending'),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('doctor_notes', sa.Text(), nullable=True),
        sa.Column('reminder_sent', sa.Boolean(), server_default='false'),
        sa.Column('reminder_sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_appointments_scheduled_at', 'appointments', ['scheduled_at'])
    op.create_index('idx_appointments_status', 'appointments', ['status'])
    op.create_index(op.f('ix_appointments_user_id'), 'appointments', ['user_id'])
    op.create_index(op.f('ix_appointments_doctor_id'), 'appointments', ['doctor_id'])

    # === NOTIFICATIONS ===
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', notificationtype, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=True),
        sa.Column('channel', notificationchannel, nullable=False),
        sa.Column('status', notificationstatus, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_notifications_status', 'notifications', ['status'])
    op.create_index('idx_notifications_type', 'notifications', ['type'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'])

    # === APP SETTINGS ===
    op.create_table(
        'app_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', postgresql.JSONB(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='false'),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('admins.id', ondelete='SET NULL'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )

    # === ACTIVITY LOGS ===
    op.create_table(
        'activity_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_type', sa.String(20), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_activity_logs_actor', 'activity_logs', ['actor_type', 'actor_id'])
    op.create_index('idx_activity_logs_action', 'activity_logs', ['action'])
    op.create_index('idx_activity_logs_created_at', 'activity_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('activity_logs')
    op.drop_table('app_settings')
    op.drop_table('notifications')
    op.drop_table('appointments')
    op.drop_table('doctor_reviews')
    op.drop_table('bot_messages')
    op.drop_table('telegram_sessions')
    op.drop_table('bot_test_sessions')
    op.drop_table('test_results')
    op.drop_table('test_sessions')
    op.drop_table('doctors')
    op.drop_table('admins')
    op.drop_table('users')

    conn = op.get_bind()
    for name in [
        'notificationstatus', 'notificationchannel', 'notificationtype',
        'appointmentstatus', 'eyeside', 'testtype', 'resultstatus',
        'teststatus', 'userrole', 'gender'
    ]:
        conn.execute(sa.text(f'DROP TYPE IF EXISTS {name}'))
