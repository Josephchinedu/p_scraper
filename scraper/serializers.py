from django.core.exceptions import ValidationError
from rest_framework import serializers

from scraper.models import ScrapedData


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, min_length=4)
    email = serializers.EmailField(max_length=255, min_length=4)
    first_name = serializers.CharField(max_length=255, min_length=4)
    last_name = serializers.CharField(max_length=255, min_length=4)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, min_length=4)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)


class WebScrapperSerializer(serializers.Serializer):
    url = serializers.URLField()
    keywords = serializers.CharField()



class ScrapeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedData 
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "updated_at"]
