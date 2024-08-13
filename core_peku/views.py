# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import mixins, viewsets, filters, status
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny,BasePermission,SAFE_METHODS


from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction, Category, Budget, SavingGoal, User
from .serializers import UserSerializer, CategorySerializer, TransactionSerializer, BudgetSerializer, SavingGoalSerializer
from rest_framework.authentication import TokenAuthentication

import logging

logger = logging.getLogger(__name__)
# class BasicMixView(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes      = [AllowAny]


# class ListPagination(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 20
#     permission_classes      = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer



class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    # authentication_classes = [TokenAuthentication]  # Assicurati di avere questo se usi Token Authentication
    # permission_classes = [IsAuthenticated]  
    
    @action(detail=False, methods=['get'])
    def monthly_expenses(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        logger.debug(f"User Type: {type(request.user)}")
        logger.debug(f"User: {request.user}")
        if not year or not month:
            return Response({"error": "Year and month are required parameters."}, status=status.HTTP_400_BAD_REQUEST)
# user_id=request.user.id, momentanemannte rimosso per test
        transactions = self.queryset.filter( date__year=year, date__month=month)
        expenses_by_category = transactions.values('category__name').annotate(total=Sum('amount'))

        return Response(expenses_by_category, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def transaction_history(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "Start date and end date are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        transactions = self.queryset.filter(user=request.user, date__range=[start_date, end_date])
        serializer = self.get_serializer(transactions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class SavingGoalViewSet(viewsets.ModelViewSet):
    queryset = SavingGoal.objects.all()
    serializer_class = SavingGoalSerializer

    @action(detail=False, methods=['get'])
    def progress(self, request):
        saving_goals = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(saving_goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
