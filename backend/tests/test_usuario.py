def test_perfil_usuario_tiene_email_correcto(fixture_user_lector):
    assert fixture_user_lector["email"] == "lector@newsradar.es"
