from tina4_python import get, post
from tina4_python.Swagger import description, example, secure, params


@get("/test/session")
async def test_session(request, response):
    request.session.set("me", "myself 1000 111")

    return response("Done")


@get("/test/session/set")
async def test_session_set(request, response):
    html = request.session.get("me")

    return response(html)


@get("/test/session/unset")
async def test_session_unset(request, response):
    html = request.session.unset("me")

    return response(html)


@post("/test/variables")
@description("A test for variables")
@example('{"id": 100, "first_name": "Andre", "last_name": "van Zuydam"}')
@params(["hello","one"])
@secure()
async def test_session_unset(request, response):
    html = request.body

    return response(html)
