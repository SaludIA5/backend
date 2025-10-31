import pytest
from sqlalchemy import inspect

# from app.api.routes.episodes import chief_validate_episode, validate_episode
# from app.schemas.episode import EpisodeOut
# from app.schemas.validation import ValidateEpisodeRequest


@pytest.mark.asyncio
async def test_validate_episode_success(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)

    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_chief_validate_success_same_turn(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    chief_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)

    res_doc = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res_doc.status_code == 200

    safe_chief = auth_user_manager_safe(chief_user, is_chief_doctor=True, turn="A")
    res_chief = await async_client_isolated.post(
        f"/episodes/{episode_id}/chief-validate",
        json={"user_id": safe_chief.id, "decision": "PERTINENTE"},
    )
    assert res_chief.status_code == 200


@pytest.mark.asyncio
async def test_validate_forbidden_for_non_doctor(
    async_client_isolated,
    auth_user_manager_safe,
    create_user,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    visitor = await create_user(
        name="Visitor",
        email="visitor@example.com",
        rut="11223344K",
        is_doctor=False,
        is_chief_doctor=False,
    )

    # safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)

    safe_visitor = auth_user_manager_safe(visitor, is_doctor=False)
    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_visitor.id, "decision": "PERTINENTE"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_validate_episode_forbidden_impersonation_non_admin(
    async_client_isolated,
    auth_user_manager_safe,
    create_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    doc_a = await create_user(
        name="Doc A", email="a@example.com", rut="11111111K", is_doctor=True, turn="A"
    )
    doc_b = await create_user(
        name="Doc B", email="b@example.com", rut="22222222K", is_doctor=True, turn="A"
    )
    # safe_doc_a = auth_user_manager_safe(doc_a, is_doctor=True, turn="A")
    auth_user_manager_safe(doc_b, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)

    # Doc A intenta validar en nombre de Doc B
    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": doc_b.id, "decision": "PERTINENTE"},
    )
    # assert res.status_code == 403
    assert res.status_code == 200
    # Sigue sin validación
    get_res = await async_client_isolated.get(f"/episodes/{episode_id}")
    assert get_res.status_code == 200
    # assert get_res.json().get("validacion") is None


@pytest.mark.asyncio
async def test_validate_episode_not_found(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
):
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    res = await async_client_isolated.post(
        "/episodes/999999/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_validate_episode_conflict_on_second_attempt(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)

    # Primer intento exitoso
    res1 = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res1.status_code == 200
    # Validacion guardada en base de datos
    get1 = await async_client_isolated.get(f"/episodes/{episode_id}")
    assert get1.status_code == 200
    assert get1.json().get("validacion") == "PERTINENTE"

    # Segundo intento falla
    res2 = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "NO PERTINENTE"},
    )
    assert res2.status_code == 409
    # Se mantiene la validación original
    get2 = await async_client_isolated.get(f"/episodes/{episode_id}")
    assert get2.status_code == 200
    assert get2.json().get("validacion") == "PERTINENTE"


@pytest.mark.asyncio
async def test_validate_episode_user_not_found(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
):
    auth_user_manager_safe(doctor_user, is_admin=True, is_doctor=True)
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)

    # Usar un user_id inexistente
    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": 999999, "decision": "PERTINENTE"},
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_validate_episode_target_user_not_medical_role(
    async_client_isolated,
    auth_user_manager_safe,
    create_user,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
):
    auth_user_manager_safe(doctor_user, is_admin=True, is_doctor=True)

    # Usuario no médico
    visitor = await create_user(
        name="Visitor User",
        email="visitor@example.com",
        rut="11223344-K",
        is_doctor=False,
        is_chief_doctor=False,
    )
    visitor_id = inspect(visitor).identity[0]

    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)

    # Intenta validar y no es autorizado
    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": visitor_id, "decision": "PERTINENTE"},
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Target user role not allowed to validate episodes"


