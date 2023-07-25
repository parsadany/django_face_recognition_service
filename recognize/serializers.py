from recognize.models import Profile, KnownImage

from rest_framework import serializers

class ProfileOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class KnownImageOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnownImage
        fields = '__all__'


class NestedKnownImageSerializer(serializers.ModelSerializer):
    profile = ProfileOnlySerializer()
    class Meta:
        model = KnownImage
        fields = '__all__'


class NestedProfileSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = '__all__'

    def get_images(self, obj):
        return KnownImageOnlySerializer(KnownImage.objects.filter(profile=obj), many=True).data

class CheckFaceSerializer(serializers.Serializer):
    matching_id = serializers.IntegerField(required=True)
    image = serializers.URLField(required=True)
    is_matched = serializers.BooleanField(required=False, read_only=True)
    result = serializers.JSONField(required=False, read_only=True)
