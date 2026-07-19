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


def test_coin_tx_unique_is_account_scoped() -> None:
    # 멱등 pre-check가 (account_id, type, ref)로 필터하므로 DB 제약도 계정 스코프여야
    # 한다. 전역 UNIQUE(type, ref)면 서로 다른 account가 같은 SPEND ref를 쓸 때
    # pre-check를 통과한 뒤 IntegrityError(500)가 난다.
    uniques = [
        c
        for c in CoinTransactionORM.__table__.constraints
        if c.__class__.__name__ == "UniqueConstraint"
    ]
    assert any(
        {col.name for col in u.columns} == {"account_id", "type", "ref"}
        for u in uniques
    )
    assert not any(
        {col.name for col in u.columns} == {"type", "ref"} for u in uniques
    )


def test_account_id_is_integer_to_match_accounts_id_fk() -> None:
    # accounts.id is Integer (SQLAlchemy default int mapping); MySQL InnoDB
    # requires FK column types to match exactly (errno 150 / Error 1215).
    assert type(CoinWalletORM.__table__.c.account_id.type).__name__ == "Integer"
    assert type(CoinLotORM.__table__.c.account_id.type).__name__ == "Integer"
    assert type(CoinTransactionORM.__table__.c.account_id.type).__name__ == "Integer"
