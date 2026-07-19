from app.domains.coin.infrastructure.orm.coin_orm import (
    CoinLotORM,
    CoinTransactionORM,
    CoinWalletORM,
)


def test_orm_tables_defined() -> None:
    assert CoinWalletORM.__tablename__ == "coin_wallets"
    assert CoinLotORM.__tablename__ == "coin_lots"
    assert CoinTransactionORM.__tablename__ == "coin_transactions"
    cols = {c.name for c in CoinLotORM.__table__.columns}
    assert {"coin_type", "remaining_amount", "expires_at", "ref", "status"} <= cols
    uniques = [
        c
        for c in CoinLotORM.__table__.constraints
        if c.__class__.__name__ == "UniqueConstraint"
    ]
    assert any(
        {"source_reason", "ref"} <= {col.name for col in u.columns} for u in uniques
    )
