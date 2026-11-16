from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q , Sum
from django.db import transaction
from django.utils import timezone

from datetime import timedelta

from rest_framework import status
from rest_framework.generics import (CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView,
                                     DestroyAPIView, get_object_or_404)
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from accounts.permissions import IsOrganizer , IsEventOrganizer ,IsTicketTypeOrganizer
from accounts.models import User

from .models import Event, TicketType, Order , OrderItem
from .serializers import (EventSerializer, EventFilterSerializer, TicketTypeSerializer,
                          OrderCreateSerializer,OrderSerializer)
from .filters import EventFilter

from drf_spectacular.utils import extend_schema

@extend_schema(    summary='Create a new event',
    description='Creates an event for the authenticated organizer.',
    tags=['Events'],
    request=EventSerializer,
    responses={201: EventSerializer}
        )

class EventCreateApiView(CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated,IsOrganizer]

    def perform_create(self, serializer):
        serializer.save(organizer = self.request.user)

class EventListApiView(ListAPIView):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilter

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == User.Role.ORGANIZER:
            queryset = Event.objects.filter(
             Q(status = Event.Status.PUBLISHED) |(
             Q(organizer = self.request.user) &
             Q(status = Event.Status.DRAFT)
             )
            )

        elif self.request.user.is_authenticated and self.request.user.role == User.Role.CUSTOMER:
            queryset = Event.objects.filter(status = Event.Status.PUBLISHED)

        elif self.request.user.is_anonymous:
            queryset = Event.objects.filter(status = Event.Status.PUBLISHED)



        else:
            queryset = Event.objects.none()

        return queryset

class EventDetailApiView(RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated :
            if user.role == User.Role.ORGANIZER:
                queryset = Event.objects.filter(
                Q(status = Event.Status.PUBLISHED) |(
                    Q(organizer = user ,status = Event.Status.DRAFT)
                )
            )

            elif user.role == User.Role.CUSTOMER:
                queryset = Event.objects.filter(status = Event.Status.PUBLISHED)

            else:
                queryset = Event.objects.none()
        else:
            queryset = Event.objects.filter(
                status=Event.Status.PUBLISHED
            )

        return queryset

class EventUpdateApiView(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated,IsOrganizer,IsEventOrganizer]

class EventDeleteApiView(DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated,IsOrganizer,IsEventOrganizer]

class EventPublishApiView(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated,IsOrganizer,IsEventOrganizer]

    def update(self, request, *args, **kwargs):
        event = self.get_object()

        if event.status != Event.Status.DRAFT:
            return Response({'detail':'only draft events can be published'},status=status.HTTP_404_NOT_FOUND)

        event.status = Event.Status.PUBLISHED
        event.save(update_fields=['status'])
        return Response({'detail':'event published successfully'},status=status.HTTP_200_OK)
        # Create your views here.

class TicketTypeCreateApiView(CreateAPIView):
    serializer_class = TicketTypeSerializer
    permission_classes = [IsAuthenticated,IsOrganizer]

    def perform_create(self, serializer):
        event_id = self.request.data.get('event')

        event = get_object_or_404(Event,id=event_id,organizer=self.request.user)

        serializer.save(event=event)

class TicketTypeListApiView(ListAPIView):
    serializer_class = TicketTypeSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']

        return TicketType.objects.filter(event_id=event_id,
                                         event__status = Event.Status.PUBLISHED)

class TicketTypeUpdateApiView(UpdateAPIView):
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer
    permission_classes = [IsAuthenticated,IsOrganizer,IsTicketTypeOrganizer]

class TicketTypeDeleteApiView(DestroyAPIView):
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer
    permission_classes = [IsAuthenticated,IsOrganizer,IsTicketTypeOrganizer]

class OrderCreateApiView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket_type = serializer.validated_data['ticket_type']
        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            ticket_type = TicketType.objects.select_for_update().select_related('event').get(pk=ticket_type.pk)

            if ticket_type.event.status != Event.Status.PUBLISHED:
                return Response(
                    {'detail': 'tickets are available only fot published events'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Order.objects.filter(
                items__ticket_type=ticket_type,
                status=Order.Status.PENDING,
                expires_at__lte=timezone.now()
            ).update(status=Order.Status.EXPIRED)

            sold_quantity = OrderItem.objects.filter(
                ticket_type=ticket_type).filter(
                Q(order__status=Order.Status.PAID) |
                Q(order__status=Order.Status.PENDING
                  ,order__expires_at__gt=timezone.now())
            ).aggregate(total=Sum('quantity'))['total'] or 0

            remaining_capacity = ticket_type.capacity - sold_quantity

            if quantity > remaining_capacity:
                return Response(
                    {'detail': 'not enough tickets available'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order = Order.objects.create(
                customer=request.user,
                expires_at = timezone.now() + timedelta(minutes=1)
            )

            OrderItem.objects.create(
                order=order,
                ticket_type=ticket_type,
                quantity=quantity,
                price=ticket_type.price
            )
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

class MyOrderListApiView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            customer = self.request.user
        ).prefetch_related('items__ticket_type').order_by('-created_at')

class OrderCancelApiView(APIView):
        permission_classes = [IsAuthenticated]

        def post(self,request,pk):
            with transaction.atomic():
                order = get_object_or_404(
                    Order.objects.select_for_update(),
                    pk=pk,#fargh in kha va khat bala chie
                    customer=self.request.user
                )

                if order.status != Order.Status.PENDING:
                    return Response(
                        {'detail':'only pending orders can be canceled'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if order.expires_at and order.expires_at <= timezone.now():
                    order.status = Order.Status.EXPIRED
                    order.save(update_fields=['status','updated_at'])

                    return Response(
                        {'detail':'this order has expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                order.status = Order.Status.CANCELED
                order.save(update_fields=['status','updated_at'])

            return Response(
                {'detail':'Order canceled successfully'},
                status=status.HTTP_200_OK
            )

class OrderPayApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,pk):
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(),
                pk=pk,
                customer = self.request.user
            )

            if order.status != Order.Status.PENDING:
                return Response(
                    {'detail':'only pending orders can be paid'},
                    status = status.HTTP_400_BAD_REQUEST
                )
            if order.expires_at and order.expires_at <= timezone.now():
                order.status = Order.Status.EXPIRED
                order.save(update_fields=['status','updated_at'])
                return Response(
                    {'detail':'this order has expired'},
                    status = status.HTTP_400_BAD_REQUEST
                )

            order.status = Order.Status.PAID
            order.save(update_fields=['status','updated_at'])

        return Response(
            {'detail':'order paid'},
            status=status.HTTP_200_OK
        )

class OrderDetailApiView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            customer = self.request.user
        ).prefetch_related('items__ticket_type')







