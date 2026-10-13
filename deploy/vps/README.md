# Despliegue unificado en VPS

El archivo de Compose de producción vive en la raíz del repositorio (`docker-compose.prod.yml`) para que el flujo local y el del VPS usen los mismos comandos. Este directorio conserva el script de compatibilidad `deploy_api.sh`; la configuración previa de API+Redis ya no se usa.

## Primera instalación

1. Instala Docker Engine con el plugin Docker Compose y abre los puertos TCP `80` y `443`, además de UDP `443`, en el firewall del VPS.
2. Configura un registro DNS tipo `A` para el dominio elegido hacia la IP del VPS.
3. En la raíz del repositorio, ejecuta `make prod-init` y edita `.env.production`:
   - define `DOMAIN` con el dominio público;
   - cambia `CORS_ALLOWED_ORIGINS` a `https://<DOMAIN>`;
   - genera valores largos y únicos para `POSTGRES_PASSWORD` y `ADMIN_API_KEY`.
4. Ejecuta `make prod-up`.
5. Comprueba `make prod-ps` y visita `https://<DOMAIN>/api/v1/health`.

Caddy obtiene y renueva automáticamente los certificados TLS. Durante la migración, deja que Caddy sea el único proceso que ocupe los puertos 80 y 443; detén o reconfigura cualquier Nginx/Certbot previo que los esté utilizando.

## Operación

- `make prod-logs` sigue los logs de todos los servicios.
- `make prod-etl` ejecuta una actualización manual de datos.
- `make prod-backup-db` crea un dump comprimido en `backups/`.
- `make prod-down` detiene los contenedores sin borrar los volúmenes persistentes.

No expongas PostgreSQL, Redis ni el puerto 8000 de la API al exterior. Los datos de PostgreSQL, Redis y los certificados de Caddy residen en volúmenes Docker y sobreviven recreaciones normales de contenedores.
