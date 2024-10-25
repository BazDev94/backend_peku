# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import mixins, viewsets, filters, status
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny,BasePermission,SAFE_METHODS

from decimal import Decimal

from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction, Category, Budget, SavingGoal, User, Income
from .serializers import UserSerializer, CategorySerializer, TransactionSerializer, BudgetSerializer, SavingGoalSerializer, IncomeSerializer
from rest_framework.authentication import TokenAuthentication
from django.db.models import Sum, F

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

    def get_queryset(self):
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        user = self.request.query_params.get('user')
        if year and month and user:
            return Budget.objects.filter(user=user, year=year, month=month)
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def allocate_monthly_income(self, request):
        # Recupera i dati dal corpo della richiesta
        year = request.data.get('year')
        month = request.data.get('month')
        user_id = request.data.get('user')
        
        # Verifica che i dati obbligatori siano presenti
        if not year or not month or not user_id:
            return Response({"error": "Year, month, and user are required parameters."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Trova l'utente con l'ID fornito
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Year: {year}, Month: {month}, User: {user_id}")

        # Calcola il reddito totale
        total_income = Income.objects.filter(
            user = user,
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Se non esiste reddito per il mese specificato
        if total_income == 0:
            print(f"Total Income: {total_income}")
            return Response({"error": "No income found for the specified month."}, status=status.HTTP_400_BAD_REQUEST)

        # Percentuali di allocazione
        necessities_percentage = Decimal('0.7')
        entertainment_percentage = Decimal('0.2')
        savings_percentage = Decimal('0.1')

        # Calcolo degli importi allocati
        necessities_amount = total_income * necessities_percentage
        entertainment_amount = total_income * entertainment_percentage
        savings_amount = total_income * savings_percentage

        # Recupera o crea le categorie
        necessities_category, _ = Category.objects.get_or_create(name='Necessities')
        entertainment_category, _ = Category.objects.get_or_create(name='Entertainment')
        savings_category, _ = Category.objects.get_or_create(name='Savings')

        # Verifica se il budget esiste già per l'utente, categoria, anno e mese specifici
        existing_budget_necessities = Budget.objects.filter(
            user=user,
            category=necessities_category,
            year=year,
            month=month
        ).first()

        if existing_budget_necessities:
            return Response({"message": "Budget already allocated for this month."}, status=status.HTTP_202_ACCEPTED)

        # Crea o aggiorna i budget per ciascuna categoria
        Budget.objects.create(
            user=user,  # Passa l'istanza dell'utente, non l'ID
            category=necessities_category,
            allocated_amount=necessities_amount,
            spent_amount=0,
            remaining_amount=necessities_amount,
            year=year,
            month=month
        )

        Budget.objects.create(
            user=user,  # Passa l'istanza dell'utente, non l'ID
            category=entertainment_category,
            allocated_amount=entertainment_amount,
            spent_amount=0,
            remaining_amount=entertainment_amount,
            year=year,
            month=month
        )

        Budget.objects.create(
            user=user,  # Passa l'istanza dell'utente, non l'ID
            category=savings_category,
            allocated_amount=savings_amount,
            spent_amount=0,
            remaining_amount=savings_amount,
            year=year,
            month=month
        )

        return Response({"message": "Budgets allocated successfully for the month."}, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['post'])
    # def allocate_monthly_income(self, request):
    #     # Recupera l'income totale per il mese specificato
    #     year = request.data.get('year')
    #     month = request.data.get('month')
    #     user = request.data.get('user')
    #     if not year or not month:
    #         return Response({"error": "Year and month are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

    #     total_income = Income.objects.filter(
    #         user=user,
    #         date__year=year,
    #         date__month=month
    #     ).aggregate(total=Sum('amount'))['total'] or 0

    #     if total_income == 0:
    #         return Response({"error": "No income found for the specified month."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Definisci le percentuali per ciascuna categoria
    #     necessities_percentage = Decimal('0.7')
    #     entertainment_percentage = Decimal('0.2')
    #     savings_percentage = Decimal('0.1')

    #     # Calcola gli importi allocati per ciascuna categoria
    #     necessities_amount = total_income * necessities_percentage
    #     entertainment_amount = total_income * entertainment_percentage
    #     savings_amount = total_income * savings_percentage

    #     # Trova o crea le categorie corrispondenti
    #     necessities_category, _ = Category.objects.get_or_create(name='Necessities')
    #     entertainment_category, _ = Category.objects.get_or_create(name='Entertainment')
    #     savings_category, _ = Category.objects.get_or_create(name='Savings')

    #     # Crea o aggiorna i budget per ciascuna categoria
    #     Budget.objects.update_or_create(
    #         user=user,
    #         category=necessities_category,
    #         defaults={'allocated_amount': necessities_amount, 'spent_amount': 0, 'remaining_amount': necessities_amount}
    #     )

    #     Budget.objects.update_or_create(
    #         user=user,
    #         category=entertainment_category,
    #         defaults={'allocated_amount': entertainment_amount, 'spent_amount': 0, 'remaining_amount': entertainment_amount}
    #     )

    #     Budget.objects.update_or_create(
    #         user=user,
    #         category=savings_category,
    #         defaults={'allocated_amount': savings_amount, 'spent_amount': 0, 'remaining_amount': savings_amount}
    #     )

    #     return Response({"message": "Budgets allocated successfully for the month."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def update_remaining(self, request):
        # Calcola il remaining_amount per ogni categoria di budget
        budgets = self.queryset.filter(user=1)
        for budget in budgets:
            spent_amount = Transaction.objects.filter(
                user=1,
                category=budget.category
            ).aggregate(total_spent=Sum('amount'))['total_spent'] or 0
            budget.spent_amount = spent_amount
            budget.update_remaining()

        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def budget_summary(self, request):
        # Fornisce una sintesi dello stato del budget
        budgets = self.queryset.filter(user=1)
        summary = budgets.annotate(
            category_name=F('category__name'),
            remaining=F('allocated_amount') - F('spent_amount')
        ).values('category_name', 'allocated_amount', 'spent_amount', 'remaining')

        return Response(summary, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset_monthly_budget(self, request):
        # Resetta il budget mensile per l'utente
        user = request.data.get('user')
        budgets = self.queryset.filter(user=user)
        for budget in budgets:
            budget.spent_amount = 0
            budget.update_remaining()

        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    # authentication_classes = [TokenAuthentication]  # Assicurati di avere questo se usi Token Authentication
    # permission_classes = [IsAuthenticated]  
    
    @action(detail=False, methods=['get'])
    def monthly_expenses(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        user = request.query_params.get('user')

        logger.debug(f"User Type: {type(request.user)}")
        logger.debug(f"User: {request.user}")
        if not year or not month:
            return Response({"error": "Year and month are required parameters."}, status=status.HTTP_400_BAD_REQUEST)
# user_id=request.user.id, momentanemannte rimosso per test
        transactions = self.queryset.filter( date__year=year, date__month=month, user=user)
        expenses_by_category = transactions.values('category__name').annotate(total=Sum('amount'))

        return Response(expenses_by_category, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def transaction_history(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "Start date and end date are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        transactions = self.queryset.filter(user=1, date__range=[start_date, end_date])
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
