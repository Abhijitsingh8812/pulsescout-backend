-- ====================================================================
-- PULSESCOUT EMAIL OTP MIGRATION
-- Database table and indexes for passwordless Email OTP verification
-- ====================================================================

CREATE TABLE IF NOT EXISTS email_otp_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    attempt_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE NULL
);

-- Performance and query indexes
CREATE INDEX IF NOT EXISTS idx_email_otp_email ON email_otp_codes(email);
CREATE INDEX IF NOT EXISTS idx_email_otp_expires_at ON email_otp_codes(expires_at);
CREATE INDEX IF NOT EXISTS idx_email_otp_created_at ON email_otp_codes(created_at);
