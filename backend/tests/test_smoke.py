def test_system_up_and_running(client):
    """Test crítico de despliegue: ¿responde la API?"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
