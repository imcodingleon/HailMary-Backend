from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.infrastructure.orm.payment_orm import PaymentORM


class PaymentMapper:
    @staticmethod
    def to_orm(entity: Payment) -> PaymentORM:
        return PaymentORM(
            id=entity.id,
            payment_key=entity.payment_key,
            order_id=entity.order_id,
            user_id=entity.user_id,
            character=entity.character,
            amount=entity.amount,
            status=entity.status,
            customer_email=entity.customer_email,
            approved_at=entity.approved_at,
            expires_at=entity.expires_at,
            method=entity.method,
            easy_pay_provider=entity.easy_pay_provider,
            card_issuer_code=entity.card_issuer_code,
            bank_code=entity.bank_code,
        )

    @staticmethod
    def to_entity(orm: PaymentORM) -> Payment:
        return Payment(
            id=orm.id,
            payment_key=orm.payment_key,
            order_id=orm.order_id,
            user_id=orm.user_id,
            character=orm.character,
            amount=orm.amount,
            status=orm.status,
            customer_email=orm.customer_email,
            approved_at=orm.approved_at,
            expires_at=orm.expires_at,
            method=orm.method,
            easy_pay_provider=orm.easy_pay_provider,
            card_issuer_code=orm.card_issuer_code,
            bank_code=orm.bank_code,
        )
