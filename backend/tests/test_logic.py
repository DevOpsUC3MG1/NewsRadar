def test_alerta_pertenece_a_gestor(fixture_alerta_base, fixture_user_gestor):
    # Comprobamos que el ID del creador de la alerta coincide con nuestro gestor
    assert fixture_alerta_base["user_id"] == fixture_user_gestor["id"]


def test_noticia_tiene_categoria_valida(fixture_noticia_rss):
    # Verificamos que la noticia tiene una categoría IPTC asignada
    categorias_validas = ["Economía", "Política", "Deportes", "Cultura"]
    assert fixture_noticia_rss["category_iptc"] in categorias_validas
