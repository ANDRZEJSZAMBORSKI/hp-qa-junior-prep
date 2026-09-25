from lab_fw.reporting import step, attach_text, attach_json

def test_step():
    with step("test step"):
        value = 1 + 1

    assert value == 2

def test_attach_text():
    attach_text("test text", "Hello from test")

def test_attach_json():
    data = {
        "status": 200,
        "user": "john",
    }

    attach_json("response", data)