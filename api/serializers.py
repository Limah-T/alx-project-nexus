from rest_framework import serializers
from django.core.validators import MinLengthValidator, MaxValueValidator
from .models import Category, Color, Product, Order

class CategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    name = serializers.CharField(validators=[MinLengthValidator(2)],
                                max_length=200)

    def validate_name(self, value):
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(f"Category name: {value} already exist.")
        return value

    def create(self, validated_data):
        # Handle bulk create
        if isinstance(validated_data, list):
            categories = [Category(**item) for item in validated_data]
            return Category.objects.bulk_create(categories)
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):       
        name = validated_data["name"]       
        instance.name = name
        # saves the name before the slug field.
        instance.save()
        instance.slug = instance.create_slug_for_category
        instance.save()
        return instance

class ColorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(validators=[MinLengthValidator(2)],
                                max_length=200)
    
    def validate_name(self, value):
        if Color.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Category name already exist.")
        return value

    def create(self, validated_data):
        if isinstance(validated_data, list):
            category = [Color(**item) for item in validated_data]
            return Color.objects.bulk_create(category) 
        return Color.objects.create(**validated_data)
    
    # def update(self, instance, validated_data):
    #     name = validated_data['name']
    #     if Category.objects.exclude(id=instance.id).filter(name__iexact=name).exists():
    #         raise serializers.ValidationError({"error": "Category name already exist."}
    #             )
    #     return super().update(instance, validated_data)
    
class ProductSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    # category = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    # color = serializers.SerializerMethodField()
    image = serializers.ImageField()
    description = serializers.CharField()
    stock = serializers.IntegerField()
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = serializers.IntegerField(
                        validators=[MinLengthValidator(0), MaxValueValidator(70)],
                        help_text="Discount percentage (0–70).", required=False)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2,
                                               required=False)
    date_added = serializers.DateTimeField(read_only=True)


    
