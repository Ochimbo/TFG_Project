# Guía común para los agentes de la Week_2

Todos los agentes que trabajan en la milestone Week_2 leen esta guía antes de empezar y la cumplen. Su objetivo es
que el resultado parezca escrito por una sola persona.

## Proyecto

TFG de Kiara Rodríguez Uribe (FIB-UPC, Sistemas de Información): un Cuadro de Mando Integral (CMI) en Power BI con
los microdatos abiertos de la evaluación de 6.º de primaria de Cataluña (2009–2025, 1,1 millones de filas).
Tres perfiles: estratégico (E, Departamento), táctico (T, inspección) y operativo (O, dirección de centro).

Raíz del repositorio: `C:\Users\kiara\Desktop\Uni\TFG\Project\TFG_Project` (Windows; usar Git Bash para los scripts).

| Qué | Dónde |
|---|---|
| Memoria (LaTeX) | `Documentation/Docu_Final/Memoria/Latex_Memoria/main.tex` y `bibliografia.bib` |
| Tareas de la semana | `Documentation/Reuniones/09-11-2026/09-11-2026_Notas_reunion.md` |
| Estado de la implementación | `trabajo_en_curso/ESTADO.md` |
| Contrato de diseño | `trabajo_en_curso/contrato_diseno.md` |
| Informe de calidad, modelo, fichas de KPI, guía de uso | `Documentation/Docu_Final/Docu_Parcial/01..04_*.md` |
| Proyecto Power BI (GENERADO, no editar a mano) | `PowerBI/` |
| Generadores del modelo, medidas, informe y diagramas | `trabajo_en_curso/generadores/` |
| Validación independiente en Python | `validacion/` |
| Datos | `Datos.csv` en la raíz (240 MB, no versionado) |
| Decisiones de esta semana (fuente única) | `trabajo_en_curso/week2/DECISIONES.md` |

## Reglas de trabajo

1. **No hacer commits, ni push, ni cambiar de rama.** La estudiante revisa antes. No usar `gh`.
2. **No ejecutar `compilar.sh` dentro del repositorio** (otros agentes pueden estar trabajando a la vez). Para
   compilar, copiar la carpeta `Latex_Memoria` entera a una carpeta propia dentro del directorio temporal y ejecutar
   allí `./compilar.sh` con Git Bash. Tectonic está en `C:\Users\kiara\bin\tectonic.exe` y Pandoc en
   `C:\Users\kiara\AppData\Local\Pandoc` (añadirlo al PATH si no se encuentra). El aviso «Fontconfig error» es inofensivo.
   Antes de terminar, comprobar que la memoria compila sin errores con los cambios propios y mirar las páginas
   afectadas en el PDF (y que el .docx se genera).
3. **`main.tex` es compartido.** Editar solo los apartados asignados, con ediciones pequeñas y localizadas (herramienta
   Edit). Si una edición falla porque el fichero ha cambiado, volver a leer la zona y repetirla. No reformatear ni
   reordenar nada fuera de lo asignado.
4. **`PowerBI/` no se edita a mano.** Se cambia el generador o los `m_*.m` y se regenera. Después se ejecutan las
   validaciones que se puedan ejecutar en este equipo (ver `ESTADO.md` y `validacion/README.md`).
5. No inventar datos, cifras ni fuentes. Toda cifra sale del repositorio (informes, CSV de `validacion/resultados/`,
   cálculo propio sobre `Datos.csv`) y toda cita, de una fuente comprobada. Si algo no se puede verificar, decirlo.
6. Ficheros temporales: en el directorio temporal del sistema, no en el repositorio.
7. Los diagramas se generan con scripts de Python (Pillow) en `trabajo_en_curso/generadores/`, en PNG, con el mismo
   estilo que los existentes (`gen_modelo_conceptual.py` es la referencia: Lato, tinta gris oscuro, fondo blanco).
   Los generadores tienen la ruta de fuentes de Linux; en este equipo Lato está en `C:\Windows\Fonts`. Si se toca un
   generador, hacer que la ruta funcione en los dos sistemas sin cambiar el aspecto.

## Trabajo retomable (obligatorio)

La sesión puede cortarse en cualquier momento por el límite de uso. Nada puede quedar a medias sin rastro:

