from rest_framework import serializers


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField(read_only=True)
    image = serializers.ImageField()


class SellerShopSerializer(serializers.Serializer):
    name = serializers.CharField(source="business_name")
    slug = serializers.SlugField()
    avatar = serializers.CharField(source="user.avatar")


class SellerSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(read_only=True)
    inn_identification_number = serializers.CharField(max_length=50)
    website_url = serializers.URLField(required=False, allow_null=True)
    phone_number = serializers.CharField(max_length=20)
    business_description = serializers.CharField()

    business_address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)

    bank_name = serializers.CharField(max_length=255)
    bank_bic_number = serializers.CharField(max_length=9)
    bank_account_number = serializers.CharField(max_length=50)
    bank_routing_number = serializers.CharField(max_length=50)

    is_approved = serializers.BooleanField(read_only=True)


class ProductSerializer(serializers.Serializer):
    seller = SellerShopSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    desc = serializers.CharField()
    price_old = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = CategorySerializer()
    in_stock = serializers.IntegerField()
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)


class CreateProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    desc = serializers.CharField()
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_slug = serializers.SlugField()
    in_stock = serializers.IntegerField()
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)
