import json

from ..authentication.renderers import UserJSONRenderer


class ProfileJSONRenderer(UserJSONRenderer):
    """
    used to render data as required in our readme
    """
    def render(self, data, media_type=None, renderer_context=None):
        """
        overide UserJSONRenderer to render our data under the "profile" namespace.
        """
        return json.dumps({
            'profile': data
        })
        