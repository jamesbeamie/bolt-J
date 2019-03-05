import json

from rest_framework.renderers import JSONRenderer


class LikeDislikeJSONRenderer(JSONRenderer):
    """ Render our data"""
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        errors = data.get('errors', None)

        if errors is not None:
            return super(LikeDislikeJSONRenderer, self).render(data)

        # Finally, we can render our data under the "message" namespace.
        return json.dumps({
            'message': data
        })
