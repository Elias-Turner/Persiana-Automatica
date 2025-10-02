# README – Sincronización en `executor15`

Este documento describe el uso de **semáforos y monitores** en el código fuente `executor15.java`.  
Se explica para cada recurso de sincronización **qué objetivo cumple**: exclusión mutua o sincronización por condición.

---

## Semáforos

### 1. `semCiudadesImp[i]`
- **Tipo**: `Semaphore(1, true)` (fair).
- **Uso**: Exclusión mutua.
- **Recurso protegido**: **Ciudades impares** → solo un vehículo a la vez puede descargar en ellas.
- **Objetivo**: Evitar que múltiples vehículos descarguen simultáneamente en ciudades impares.

---

### 2. `semCarrilUnico` (en `Puente P1`)
- **Tipo**: `Semaphore(1, true)`.
- **Uso**: Exclusión mutua.
- **Recurso protegido**: **Puente P1 (carril único)**.
- **Objetivo**: Asegurar que un único vehículo cruce a la vez.

---

### 3. `mutex` (en `Puente P2`)
- **Tipo**: `Semaphore(1, true)`.
- **Uso**: Exclusión mutua.
- **Recurso protegido**: Variables de estado de **Puente P2**:  
  - `sentidoActual`  
  - `vehiculosEnPuente`  
  - `consecutivosActuales`
- **Objetivo**: Coordinar acceso concurrente de vehículos en sentidos opuestos y evitar inanición.

---

### 4. `limpiado` (en `Puente`)
- **Tipo**: `Semaphore(0, true)`.
- **Uso**: Sincronización por condición.
- **Condición**: Esperar a que el **puente sea reabierto tras limpieza**.
- **Objetivo**: Los vehículos bloqueados esperan hasta que el limpiador reabra el puente.

---

### 5. `semGrupo` (en `Galpon`)
- **Tipo**: `Semaphore(0, true)`.
- **Uso**: Sincronización por condición.
- **Condición**: Reunir **grupo completo de vehículos** (3 en G1, 5 en G2).
- **Objetivo**: Los vehículos esperan hasta que se forme el grupo antes de ingresar al galpón (o se liberen por terminación).

---

## Monitores (uso de `synchronized`)

### 6. `bloqCiudad[i]`
- **Tipo**: Monitor (`synchronized`).
- **Uso**: Exclusión mutua.
- **Recurso protegido**: Actualización de `totalCiudad[i]`.
- **Objetivo**: Evitar condiciones de carrera en la suma de mercancías descargadas.

---

### 7. `synchronized (this)` en `Galpon.entrarYTerminar`
- **Tipo**: Monitor (`synchronized`).
- **Uso**: Exclusión mutua + sincronización por condición.
- **Condición**: Verificar si se completó el grupo para liberar a los vehículos.
- **Objetivo**: Asegurar que un solo vehículo libere al grupo y evitar inconsistencias.

---

## Contadores atómicos

### 8. `AtomicIntegerArray totalCiudad`
- **Uso**: Operaciones atómicas de suma en mercancías depositadas por ciudad.
- **Objetivo**: Consistencia sin necesidad de locks adicionales (aunque se combina con `synchronized` para mayor seguridad).

### 9. `AtomicInteger esperando` (en `Galpon`)
- **Uso**: Contador seguro de vehículos esperando.
- **Objetivo**: Controlar cuántos vehículos esperan y decidir cuándo liberar al grupo.

### 10. `AtomicInteger esperandoDir1 / esperandoDirM1` (en `Puente P2`)
- **Uso**: Contadores seguros por sentido.
- **Objetivo**: Implementar política anti-inanición y control de turnos.

---

## Resumen

- **Exclusión mutua**:  
  - `semCiudadesImp[i]` (ciudades impares)  
  - `semCarrilUnico` (puente P1)  
  - `mutex` (puente P2)  
  - `bloqCiudad[i]` (ciudades pares)  
  - `synchronized` en galpones  

- **Sincronización por condición**:  
  - `limpiado` (espera reapertura tras limpieza)  
  - `semGrupo` (espera formación de grupo en galpones)  

---
