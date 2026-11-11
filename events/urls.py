from django.urls import path
from .views import (EventCreateApiView , EventListApiView , EventDetailApiView , EventUpdateApiView,
                    EventDeleteApiView,EventPublishApiView,TicketTypeCreateApiView,TicketTypeListApiView,
                    TicketTypeUpdateApiView,TicketTypeDeleteApiView,OrderCreateApiView,MyOrderListApiView,
                    OrderCancelApiView,OrderPayApiView,OrderDetailApiView)

urlpatterns = [
    path('',EventCreateApiView.as_view(),name='event-create'),
    path('list/',EventListApiView.as_view(),name='event-list'),
    path('<int:pk>/',EventDetailApiView.as_view(),name='event-detail'),
    path('<int:pk>/update/',EventUpdateApiView.as_view(),name='event-update'),
    path('<int:pk>/delete/',EventDeleteApiView.as_view(),name='event-delete'),
    path('<int:pk>/publish/',EventPublishApiView.as_view(),name='event-publish'),

    path('ticket-types/create/',TicketTypeCreateApiView.as_view(),name='ticket-type-create'),
    path('<int:event_id>/ticket-types/',TicketTypeListApiView.as_view(),name='ticket-type-list'),
    path('ticket-types/<int:pk>/update/',TicketTypeUpdateApiView.as_view(),name='ticket-type-update'),
    path('ticket-types/<int:pk>/delete/',TicketTypeDeleteApiView.as_view(),name='ticket-type-delete'),

    path('order/', OrderCreateApiView.as_view(), name='order-create'),
    path('my-orders/', MyOrderListApiView.as_view(), name='my-orders'),
    path('orders/<int:pk>/cancel/', OrderCancelApiView.as_view(), name='order-cancel'),
    path('orders/<int:pk>/pay/', OrderPayApiView.as_view(), name='order-pay'),
    path('orders/<int:pk>/', OrderDetailApiView.as_view(), name='order-detail'),

]