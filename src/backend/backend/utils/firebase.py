from firebase_admin import credentials, auth, initialize_app


default_app = initialize_app()


def verify_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Hubo un error {e}")