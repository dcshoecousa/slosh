from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CasbinRule(Base):
    __tablename__ = "casbin_rules"
    __table_args__ = (
        UniqueConstraint(
            "ptype",
            "v0",
            "v1",
            "v2",
            "v3",
            "v4",
            "v5",
            name="uq_casbin_rules_policy",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ptype: Mapped[str] = mapped_column(String(16), nullable=False)
    v0: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    v1: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    v2: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    v3: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    v4: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    v5: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    def __str__(self) -> str:
        values = [self.ptype]
        for value in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if not value:
                break
            values.append(value)
        return ", ".join(values)

    def __repr__(self) -> str:
        return f'<CasbinRule {self.id}: "{self}">'
