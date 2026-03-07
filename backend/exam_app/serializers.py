from rest_framework import serializers

from .models import Review





class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'is_deleted': {'read_only': True},
            'deleted_at': {'read_only': True},
            'user': {'read_only': True}
        }
