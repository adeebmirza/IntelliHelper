from itsdangerous import URLSafeTimedSerializer

def generate_reset_token(email, secret_key):
    s = URLSafeTimedSerializer(secret_key)
    return s.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, secret_key, expiration=3600):
    s = URLSafeTimedSerializer(secret_key)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expiration)
    except:
        return None
    return email