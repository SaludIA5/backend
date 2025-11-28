from datetime import datetime
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.databases.postgresql.models.episode import Episode
from app.databases.postgresql.models.user import User
from app.databases.postgresql.models.user_episodes_validations import (
    UserEpisodeValidation,
)
from app.schemas.metric import (
    EpisodeMetrics,
    MetricsSummary,
    RecommendationMetrics,
    ValidationMetrics,
)


class MetricRepository:
    """Repositorio para cálculos de métricas de recomendaciones de IA"""

    @staticmethod
    async def get_recommendation_metrics(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> RecommendationMetrics:
        """Calcula métricas de recomendaciones de IA"""

        # Query base para episodios con recomendaciones de IA
        query = select(Episode).where(Episode.recomendacion_modelo.isnot(None))

        if start_date:
            query = query.where(Episode.created_at >= start_date)
        if end_date:
            query = query.where(Episode.created_at <= end_date)

        episodes = await db.execute(query)
        episodes = episodes.scalars().all()

        if not episodes:
            return RecommendationMetrics(
                total_recommendations=0,
                accepted_recommendations=0,
                rejected_recommendations=0,
                accepted_concordant=0,
                accepted_ia_pertinent_doctor_pertinent=0,
                accepted_ia_no_pertinent_doctor_no_pertinent=0,
                accepted_discordant=0,
                accepted_ia_pertinent_doctor_no_pertinent=0,
                accepted_ia_no_pertinent_doctor_pertinent=0,
                rejected_concordant=0,
                rejected_ia_pertinent_doctor_pertinent=0,
                rejected_ia_no_pertinent_doctor_no_pertinent=0,
                rejected_discordant=0,
                rejected_ia_pertinent_doctor_no_pertinent=0,
                rejected_ia_no_pertinent_doctor_pertinent=0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                accuracy=0.0,
                concordance_rate=0.0,
                acceptance_rate=0.0,
            )

        total_recommendations = len(episodes)

        # Contadores para métricas
        accepted_recommendations = 0
        rejected_recommendations = 0

        # Contadores para concordancia en aceptadas
        accepted_concordant = 0
        accepted_ia_pertinent_doctor_pertinent = 0
        accepted_ia_no_pertinent_doctor_no_pertinent = 0

        # Contadores para discordancia en aceptadas
        accepted_discordant = 0
        accepted_ia_pertinent_doctor_no_pertinent = 0
        accepted_ia_no_pertinent_doctor_pertinent = 0

        # Contadores para concordancia en rechazadas
        rejected_concordant = 0
        rejected_ia_pertinent_doctor_pertinent = 0
        rejected_ia_no_pertinent_doctor_no_pertinent = 0

        # Contadores para discordancia en rechazadas
        rejected_discordant = 0
        rejected_ia_pertinent_doctor_no_pertinent = 0
        rejected_ia_no_pertinent_doctor_pertinent = 0

        # Contadores para métricas de precisión
        true_positives = 0  # IA dice PERTINENTE y doctor dice PERTINENTE
        false_positives = 0  # IA dice PERTINENTE y doctor dice NO PERTINENTE
        true_negatives = 0  # IA dice NO PERTINENTE y doctor dice NO PERTINENTE
        false_negatives = 0  # IA dice NO PERTINENTE y doctor dice PERTINENTE

        for episode in episodes:
            ai_rec = episode.recomendacion_modelo
            doctor_val = episode.validacion

            # Solo procesar si hay validación del doctor
            if not doctor_val:
                continue

            # Determinar si fue aceptada o rechazada
            # Asumimos que si hay validación, fue "aceptada" por el médico
            # La lógica puede ajustarse según el negocio
            is_accepted = True  # Por ahora, asumimos que toda validación es aceptación

            if is_accepted:
                accepted_recommendations += 1

                # Verificar concordancia
                if ai_rec == doctor_val:
                    accepted_concordant += 1
                    if ai_rec == "PERTINENTE":
                        accepted_ia_pertinent_doctor_pertinent += 1
                        true_positives += 1
                    else:
                        accepted_ia_no_pertinent_doctor_no_pertinent += 1
                        true_negatives += 1
                else:
                    accepted_discordant += 1
                    if ai_rec == "PERTINENTE" and doctor_val == "NO PERTINENTE":
                        accepted_ia_pertinent_doctor_no_pertinent += 1
                        false_positives += 1
                    elif ai_rec == "NO PERTINENTE" and doctor_val == "PERTINENTE":
                        accepted_ia_no_pertinent_doctor_pertinent += 1
                        false_negatives += 1
            else:
                rejected_recommendations += 1

                # Verificar concordancia en rechazadas
                if ai_rec == doctor_val:
                    rejected_concordant += 1
                    if ai_rec == "PERTINENTE":
                        rejected_ia_pertinent_doctor_pertinent += 1
                    else:
                        rejected_ia_no_pertinent_doctor_no_pertinent += 1
                else:
                    rejected_discordant += 1
                    if ai_rec == "PERTINENTE" and doctor_val == "NO PERTINENTE":
                        rejected_ia_pertinent_doctor_no_pertinent += 1
                    elif ai_rec == "NO PERTINENTE" and doctor_val == "PERTINENTE":
                        rejected_ia_no_pertinent_doctor_pertinent += 1

        # Calcular métricas de precisión
        total_with_validation = accepted_recommendations + rejected_recommendations

        if total_with_validation > 0:
            precision = (
                true_positives / (true_positives + false_positives)
                if (true_positives + false_positives) > 0
                else 0.0
            )
            recall = (
                true_positives / (true_positives + false_negatives)
                if (true_positives + false_negatives) > 0
                else 0.0
            )
            f1_score = (
                2 * (precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )
            accuracy = (true_positives + true_negatives) / total_with_validation
            concordance_rate = (
                accepted_concordant + rejected_concordant
            ) / total_with_validation
            acceptance_rate = accepted_recommendations / total_with_validation
        else:
            precision = recall = f1_score = accuracy = concordance_rate = (
                acceptance_rate
            ) = 0.0

        return RecommendationMetrics(
            total_recommendations=total_recommendations,
            accepted_recommendations=accepted_recommendations,
            rejected_recommendations=rejected_recommendations,
            accepted_concordant=accepted_concordant,
            accepted_ia_pertinent_doctor_pertinent=accepted_ia_pertinent_doctor_pertinent,
            accepted_ia_no_pertinent_doctor_no_pertinent=accepted_ia_no_pertinent_doctor_no_pertinent,
            accepted_discordant=accepted_discordant,
            accepted_ia_pertinent_doctor_no_pertinent=accepted_ia_pertinent_doctor_no_pertinent,
            accepted_ia_no_pertinent_doctor_pertinent=accepted_ia_no_pertinent_doctor_pertinent,
            rejected_concordant=rejected_concordant,
            rejected_ia_pertinent_doctor_pertinent=rejected_ia_pertinent_doctor_pertinent,
            rejected_ia_no_pertinent_doctor_no_pertinent=rejected_ia_no_pertinent_doctor_no_pertinent,
            rejected_discordant=rejected_discordant,
            rejected_ia_pertinent_doctor_no_pertinent=rejected_ia_pertinent_doctor_no_pertinent,
            rejected_ia_no_pertinent_doctor_pertinent=rejected_ia_no_pertinent_doctor_pertinent,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            accuracy=accuracy,
            concordance_rate=concordance_rate,
            acceptance_rate=acceptance_rate,
        )

    @staticmethod
    async def get_validation_metrics_by_doctor(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[ValidationMetrics]:
        """Obtiene métricas de validaciones por médico"""

        # Query para obtener validaciones con información del médico
        query = (
            select(
                User.id,
                User.name,
                func.count(Episode.id).label("total_validations"),
                func.sum(
                    case((Episode.validacion == "PERTINENTE", 1), else_=0)
                ).label(
                    "accepted_validations"
                ),
                func.sum(
                    case((Episode.validacion == "NO PERTINENTE", 1), else_=0)
                ).label(
                    "rejected_validations"
                ),
                func.sum(
                    case(
                        (Episode.recomendacion_modelo == Episode.validacion, 1),
                        else_=0,
                    )
                ).label("concordant_validations"),
                func.sum(
                    case(
                        (Episode.recomendacion_modelo != Episode.validacion, 1),
                        else_=0,
                    )
                ).label("discordant_validations"),
            )
            .select_from(User)
            .join(
                UserEpisodeValidation,
                User.id == UserEpisodeValidation.user_id,
            )
            .join(
                Episode,
                UserEpisodeValidation.episode_id == Episode.id,
            )
            .where(Episode.recomendacion_modelo.isnot(None))
            .group_by(User.id, User.name)
        )

        if start_date:
            query = query.where(Episode.created_at >= start_date)
        if end_date:
            query = query.where(Episode.created_at <= end_date)

        result = await db.execute(query)
        rows = result.all()

        validation_metrics = []
        for row in rows:
            total_validations = row.total_validations or 0
            accepted_validations = row.accepted_validations or 0
            rejected_validations = row.rejected_validations or 0
            concordant_validations = row.concordant_validations or 0
            discordant_validations = row.discordant_validations or 0

            concordance_rate = (
                concordant_validations / total_validations
                if total_validations > 0
                else 0.0
            )
            acceptance_rate = (
                accepted_validations / total_validations
                if total_validations > 0
                else 0.0
            )

            validation_metrics.append(
                ValidationMetrics(
                    doctor_id=row.id,
                    doctor_name=row.name,
                    total_validations=total_validations,
                    accepted_validations=accepted_validations,
                    rejected_validations=rejected_validations,
                    concordant_validations=concordant_validations,
                    discordant_validations=discordant_validations,
                    concordance_rate=concordance_rate,
                    acceptance_rate=acceptance_rate,
                )
            )

        return validation_metrics

    @staticmethod
    async def get_episode_metrics(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EpisodeMetrics]:
        """Obtiene métricas detalladas por episodio"""

        query = (
            select(Episode)
            .options(
                selectinload(Episode.validated_by).selectinload(
                    UserEpisodeValidation.user
                )
            )
            .where(Episode.recomendacion_modelo.isnot(None))
            .limit(limit)
            .offset(offset)
        )

        if start_date:
            query = query.where(Episode.created_at >= start_date)
        if end_date:
            query = query.where(Episode.created_at <= end_date)

        result = await db.execute(query)
        episodes = result.scalars().all()

        episode_metrics = []
        for episode in episodes:
            is_concordant = episode.recomendacion_modelo == episode.validacion
            is_accepted = episode.validacion is not None

            validated_by_doctor = None
            if episode.validated_by and episode.validated_by.user:
                validated_by_doctor = episode.validated_by.user.name

            episode_metrics.append(
                EpisodeMetrics(
                    episode_id=episode.id,
                    numero_episodio=episode.numero_episodio,
                    patient_id=episode.patient_id,
                    ai_recommendation=episode.recomendacion_modelo,
                    doctor_validation=episode.validacion or "SIN VALIDAR",
                    chief_validation=episode.validacion_jefe_turno,
                    is_concordant=is_concordant,
                    is_accepted=is_accepted,
                    validation_date=episode.updated_at,
                    validated_by_doctor=validated_by_doctor,
                )
            )

        return episode_metrics

    @staticmethod
    async def get_metrics_summary(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> MetricsSummary:
        """Obtiene resumen completo de métricas"""

        # Obtener métricas de recomendaciones
        recommendation_metrics = await MetricRepository.get_recommendation_metrics(
            db, start_date, end_date
        )

        # Obtener métricas por médico
        validation_metrics = await MetricRepository.get_validation_metrics_by_doctor(
            db, start_date, end_date
        )

        # Contar episodios totales
        total_episodes_query = select(func.count(Episode.id))
        if start_date:
            total_episodes_query = total_episodes_query.where(
                Episode.created_at >= start_date
            )
        if end_date:
            total_episodes_query = total_episodes_query.where(
                Episode.created_at <= end_date
            )

        total_episodes_result = await db.execute(total_episodes_query)
        total_episodes = total_episodes_result.scalar() or 0

        # Contar episodios con recomendación de IA
        episodes_with_ai_query = select(func.count(Episode.id)).where(
            Episode.recomendacion_modelo.isnot(None)
        )
        if start_date:
            episodes_with_ai_query = episodes_with_ai_query.where(
                Episode.created_at >= start_date
            )
        if end_date:
            episodes_with_ai_query = episodes_with_ai_query.where(
                Episode.created_at <= end_date
            )

        episodes_with_ai_result = await db.execute(episodes_with_ai_query)
        episodes_with_ai_recommendation = episodes_with_ai_result.scalar() or 0

        # Contar episodios con validación de doctor
        episodes_with_doctor_query = select(func.count(Episode.id)).where(
            Episode.validacion.isnot(None)
        )
        if start_date:
            episodes_with_doctor_query = episodes_with_doctor_query.where(
                Episode.created_at >= start_date
            )
        if end_date:
            episodes_with_doctor_query = episodes_with_doctor_query.where(
                Episode.created_at <= end_date
            )

        episodes_with_doctor_result = await db.execute(episodes_with_doctor_query)
        episodes_with_doctor_validation = episodes_with_doctor_result.scalar() or 0

        # Contar episodios con validación de jefe de turno
        episodes_with_chief_query = select(func.count(Episode.id)).where(
            Episode.validacion_jefe_turno.isnot(None)
        )
        if start_date:
            episodes_with_chief_query = episodes_with_chief_query.where(
                Episode.created_at >= start_date
            )
        if end_date:
            episodes_with_chief_query = episodes_with_chief_query.where(
                Episode.created_at <= end_date
            )

        episodes_with_chief_result = await db.execute(episodes_with_chief_query)
        episodes_with_chief_validation = episodes_with_chief_result.scalar() or 0

        return MetricsSummary(
            recommendation_metrics=recommendation_metrics,
            validation_metrics=validation_metrics,
            total_episodes=total_episodes,
            episodes_with_ai_recommendation=episodes_with_ai_recommendation,
            episodes_with_doctor_validation=episodes_with_doctor_validation,
            episodes_with_chief_validation=episodes_with_chief_validation,
            period_start=start_date,
            period_end=end_date,
        )
