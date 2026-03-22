import secrets
from datetime import datetime, timedelta
from flask_mail import Message


class RecuperacionPassword:
    """Gestiona el flujo de recuperación de contraseña por email."""

    def __init__(self, mysql, mail):
        self.mysql = mysql
        self.mail  = mail

    # ── Generar token único ────────────────────────────────────
    def _generar_token(self) -> str:
        return secrets.token_urlsafe(32)

    # ── Verificar si el email existe en la BD ──────────────────
    def email_existe(self, email: str) -> bool:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT id FROM usuarios WHERE email = %s',
                        (email.strip().lower(),))
            row = cur.fetchone()
            cur.close()
            return row is not None
        except Exception:
            return False

    # ── Guardar token en BD ────────────────────────────────────
    def guardar_token(self, email: str) -> dict:
        try:
            token   = self._generar_token()
            expira  = datetime.now() + timedelta(minutes=30)
            email   = email.strip().lower()

            cur = self.mysql.connection.cursor()

            # Eliminar tokens anteriores del usuario
            cur.execute('DELETE FROM password_resets WHERE email = %s', (email,))

            # Guardar nuevo token
            cur.execute('''
                INSERT INTO password_resets (email, token, expira_en)
                VALUES (%s, %s, %s)
            ''', (email, token, expira))
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'token': token}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}

    # ── Enviar email con link ──────────────────────────────────
    def enviar_email(self, email: str, token: str, base_url: str) -> dict:
        try:
            link = f"{base_url}/recuperar/{token}"
            msg  = Message(
                subject='EcoVision AI — Recupera tu contraseña',
                recipients=[email],
                html=f"""
                <div style="font-family:sans-serif;max-width:500px;margin:0 auto;
                            background:#0a1a12;color:#eaf6ee;padding:2rem;border-radius:12px">
                    <div style="text-align:center;margin-bottom:1.5rem">
                    <h1 style="color:#52b788;font-size:24px;margin:0">EcoVision AI</h1>
                    <p style="color:#7aaa8f;font-size:13px">Recuperación de contraseña</p>
                    </div>
                    <p style="color:#eaf6ee;font-size:14px;margin-bottom:1rem">
                    Hola, recibimos una solicitud para restablecer tu contraseña.
                    </p>
                    <p style="color:#eaf6ee;font-size:14px;margin-bottom:1.5rem">
                    Haz clic en el botón para crear una nueva contraseña.
                    Este enlace expira en <strong style="color:#52b788">30 minutos</strong>.
                    </p>
                    <div style="text-align:center;margin-bottom:1.5rem">
                    <a href="{link}"
                        style="display:inline-block;background:#2d6a4f;color:#d8f3dc;
                                padding:12px 32px;border-radius:8px;text-decoration:none;
                                font-weight:700;font-size:15px">
                        Restablecer contraseña
                    </a>
                  </div>
                  <p style="color:#7aaa8f;font-size:12px;text-align:center">
                    Si no solicitaste esto, ignora este mensaje.
                  </p>
                  <hr style="border-color:rgba(82,183,136,0.2);margin:1rem 0">
                  <p style="color:#7aaa8f;font-size:11px;text-align:center">
                    EcoVision AI © 2024 — Proyecto universitario
                  </p>
                </div>
                """
            )
            self.mail.send(msg)
            return {'ok': True}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}

    # ── Verificar token ────────────────────────────────────────
    def verificar_token(self, token: str) -> dict:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT email, expira_en FROM password_resets
                WHERE token = %s
            ''', (token,))
            row = cur.fetchone()
            cur.close()

            if not row:
                return {'ok': False, 'msg': 'Enlace inválido'}

            email    = row['expira_en'] if isinstance(row, dict) else row[1]
            expira   = row['expira_en'] if isinstance(row, dict) else row[1]
            email    = row['email']     if isinstance(row, dict) else row[0]

            if datetime.now() > expira:
                return {'ok': False, 'msg': 'El enlace ha expirado. Solicita uno nuevo.'}

            return {'ok': True, 'email': email}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}

    # ── Cambiar contraseña ─────────────────────────────────────
    def cambiar_password(self, token: str, nueva: str, confirmar: str) -> dict:
        from werkzeug.security import generate_password_hash

        if len(nueva) < 8:
            return {'ok': False, 'msg': 'La contraseña debe tener mínimo 8 caracteres'}
        if nueva != confirmar:
            return {'ok': False, 'msg': 'Las contraseñas no coinciden'}

        verificacion = self.verificar_token(token)
        if not verificacion['ok']:
            return verificacion

        try:
            email   = verificacion['email']
            hash_pw = generate_password_hash(nueva)
            cur     = self.mysql.connection.cursor()
            cur.execute('UPDATE usuarios SET password = %s WHERE email = %s',
                        (hash_pw, email))
            cur.execute('DELETE FROM password_resets WHERE email = %s', (email,))
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': '¡Contraseña actualizada! Ya puedes iniciar sesión.'}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}