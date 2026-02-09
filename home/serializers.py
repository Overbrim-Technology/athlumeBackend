from rest_framework import serializers
from .models import Highlight


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = ['id', 'title', 'body', 'image', 'url', 'created_by', 'created_at', 'published']