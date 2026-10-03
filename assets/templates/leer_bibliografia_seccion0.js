// Lee la bibliografía de la sección 0 del aula (Moodle TUP). Se pega en mcp__claude-in-chrome__javascript_tool con la página
// https://<campus>/course/view.php?id=<ID>&section=0 ya cargada (esperar 2-3 s tras navegar). SOLO LECTURA.
// - Ubica el bloque por CONTENIDO, no por posición (cambia entre materias y años):
//   1) la actividad (label) cuyo texto contiene "NECESITÁS PARA ESTUDIAR"; 2) si no, cualquiera con un encabezado "BIBLIOGRAF*";
//   3) si ninguna, devuelve los títulos de las actividades de la sección 0 para preguntarle al tutor dónde está. Nunca adivinar.
// - Devuelve las líneas bajo el encabezado "BIBLIOGRAF*" como `n|texto`. Las URL del texto se reemplazan por [URL]: el navegador
//   bloquea salidas con parámetros de consulta ("Cookie/query string data"). ENLACES=true agrega host+ruta de cada enlace; si se
//   bloquea, dejalo en false o bajá CUANTAS.
// - La salida de javascript_tool se corta cerca de los 1000 caracteres: se pide por tramos cambiando DESDE (la respuesta dice
//   cuál es el siguiente) hasta que `siguiente=null`.
(() => {
  const DESDE = 0, CUANTAS = 3, ENLACES = false;
  const acts = [...document.querySelectorAll('li.activity')];
  const limpio = t => t.replace(/\s+/g, ' ').replace(/https?:\/\/\S+/g, '[URL]').trim();
  const tieneEncabezado = a => [...a.querySelectorAll('h2,h3,h4,h5')].some(h => /BIBLIOGRAF/i.test(h.textContent));
  let a = acts.find(x => /NECESIT[ÁA]S PARA ESTUDIAR/i.test(x.textContent) && tieneEncabezado(x)) || acts.find(tieneEncabezado);
  if (!a) {
    return 'NO ENCONTRADA. Actividades de la sección 0 (preguntale al tutor dónde está la bibliografía):\n' +
      acts.map((x, i) => i + '|' + limpio((x.querySelector('.instancename, .activity-name-area, h3, h4') || x).textContent).slice(0, 70)).join('\n');
  }
  const lineas = [];
  let dentro = false;
  a.querySelectorAll('h2,h3,h4,h5,li').forEach(e => {
    if (e.tagName !== 'LI') { dentro = /BIBLIOGRAF/i.test(e.textContent); return; }
    if (!dentro) return;
    const enlaces = ENLACES ? '|' + [...e.querySelectorAll('a')].map(x => x.hostname + x.pathname.slice(0, 40) + (x.search ? ' (+consulta omitida)' : '')).join(' ; ') : '';
    lineas.push((lineas.length + 1) + '|' + limpio(e.textContent) + enlaces);
  });
  const fin = Math.min(DESDE + CUANTAS, lineas.length);
  return 'total=' + lineas.length + ' siguiente=' + (fin < lineas.length ? fin : null) + '\n' + lineas.slice(DESDE, fin).join('\n');
})()
