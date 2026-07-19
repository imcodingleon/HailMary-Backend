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


def test_account_id_is_integer_to_match_accounts_id_fk() -> None:
    # accounts.id is Integer (SQLAlchemy default int mapping); MySQL InnoDB
    # requires FK column types to match exactly (errno 150 / Error 1215).
    assert type(CoinWalletORM.__table__.c.account_id.type).__name__ == "Integer"
    assert type(CoinLotORM.__table__.c.account_id.type).__name__ == "Integer"
    assert type(CoinTransactionORM.__table__.c.account_id.type).__name__ == "Integer"
