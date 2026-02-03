from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.deps_auth import get_current_user
from app.models.membership import Membership
from app.models.user import User


def get_current_org_id(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> int:
    m = (
        db.query(Membership)
        .filter(Membership.user_id == user.id)
        .order_by(Membership.id.asc())
        .first()
    )
    if not m:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="sem_organizacao")
    return m.organization_id
