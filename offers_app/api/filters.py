import django_filters
from django.db.models import Min
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend, OrderingFilter

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    creator_id = django_filters.NumberFilter(field_name='user_id')
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_delivery_time = django_filters.NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_min_price(self, queryset, name, value):
        return queryset.filter(details__price__gte=value).distinct()

    def filter_max_delivery_time(self, queryset, name, value):
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()


class OfferQueryParamsValidationBackend(BaseFilterBackend):
    allowed_ordering_fields = {
        'updated_at',
        '-updated_at',
        'created_at',
        '-created_at',
        'min_price',
        '-min_price',
    }

    def filter_queryset(self, request, queryset, view):
        if getattr(view, 'action', None) != 'list':
            return queryset

        creator_id = request.query_params.get('creator_id')
        if creator_id:
            self._parse_int(creator_id)

        min_price = request.query_params.get('min_price')
        if min_price:
            self._parse_float(min_price)

        max_delivery_time = request.query_params.get('max_delivery_time')
        if max_delivery_time:
            self._parse_int(max_delivery_time)

        ordering = request.query_params.get('ordering')
        if ordering and ordering not in self.allowed_ordering_fields:
            raise ValidationError(
                {"error": "Invalid ordering field. Allowed: updated_at, created_at, min_price"}
            )

        page_size = request.query_params.get('page_size')
        if page_size:
            page_size_int = self._parse_int(page_size)
            if page_size_int < 1:
                raise ValidationError({"error": "page_size must be positive"})

        return queryset

    def _parse_int(self, value):
        try:
            return int(value)
        except ValueError as exc:
            raise ValidationError({"error": "Invalid parameter format"}) from exc

    def _parse_float(self, value):
        try:
            return float(value)
        except ValueError as exc:
            raise ValidationError({"error": "Invalid parameter format"}) from exc


class OfferOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if not ordering:
            return queryset

        if len(ordering) == 1 and ordering[0] in {'min_price', '-min_price'}:
            direction = '' if ordering[0] == 'min_price' else '-'
            return queryset.annotate(min_detail_price=Min('details__price')).order_by(
                f'{direction}min_detail_price'
            )

        return super().filter_queryset(request, queryset, view)
