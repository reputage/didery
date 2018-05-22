import falcon

try:
    import simplejson as json
except ImportError:
    import json


def testStaticSinc(client):
    response = client.simulate_get('/')

    exp_result = b'<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>Didery</title>\n' \
                 b'    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">\n    ' \
                 b'<link rel="icon" href="favicon.ico" type="image/x-icon">\n    ' \
                 b'<link href="https://fonts.googleapis.com/css?family=Pacifico" rel="stylesheet">\n    ' \
                 b'<link rel="stylesheet" href="node_modules/semantic-ui/dist/semantic.min.css">\n    ' \
                 b'<link rel="stylesheet" href="css/dashboard.css">\n</head>\n<body>\n    <!--<div class="item">\n' \
                 b'        <a class="ui centered image small" href="/">\n            ' \
                 b'<img src="images/logo-extended.png">\n        </a>\n    </div>-->\n    ' \
                 b'<div class="ui bottom attached segment">\n        <p></p>\n    </div>\n    ' \
                 b'<script src="node_modules/jquery/dist/jquery.min.js"></script>\n    ' \
                 b'<script src="node_modules/semantic-ui/dist/semantic.min.js"></script>\n    ' \
                 b'<script src="node_modules/mithril/mithril.min.js"></script>\n    ' \
                 b'<script src="transcrypt/__javascript__/main.js"></script>\n    ' \
                 b'<!--<script>\n        $(".tab").click(function() {\n            $(".tab").removeClass("active");\n' \
                 b'            $(this).addClass("active");\n        })\n    </script>-->\n</body>\n</html>'

    assert response.content == exp_result
    assert response.status == falcon.HTTP_200

    response = client.simulate_get('/static')

    assert response.content == exp_result
    assert response.status == falcon.HTTP_200

    response = client.simulate_get('/invalid')

    assert json.loads(response.content)['title'] == "Missing Resource"
    assert response.status == falcon.HTTP_404
