import os
import asyncio
import logging
from typing import List, Dict, Any

# Configuración de Logging Seguro (Regla 65: No exponer info sensible)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Carga de variables
USE_MOCK = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

class GithubAnalyticsETL:
    def __init__(self):
        self.use_mock = USE_MOCK or not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_personal_access_token_here"
        
        # Enmascarar el token en los logs por seguridad (Regla 65)
        safe_token = f"{GITHUB_TOKEN[:4]}...{GITHUB_TOKEN[-4:]}" if len(GITHUB_TOKEN) > 8 else "NOT_SET"
        logger.info(f"Inicializando ETL. Token configurado: {safe_token}")
        
        if self.use_mock:
            logger.info("Modo MOCK activado: No se requiere API de GitHub.")

    async def extract_data(self) -> List[Dict[str, Any]]:
        """Extrae datos de repositorios."""
        logger.info("Iniciando fase de EXTRACCIÓN...")
        if self.use_mock:
            await asyncio.sleep(1) # Simular latencia de red
            return [
                {"id": 101, "name": "repo-uno", "stars": 150, "language": "Python"},
                {"id": 102, "name": "repo-dos", "stars": 80, "language": "TypeScript"}
            ]
        else:
            # Lógica real de requests iría aquí
            raise NotImplementedError("Live API request not implemented in this snippet.")

    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Limpia y valida los datos (Regla 13: Valida todas las entradas)."""
        logger.info("Iniciando fase de TRANSFORMACIÓN...")
        if not raw_data:
            logger.warning("No se recibieron datos para transformar.")
            return []
            
        clean_data = []
        for item in raw_data:
            # Validación estricta
            if "name" in item and "stars" in item:
                clean_data.append({
                    "repo_name": str(item["name"]).strip().lower(),
                    "star_count": int(item["stars"]),
                    "main_language": str(item.get("language", "Unknown"))
                })
        return clean_data

    async def load_data(self, transformed_data: List[Dict[str, Any]]):
        """Carga datos en base de datos con monitoreo (Regla 12)."""
        logger.info("Iniciando fase de CARGA...")
        if not transformed_data:
            logger.warning("Abortando carga: conjunto de datos vacío.")
            return

        # Simulación de transacción de base de datos
        logger.info(f"Transacción DB Iniciada (Monitoreo) - Registros a insertar: {len(transformed_data)}")
        await asyncio.sleep(0.5)
        logger.info("Transacción DB Completada exitosamente.")

    async def run_pipeline(self):
        """Orquestador principal con Sistema de Gestión de Errores (Regla 64)."""
        try:
            logger.info("--- INICIANDO PIPELINE ETL ---")
            raw_data = await self.extract_data()
            clean_data = await self.transform_data(raw_data)
            await self.load_data(clean_data)
            logger.info("--- PIPELINE ETL FINALIZADO CON ÉXITO ---")
        except Exception as e:
            # Captura global de errores sin colapsar el sistema
            logger.error(f"Error crítico en la ejecución del pipeline: {str(e)}", exc_info=True)
            # Aquí podríamos integrar alertas a Sentry (Regla 74)

if __name__ == "__main__":
    pipeline = GithubAnalyticsETL()
    asyncio.run(pipeline.run_pipeline())