1. Cada agente mantiene un fichero `trabajo_en_curso/week2/PROGRESO_<nombre>.md` (por ejemplo `PROGRESO_datos.md`,
   `PROGRESO_especificacion.md`, `PROGRESO_diseno_modelo.md`). Lo crea al empezar con su lista de pasos y lo actualiza
   al terminar cada paso: `[x]` hecho, `[~]` en curso (con qué falta exactamente y en qué fichero), `[ ]` pendiente.
   Incluye también las comprobaciones ya ejecutadas con su resultado y las que faltan.
2. Trabajar en incrementos pequeños y completos: terminar y guardar un paso antes de empezar el siguiente. Guardar
   en el repositorio (no solo en el directorio temporal) todo lo que haga falta para continuar.
3. `main.tex` debe compilar en todo momento. No dejar entornos abiertos, tablas a medias ni referencias a labels
   que todavía no existen. Si un apartado no está terminado, dejarlo vacío con su comentario guía.
4. No dejar el repositorio en un estado incoherente: si se cambia un generador, regenerar su salida en el mismo paso.
5. Registrar cada decisión en `DECISIONES.md` en el momento de tomarla, no al final.
6. Quien retome el trabajo lee primero `PROGRESO_<nombre>.md` y `DECISIONES.md` y continúa desde el primer paso
   que no esté marcado como hecho, comprobando antes el estado real de los ficheros.

## Decisiones de ingeniería

Cuando haya una incongruencia o un problema (entre documentos, entre la memoria y la implementación, o en los datos),
el agente decide como lo haría un ingeniero experto en BI y calidad de datos, aplica la decisión y la registra en
`trabajo_en_curso/week2/DECISIONES.md` con este formato (añadir al final; no borrar entradas de otros):

```
## D-NN Título corto
- Problema: qué no cuadra y dónde (fichero y apartado o línea).
- Opciones: las alternativas consideradas, en una línea cada una.
- Decisión: qué se hace.
- Justificación: por qué, con la evidencia (cifras, norma, referencia).
- Cambios aplicados: ficheros tocados. Si queda algo por aplicar en la memoria, indicarlo en «Pendiente en la memoria».
```

La memoria también debe justificar las decisiones relevantes para el TFG, en el apartado que corresponda, de forma
breve. Excepción: la issue #14 (mover el 7.3 al diseño) NO se decide; el 7.3 se queda en el capítulo 7.

## Estilo de la memoria

- Castellano, impersonal o en presente («se calcula», «el sistema muestra»). Frases cortas y llanas, como las del
  capítulo 7 actual. Las directoras revisan sobre todo la redacción y penalizan el texto artificioso.
- Evitar: «El presente…», «se enmarca en», «cabe destacar», «robusto», «clave», «fundamental», contrastes del tipo
  «no es X, sino Y», tríadas forzadas, frases de cierre que resumen lo ya dicho, rayas (—) y negritas en medio de frase.
- Cada apartado empieza diciendo qué contiene y de dónde parte, con referencias cruzadas (`Sección~\ref{}`,
  `Tabla~\ref{}`). No repetir contenido de otro capítulo: referenciarlo.
- Un concepto, un nombre. Usar los nombres que fije la issue #12 (sección «Nombres» de `DECISIONES.md`).
- Tablas: `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), `tabularx`, `\small`, leyenda debajo y `\label`.
  Copiar el formato de las tablas del capítulo 7 (fichas de casos de uso, Tabla de restricciones, historias con
  `longtable`). Tablas largas: `longtable`. Figuras: `\begin{figure}[H]`, PNG en `imagenes/<capítulo>/`.
- Comillas: `\guillemotleft{}…\guillemotright{}` (no escribir « » directamente). Símbolos: `\texteuro{}`,
  `6.\textordmasculine{}`. Términos en inglés en `\textit{}`. Decimales con coma (`0{,}5` en modo matemático).
- El .docx se genera con Pandoc: evitar paquetes y entornos nuevos que Pandoc no entienda. Si hace falta código
  (OCL, DAX, M), comprobar que sale bien en el PDF y en el .docx; si se necesita adaptar `compilar.sh` o
  `docx/memoria.lua`, hacerlo con cuidado y sin romper lo existente.
- No tocar los capítulos 6 y 9 (marcados como revisados con el entorno `revisado`).

## Informe final de cada agente

Al terminar, responder con: qué se ha hecho, ficheros tocados, decisiones tomadas (identificadores D-NN),
comprobaciones realizadas con su resultado real, y lo que queda pendiente o no se ha podido verificar.
