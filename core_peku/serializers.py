from rest_framework import serializers
from .models import Transaction, Category, Budget, SavingGoal, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class SavingGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingGoal
        fields = '__all__'
    