// Lee la bibliografía de la sección 0 del aula (Moodle TUP). Se pega en mcp__claude-in-chrome__javascript_tool con la página
// https://<campus>/course/view.php?id=<ID>&section=0 ya cargada (esperar 2-3 s tras navegar). Solo lectura.
// - Ubica el label por su texto ("NECESITÁS"), no por índice: la posición cambia entre materias.
// - Devuelve las líneas de "I. BIBLIOGRAFÍA" como `n|texto|enlaces`. Las URL del texto se reemplazan por [URL] porque el navegador
//   bloquea salidas con parámetros de consulta; los enlaces salen aparte como host+ruta.
// - La salida de javascript_tool se corta cerca de los 1000 caracteres: se pide por tramos cambiando DESDE (la respuesta dice
//   cuál es el siguiente) hasta que `siguiente` sea null.
(() => {
  const DESDE = 0, CUANTAS = 3;
  const acts = [...document.querySelectorAll('li.activity')];
  const i = acts.findIndex(a => /NECESIT/i.test(a.textContent));
  if (i < 0) return 'ERROR: no se encontró el label "¿Qué necesitás para estudiar?" (actividades: ' + acts.length + ')';
  const limpio = t => t.replace(/\s+/g, ' ').replace(/https?:\/\/\S+/g, '[URL]').trim();
  const lineas = [];
  let dentro = false;
  acts[i].querySelectorAll('h3,h4,li').forEach(e => {
    if (e.tagName === 'H4' || e.tagName === 'H3') { dentro = /BIBLIOGRAF/i.test(e.textContent); return; }
    if (!dentro) return;
    const enlaces = [...e.querySelectorAll('a')].map(a => a.hostname + a.pathname.slice(0, 40) + (a.search ? ' (+consulta omitida)' : ''));
    lineas.push((lineas.length + 1) + '|' + limpio(e.textContent) + '|' + enlaces.join(' ; '));
  });
  const fin = Math.min(DESDE + CUANTAS, lineas.length);
  return 'total=' + lineas.length + ' siguiente=' + (fin < lineas.length ? fin : null) + '\n' + lineas.slice(DESDE, fin).join('\n');
})()
