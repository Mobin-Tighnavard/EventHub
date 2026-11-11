from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework import serializers
from .models import Event, TicketType, OrderItem, Order


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['organizer', 'status']

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = '__all__'
        read_only_fields = ['event']

    def validate_capacity(self,value):
        ticket_type = self.instance

        if ticket_type is None:
            return value

        occupied_quantity = OrderItem.objects.filter(
            ticket_type = ticket_type
        ).filter(
            Q(order__status = Order.Status.PAID) |
            Q(order__status = Order.Status.PENDING,
              order__expires_at__gt = timezone.now())
        ).aggregate(total=Sum('quantity'))['total'] or 0

        if value < occupied_quantity:
            raise serializers.ValidationError('capacity can not be lower than sold or reserved tickets')
        return value



class EventFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Event.Status.choices,required=False)
    event_date = serializers.DateField(required=False)
    ordering = serializers.ChoiceField(choices=['event_date','-event_date','title','-title'],
                                       required=False)
    location = serializers.CharField(required=False,allow_blank=False,max_length=200)
    search = serializers.CharField(required=False,allow_blank=False,max_length=100)
    min_price = serializers.IntegerField(min_value=0,required=False)
    max_price = serializers.IntegerField(min_value=0,required=False)


    def validate(self,attrs):
        min_price = attrs.get('min_price')
        max_price = attrs.get('max_price')

        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise serializers.ValidationError('min_price must be less than max_price')

        return attrs

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','ticket_type','quantity','price']
        read_only_fields = ['id','price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = ['id','customer', 'status' , 'created_at' , 'items']
        read_only_fields = ['id','customer', 'status', 'created_at' , 'items' ]

class OrderCreateSerializer(serializers.Serializer):
    ticket_type = serializers.PrimaryKeyRelatedField(
        queryset = TicketType.objects.all()
    )
    quantity = serializers.IntegerField(min_value = 1)