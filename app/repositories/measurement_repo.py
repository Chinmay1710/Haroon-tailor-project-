from __future__ import annotations
"""Measurement repository — database operations for measurements."""

from sqlalchemy.orm import Session

from app.models.measurement import MeasurementProfile, MeasurementValue


class MeasurementRepository:

    def __init__(self, session: Session):
        self.session = session

    def create_profile(self, customer_id: int, template_type: str, name: str,
                       unit: str = "inches", notes: str = "") -> MeasurementProfile:
        profile = MeasurementProfile(
            customer_id=customer_id,
            template_type=template_type,
            name=name,
            unit=unit,
            notes=notes,
        )
        self.session.add(profile)
        self.session.flush()
        return profile

    def add_value(self, profile_id: int, field_name: str,
                  field_value: str = "", display_order: int = 0) -> MeasurementValue:
        value = MeasurementValue(
            profile_id=profile_id,
            field_name=field_name,
            field_value=field_value,
            display_order=display_order,
        )
        self.session.add(value)
        self.session.flush()
        return value

    def get_profile_by_id(self, profile_id: int) -> MeasurementProfile | None:
        return self.session.query(MeasurementProfile).filter(
            MeasurementProfile.id == profile_id
        ).first()

    def get_profiles_by_customer(self, customer_id: int) -> list[MeasurementProfile]:
        from sqlalchemy.orm import selectinload
        return self.session.query(MeasurementProfile).options(
            selectinload(MeasurementProfile.values)
        ).filter(
            MeasurementProfile.customer_id == customer_id
        ).order_by(MeasurementProfile.created_at.desc()).all()

    def get_all_profiles(self) -> list[MeasurementProfile]:
        from sqlalchemy.orm import joinedload, selectinload
        return self.session.query(MeasurementProfile).options(
            joinedload(MeasurementProfile.customer),
            selectinload(MeasurementProfile.values)
        ).order_by(
            MeasurementProfile.created_at.desc()
        ).all()

    def update_profile(self, profile_id: int, **kwargs) -> MeasurementProfile | None:
        profile = self.get_profile_by_id(profile_id)
        if profile:
            for key, value in kwargs.items():
                if hasattr(profile, key) and key not in ("id", "created_at"):
                    setattr(profile, key, value)
            self.session.flush()
        return profile

    def update_values(self, profile_id: int, values_dict: dict[str, str]):
        """Replace all measurement values for a profile."""

        # Delete existing values
        self.session.query(MeasurementValue).filter(
            MeasurementValue.profile_id == profile_id
        ).delete()
        # Add new values
        for order, (field_name, field_value) in enumerate(values_dict.items()):
            self.add_value(profile_id, field_name, field_value, order)

    def delete_profile(self, profile_id: int) -> bool:
        profile = self.get_profile_by_id(profile_id)
        if profile:
            self.session.delete(profile)
            self.session.flush()
            return True
        return False

    def duplicate_profile(self, profile_id: int, new_name: str = "") -> MeasurementProfile | None:
        """Create a copy of an existing profile."""
        original = self.get_profile_by_id(profile_id)
        if not original:
            return None
        name = new_name or f"{original.name} (Copy)"
        new_profile = self.create_profile(
            customer_id=original.customer_id,
            template_type=original.template_type,
            name=name,
            unit=original.unit,
            notes=original.notes,
        )
        for val in original.values:
            self.add_value(new_profile.id, val.field_name, val.field_value, val.display_order)
        return new_profile
