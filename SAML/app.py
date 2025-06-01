from flask import Flask, redirect, request, session, url_for
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ✅ Ensure correct handling of HTTPS and Host headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


def prepare_flask_request(req):
    return {
        'https': 'on' if req.scheme == 'https' else 'off',
        'http_host': req.host,
        'server_port': req.environ.get('SERVER_PORT'),
        'script_name': req.path,
        'get_data': req.args.copy(),
        'post_data': req.form.copy()
    }


@app.route('/')
def index():
    print(f"this is session data: {session}")
    if 'samlUserdata' in session:
        user_name = session['samlUserdata'].get('name', ['User'])[0]
        return f"""
        Hello, {user_name}!<br>
        <a href="/logout">Logout</a>
        <p> this is session data: {session['samlUserdata']}</p>
        <p> this is session data: {session}</p>
        """
    return 'You are not logged in. <a href="/login">Login with SAML</a>'


@app.route('/login')
def login():
    req = prepare_flask_request(request)
    auth = OneLogin_Saml2_Auth(req, custom_base_path="saml")
    return redirect(auth.login())


@app.route('/acs', methods=['POST'])
def acs():
    req = prepare_flask_request(request)
    auth = OneLogin_Saml2_Auth(req, custom_base_path="saml")
    auth.process_response()
    if not auth.get_errors():
        session['samlUserdata'] = auth.get_attributes()
    return redirect('/')


@app.route('/metadata')
def metadata():
    req = prepare_flask_request(request)
    auth = OneLogin_Saml2_Auth(req, custom_base_path="saml")
    settings = auth.get_settings()

    # ✅ Set correct ACS URL and Entity ID
    sp_data = settings.get_sp_data()
    sp_data['assertionConsumerService']['url'] = 'http://localhost:5000/acs'  # ✅ Fixed
    sp_data['entityId'] = 'https://localhost:5000/metadata'
    settings.set_sp_data(sp_data)

    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    if len(errors) > 0:
        return f'Metadata validation error: {errors}', 500
    return metadata, 200, {'Content-Type': 'text/xml'}


@app.route('/logout')
def logout():
    req = prepare_flask_request(request)
    auth = OneLogin_Saml2_Auth(req, custom_base_path="saml")
    return redirect(auth.logout())


@app.route('/sls')
def sls():
    req = prepare_flask_request(request)
    auth = OneLogin_Saml2_Auth(req, custom_base_path="saml")
    dscb = lambda: session.clear()
    url = auth.process_slo(delete_session_cb=dscb)
    errors = auth.get_errors()
    if errors:
        return f"Logout failed: {', '.join(errors)}"
    else:
        return redirect(url or '/')


if __name__ == '__main__':
    app.run(debug=True)