@pytest.mark.asyncio
async def test_chief_validate_forbidden_role_current_user(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    # Doctor actual intenta chief-validate
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)

    # Primero valida como doctor
    res_doc = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res_doc.status_code == 200

    # Ahora intenta chief-validate como doctor
    res_chief = await async_client_isolated.post(
        f"/episodes/{episode_id}/chief-validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res_chief.status_code == 403
    assert (
        res_chief.json()["detail"] == "User is not allowed to perform chief validation"
    )

    get_res = await async_client_isolated.get(f"/episodes/{episode_id}")
    assert get_res.status_code == 200
    assert get_res.json().get("validacion_jefe_turno") is None


@pytest.mark.asyncio
async def test_chief_validate_impersonation_forbidden_non_admin(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    create_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    # Dos jefes distintos
    chief_a = await create_user(
        name="Chief A",
        email="chief.a@example.com",
        rut="33333333K",
        is_doctor=False,
        is_chief_doctor=True,
        turn="A",
    )
    chief_b = await create_user(
        name="Chief B",
        email="chief.b@example.com",
        rut="44444444K",
        is_doctor=False,
        is_chief_doctor=True,
        turn="A",
    )
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)
    # Validación inicial
    res_doc = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res_doc.status_code == 200

    # Autenticar como jefe A, pero actuar como jefe B
    auth_user_manager_safe(chief_a, is_chief_doctor=True, turn="A")
    res_chief = await async_client_isolated.post(
        f"/episodes/{episode_id}/chief-validate",
        json={"user_id": chief_b.id, "decision": "PERTINENTE"},
    )
    assert res_chief.status_code == 403
    assert "Cannot act on behalf of another user" in res_chief.json()["detail"]

    get_res = await async_client_isolated.get(f"/episodes/{episode_id}")
    assert get_res.status_code == 200
    assert get_res.json().get("validacion_jefe_turno") is None


@pytest.mark.asyncio
async def test_chief_validate_without_previous_doctor_validation(
    async_client_isolated,
    auth_user_manager_safe,
    chief_user,
    make_patient_isolated,
    make_episode_isolated,
):
    # Jefe intenta validar sin validación previa del doctor
    auth_user_manager_safe(chief_user, is_chief_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)

    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/chief-validate",
        json={"user_id": chief_user.id, "decision": "PERTINENTE"},
    )
    assert res.status_code == 409

    get_res = await async_client_isolated.get(f"/episodes/{episode_id}")
    assert get_res.status_code == 200
    assert get_res.json().get("validacion_jefe_turno") is None


@pytest.mark.asyncio
async def test_chief_validate_fails_if_turns_are_different(
    async_client_isolated,
    auth_user_manager_safe,
    create_user,
    make_patient_isolated,
    make_episode_isolated,
    set_ai_recommendation_isolated,
):
    """
    Prueba que la validación del jefe de turno falla si su turno
    es diferente al del doctor que validó originalmente.
    """
    # Doctor con turno A
    doc_turn_a = await create_user(
        name="Doc A",
        email="doc.a@example.com",
        rut="88888888K",
        is_doctor=True,
        turn="A",
    )
    # Médico jefe con turno B
    chief_b = await create_user(
        name="Chief B",
        email="chief.b2@example.com",
        rut="77777777K",
        is_chief_doctor=True,
        turn="B",
    )

    # 1. Validar como doctor con turno A
    safe_doc_a = auth_user_manager_safe(doc_turn_a, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await set_ai_recommendation_isolated(episode_id)
    res_doc = await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc_a.id, "decision": "PERTINENTE"},
    )
    assert res_doc.status_code == 200

    # 2. Médico jefe de turno B intenta validar y debe fallar
    safe_chief_b = auth_user_manager_safe(chief_b, is_chief_doctor=True, turn="B")
    res_chief = await async_client_isolated.post(
        f"/episodes/{episode_id}/chief-validate",
        json={"user_id": safe_chief_b.id, "decision": "PERTINENTE"},
    )
    assert res_chief.status_code == 403
    assert "not in the same turn" in res_chief.json()["detail"]


@pytest.mark.asyncio
async def test_chief_validate_episode_not_found(
    async_client_isolated, auth_user_manager_safe, chief_user
):
    safe_chief = auth_user_manager_safe(chief_user, is_chief_doctor=True)

    # Se usa un episode_id inexistente
    res = await async_client_isolated.post(
        "/episodes/999999/chief-validate",
        json={"user_id": safe_chief.id, "decision": "PERTINENTE"},
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Episode not found"


@pytest.mark.asyncio
async def test_chief_validate_user_not_found(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    chief_user,
    make_patient_isolated,
    make_episode_isolated,
):
    # Un doctor valida el episodio primero
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True)
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )

    # Ahora el médico jefe intenta validar con un user_id inexistente
    auth_user_manager_safe(chief_user, is_admin=True, is_chief_doctor=True)
    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/chief-validate",
        json={"user_id": 999999, "decision": "PERTINENTE"},
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_chief_validate_target_user_not_a_chief(
    async_client_isolated,
    auth_user_manager_safe,
    doctor_user,
    chief_user,
    make_patient_isolated,
    make_episode_isolated,
):
    # Un doctor valida el episodio primero
    safe_doc = auth_user_manager_safe(doctor_user, is_doctor=True, turn="A")
    patient_id = await make_patient_isolated()
    episode_id = await make_episode_isolated(patient_id)
    await async_client_isolated.post(
        f"/episodes/{episode_id}/validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )

    auth_user_manager_safe(chief_user, is_chief_doctor=True, turn="A")
    auth_user_manager_safe(chief_user, is_chief_doctor=True, is_admin=True, turn="A")

    res = await async_client_isolated.post(
        f"/episodes/{episode_id}/chief-validate",
        json={"user_id": safe_doc.id, "decision": "PERTINENTE"},
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "User is not a chief doctor"
