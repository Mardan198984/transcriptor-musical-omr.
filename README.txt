TRANSCRIPTOR MUSICAL - PAQUETE PARA SERVIDOR (v3)
=================================================

CONTENIDO
---------
- app.html: interfaz web adaptable a teléfono.
- server.py: API FastAPI; sirve la interfaz y procesa /api/transpose.
- requirements.txt: dependencias Python.
- Dockerfile: prepara el servidor y Audiveris 5.11.0 para despliegue Docker.

IMPORTANTE
----------
Este paquete prepara el despliegue, pero NO significa que el servidor ya esté
publicado ni probado en un proveedor. La primera compilación Docker descarga e
instala Audiveris y puede tardar y consumir bastante memoria/almacenamiento.

DESPLIEGUE PREVISTO
-------------------
1. Subir los cuatro archivos de la carpeta al repositorio GitHub.
2. En un proveedor compatible con Docker, crear un servicio desde ese repo.
3. Seleccionar Dockerfile como método de construcción.
4. Esperar a que termine la construcción y revisar los registros.
5. Abrir la URL HTTPS del servicio. La página principal debe mostrar la app.
6. Comprobar /api/health; debe responder JSON con ok=true y audiveris=true.

PRUEBA
------
La app envía los archivos a /api/transpose en el mismo dominio. Acepta PDF,
PNG y JPG de hasta 15 MB. La salida es MusicXML. Revisa siempre el resultado
en MuseScore porque el OMR puede confundir símbolos o notas.

LIMITACIONES
------------
- La precisión depende de la calidad y complejidad de la partitura.
- No incluye todavía reproducción de audio ni exportación directa a PDF.
- Antes de abrir el servicio al público deben añadirse autenticación, límites
de uso, limpieza/retención controlada y CORS restringido al dominio final.
- El contenedor necesita recursos suficientes para ejecutar Audiveris. Un
  plan gratuito o de pocos recursos podría no construirlo o procesar partituras.

LICENCIA DE AUDIVERIS
---------------------
Audiveris se distribuye bajo AGPL-3.0. Consulta su repositorio y licencia:
https://github.com/Audiveris/audiveris

Documentación de la CLI:
https://audiveris.github.io/audiveris/_pages/guides/advanced/cli/
