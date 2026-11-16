# Notas de la reunión con las directoras

| | |
|---|---|
| Fecha | 16 de noviembre de 2026 |
| Asistentes | Kiara Kristin Rodríguez Uribe · Carme Martín Escofet · Maria Hitz Martinez |
| Reunión anterior | [09-11-2026](../09-11-2026/09-11-2026_Notas_reunion.md) |
| Milestone | [Week 3](https://github.com/Ochimbo/TFG_Project/milestone/3) (fecha límite: 22-11-2026) |

---

## 1. Trabajo presentado (Week 2)

Se presentaron las tareas de la milestone [Week 2](https://github.com/Ochimbo/TFG_Project/milestone/2):

| Issue | Trabajo |
|---|---|
| [#9](https://github.com/Ochimbo/TFG_Project/issues/9) Restricciones en OCL | Restricciones de integridad RI1–RI7 del modelo conceptual, con las principales (RI2, RI3 y RI5) escritas en OCL (apartado 7.2.1). |
| [#10](https://github.com/Ochimbo/TFG_Project/issues/10) Fichas Volere | Una ficha para cada requisito no funcional (RNF01–RNF11) en el apartado 7.4. |
| [#11](https://github.com/Ochimbo/TFG_Project/issues/11) Modelo de la base de datos | Diseño lógico del modelo dimensional, diagrama en estrella y diccionario de datos (apartado 8.1). |
| [#12](https://github.com/Ochimbo/TFG_Project/issues/12) Títulos de los capítulos 7 y 8 | Títulos revisados para que cada concepto tenga un solo nombre. |
| [#13](https://github.com/Ochimbo/TFG_Project/issues/13) Resto del diseño | Capítulo 8 completo: ETL, lógica analítica, interfaz y organización del repositorio. |

## 2. Respuestas a las preguntas de la issue [#15](https://github.com/Ochimbo/TFG_Project/issues/15)

| Pregunta | Respuesta |
|---|---|
| Resumen | Se da por cerrado. |
| Apartado 2.1.1 (el CMI en el ámbito educativo) | Carme también está de acuerdo con el cambio. Queda cerrado. |
| Apartado 2.1.2 (soluciones existentes) | No se trató. Queda pendiente para la próxima reunión. |
| Requisitos funcionales (3.4.2) | Se quedan donde están y se dan por cerrados. |
| Requisitos no funcionales (3.4.3) | Ver el apartado 3 de estas notas. |
| Sostenibilidad y gestión económica | Se quedan en el cuerpo de la memoria. |
| Restricciones en OCL (7.2.1) | Se quedan en el capítulo 7. |

## 3. Cambios en la estructura de la memoria

### Arquitectura general ([#14](https://github.com/Ochimbo/TFG_Project/issues/14))

- [ ] Mover el apartado 7.3 (arquitectura general) al capítulo 8 de diseño.

### Requisitos no funcionales

- [ ] Mover las fichas Volere de los requisitos no funcionales del apartado 7.4 al 3.4.3. La tabla resumen del 3.4.3 se mantiene y las fichas van a continuación.
- [ ] Los requisitos funcionales se mantienen donde están.

### Nuevos capítulos de implementación y de validación

- [ ] Después del capítulo 8 de diseño, añadir dos capítulos nuevos: **9. Implementación** y **10. Validación y pruebas**. El capítulo de sostenibilidad pasa a continuación de ellos.
- [ ] Mover el apartado 8.5 (organización del repositorio) al capítulo 9 de implementación.
- [ ] Código: en el texto solo se incluyen fragmentos cortos, los necesarios para explicar cada parte, y no los ficheros completos. Se añade un anexo con una selección de fragmentos más largos.

## 4. Cuestiones abiertas

- **Apartado 2.1.2:** si debe quedarse solo con el análisis de las tres formas de consulta actuales y remitir al 1.3 para el resto, ya que en parte repite lo que se explica ahí.

## 5. Orden de trabajo para la Week 3

1. Mover el 7.3 al diseño y las fichas Volere al 3.4.3, porque cambian la numeración que usarán los capítulos nuevos.
2. Crear la estructura de los capítulos 9 y 10 y mover el 8.5 al capítulo 9.
3. Redactar el capítulo 9 de implementación.
4. Redactar el capítulo 10 de validación y pruebas.
5. Preparar el anexo de código.
