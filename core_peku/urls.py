from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('user', views.UserViewSet, basename='user')
router.register('transaction', views.TransactionViewSet, basename='transaction')
router.register('category', views.CategoryViewSet, basename='category')
router.register('budget', views.BudgetViewSet, basename='budget')
router.register('saving_goal', views.SavingGoalViewSet, basename='saving_goal')


urlpatterns = [
    path('api/', include(router.urls)),
]