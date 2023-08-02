from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from scraper.models import ScrapedData
from scraper.serializers import (
    LoginSerializer,
    RegisterSerializer,
    ScrapeDataSerializer,
    WebScrapperSerializer,
)
from scraper.utils import CustomPagination, ScraperHelper


# Create your views here.
## --------------- AUTHENTICATION CLASSES
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        password = serializer.validated_data.get("password")

        User = get_user_model()

        # validate the data
        if User.objects.filter(email=email).exists():
            data = {"error": True, "message": "Email already exists"}

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            data = {
                "error": True,
                "message": "Username already exists",
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        user_instance = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
        )

        # handle account verification here

        # handle token generation here
        tokenr = TokenObtainPairSerializer().get_token(user_instance)
        tokena = AccessToken().for_user(user_instance)

        data = {
            "error": False,
            "code": "201",
        }

        data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        User = get_user_model()

        try:
            user_instance = User.objects.get(username=username)
        except User.DoesNotExist:
            data = {"error": True, "message": "incorrect username or password"}

            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if not check_password(password, user_instance.password):
            data = {"error": True, "message": "incorrect username or password"}

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        tokenr = TokenObtainPairSerializer().get_token(user_instance)
        tokena = AccessToken().for_user(user_instance)

        data = {
            "error": False,
            "code": "200",
        }

        data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}
        return Response(data, status=status.HTTP_200_OK)


## --------------- END OF AUTHENTICATION CLASSES


## --------------- WEB SCRAPER CLASS
class WebScraperView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = WebScrapperSerializer

    rate_limit_per_minute = ratelimit(key="user", rate="5/m", method="POST", block=True)

    @method_decorator(rate_limit_per_minute)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data.get("url")
        keywords = serializer.validated_data.get("keywords")

        keywords = keywords.split(",")

        dict_keywords = {i: None for i in keywords}

        # do the scraping here
        web_scraper = ScraperHelper(url=str(url), keywords=dict_keywords)
        if web_scraper.extract_product_info() is None:
            data = {"error": True, "message": "unable to scrape data"}

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        ScrapedData.objects.create(
            user=request.user,
            url=url,
            data=web_scraper.extract_product_info(),
            keywords=keywords,
        )

        data = {
            "error": False,
            "message": "data scraped successfully",
        }

        return Response(data, status=status.HTTP_200_OK)

    def get(self, request):
        data = ScrapedData.objects.filter(user=request.user)
        pagination_class = CustomPagination
        paginator = pagination_class()
        page = paginator.paginate_queryset(data, request)
        serializer = ScrapeDataSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
