
@app.route('/auth/oidc/login')
def oidc_login():
    """Redirect user to Authentik for authentication"""
    redirect_uri = url_for('oidc_callback', _external=True)
    return redirect(oidc_provider.get_authorization_url(redirect_uri))

@app.route('/auth/oidc/callback')
def oidc_callback():
    """Handle the callback from Authentik"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Exchange code for tokens
    tokens = oidc_provider.exchange_code(code, state)
    
    # Create session and return to frontend
    session['tokens'] = tokens
    return redirect('/dashboard')

@app.route('/auth/oidc/user')
@require_authentication
def get_user():
    """Return current user information from Authentik"""
    tokens = session.get('tokens')
    user_info = oidc_provider.get_userinfo(tokens['access_token'])
    return jsonify(user_info)

@app.route('/auth/oidc/logout', methods=['POST'])
@require_authentication
def logout():
    """Logout from Authentik and clear local session"""
    tokens = session.get('tokens')
    oidc_provider.logout(tokens.get('id_token'))
    session.clear()
    return jsonify({"success": True})