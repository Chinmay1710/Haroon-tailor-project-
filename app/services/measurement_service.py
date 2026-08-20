from __future__ import annotations
"""Measurement service — measurement profile management."""

from app.database.engine import get_session
from app.repositories.measurement_repo import MeasurementRepository
from app.models.measurement import MeasurementProfile
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MeasurementService:

    def create_profile(self, customer_id: int, template_type: str, name: str,
                       unit: str = "inches", notes: str = "",
                       values: dict[str, str] = None) -> MeasurementProfile:
        session = get_session()
        try:
            repo = MeasurementRepository(session)
            profile = repo.create_profile(
                customer_id=customer_id,
                template_type=template_type,
                name=name,
                unit=unit,
                notes=notes,
            )
            if values:
                for order, (field_name, field_value) in enumerate(values.items()):
                    repo.add_value(profile.id, field_name, field_value, order)
            session.commit()
            logger.info(f"Measurement profile created: {name} (ID: {profile.id})")
            return profile
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create measurement profile: {e}")
            raise
        finally:
            session.close()

    def update_profile(self, profile_id: int, name: str = None,
                       unit: str = None, notes: str = None,
                       values: dict[str, str] = None) -> MeasurementProfile | None:
        session = get_session()
        try:
            repo = MeasurementRepository(session)
            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if unit is not None:
                kwargs["unit"] = unit
            if notes is not None:
                kwargs["notes"] = notes
            if kwargs:
                repo.update_profile(profile_id, **kwargs)
            if values is not None:
                repo.update_values(profile_id, values)
            session.commit()
            return repo.get_profile_by_id(profile_id)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update measurement profile: {e}")
            raise
        finally:
            session.close()

    def delete_profile(self, profile_id: int) -> bool:
        session = get_session()
        try:
            repo = MeasurementRepository(session)
            result = repo.delete_profile(profile_id)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete measurement profile: {e}")
            raise
        finally:
            session.close()

    def duplicate_profile(self, profile_id: int, new_name: str = "") -> MeasurementProfile | None:
        session = get_session()
        try:
            repo = MeasurementRepository(session)
            new_profile = repo.duplicate_profile(profile_id, new_name)
            session.commit()
            return new_profile
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to duplicate measurement profile: {e}")
            raise
        finally:
            session.close()

    def get_profile(self, profile_id: int) -> MeasurementProfile | None:
        session = get_session()
        try:
            return MeasurementRepository(session).get_profile_by_id(profile_id)
        finally:
            session.close()

    def get_profiles_for_customer(self, customer_id: int) -> list[MeasurementProfile]:
        session = get_session()
        try:
            return MeasurementRepository(session).get_profiles_by_customer(customer_id)
        finally:
            session.close()

    def get_all_profiles(self) -> list[MeasurementProfile]:
        session = get_session()
        try:
            return MeasurementRepository(session).get_all_profiles()
        finally:
            session.close()
