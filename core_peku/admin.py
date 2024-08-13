from django.contrib import admin
from .models import User, Category, Transaction, Budget, SavingGoal

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(SavingGoal)
